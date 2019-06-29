"""
Matrix factorization library.


Copyright (c) 2019, Corey Smith
Distributed under the MIT License.
See LICENCE file for full terms.
"""
import numpy as np
import torch
import pandas as pd
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader


def product_sets(df):
    """
    Generate sets for each user containing products that
    they have previously purchased.

    Args:
        df (pandas DataFrame): Dataframe containing user_id and
            product_id columns.
    Return:
        dictionary with user_id as keys and the product sets as values.
    """
    df_g = (
        df[["user_id", "product_id"]]
        .groupby(["user_id"])["product_id"]
        .agg(lambda x: set([val for val in x]))
    )
    df_g = df_g.reset_index()
    df_g.columns = ["user_id", "product_list"]

    return df_g.set_index("user_id").to_dict()["product_list"]


def list_to_indexed_dict(list_):
    """
    Assign id to distinct list elements and return
    the id -> element mapping as a dictionary.
    """
    return dict(enumerate(sorted(set(list_))))


class RatingsDataset(Dataset):
    """
    User, product, ratings dataset.
    """

    def __init__(
        self,
        dataframe,
        product_dict,
        user_dict,
        dev=torch.device("cpu"),
        reweighting=dict(),
        num_negs=0,
    ):
        """
        Args:
            dataframe (pandas.DataFrame): Dataframe containing ratings.
            product_dict (dict): Dictionary mapping product ids to indices.
            user_dict (dict): Dictionary mapping user ids to indices.
            reweighting (dict, optional): Dictionary mapping ratings to new values.
            dev (torch device): Hardware that the model should run on.
        """
        super(RatingsDataset, self).__init__()

        if num_negs < 0:
            raise ValueError("The number of negative samples must be positive.")

        self.df = dataframe
        self.prod_sets = product_sets(dataframe)
        self.p_dict = product_dict
        self.u_dict = user_dict
        self.w_dict = reweighting
        self.num_prods = len(product_dict)
        self.num_users = len(user_dict)
        self.dev = dev
        self.num_negs = num_negs

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        """
        Get and return Tensor for item, user, ratings triplet
        """
        user_ids = self.df["user_id"].iloc[idx]
        item = self.transform(self.df["product_id"].iloc[idx], self.p_dict)
        user = self.transform(user_ids, self.u_dict)
        rating = self.transform(self.df["rating"].iloc[idx], self.w_dict).float()

        if self.num_negs:
            users, neg_i, neg_r = self.negative_sampling(user_ids)

            item = torch.cat((item, neg_i.to(self.dev)))
            user = torch.cat((user, users.to(self.dev)))
            rating = torch.cat((rating, neg_r.to(self.dev)))

        return (user, item, rating)

    def transform(self, df_rows, mapping):
        """
        Replace dataframe with index values and convert to torch.Tensor
        """
        transformed = pd.Series(df_rows).replace(mapping).to_numpy()

        return torch.from_numpy(transformed).to(self.dev)

    def negative_sampling(self, user_ids):
        """
        For each user interaction randomly sample products that they
        have not previously purchased.
        """
        if isinstance(user_ids, np.int64):
            user_ids = [user_ids]

        u_list = []
        p_list = []
        r_list = self.num_negs * len(user_ids) * [0.0]

        for u_id in user_ids:
            neg_set = set(self.p_dict.keys()) - self.prod_sets[u_id]
            neg_v = np.random.choice(tuple(neg_set), self.num_negs)

            for p_id in neg_v:
                u_list.append(self.u_dict[u_id])
                p_list.append(self.p_dict[p_id])

        return (torch.tensor(u_list), torch.tensor(p_list), torch.tensor(r_list))


def dataframe_split(df, train_frac=0.80, test_frac=0.10):
    """
    Split dataframe into training, testing, and validation sets.
    """
    train_df = df.sample(frac=train_frac, random_state=23)
    test_df = df.drop(train_df.index).sample(int(test_frac * len(df)), random_state=23)
    # All samples not in test or train sets are used for validation
    val_df = df.drop(pd.concat([train_df, test_df], axis=0).index)

    return train_df, val_df, test_df


class MatrixFactorization(torch.nn.Module):
    """Matrix factorization using pytorch."""

    def __init__(
        self,
        n_users,
        n_products,
        n_factors=20,
        optimizer=torch.optim.SGD,
        lr=0.001,
        l2=0,
        momentum=0,
        loss_fn=nn.BCEWithLogitsLoss,
        activation=nn.Sigmoid,
    ):
        """
        Initalize the user and product embedding vectors in latent space.

        Args:
            n_users (int): Number of users with prior purchases.
            n_products (int): Total number of products purchased.
            n_factors (integer, optional): Dimension of the latent embedding space.
        """
        super(MatrixFactorization, self).__init__()

        self.l2 = l2
        self.lr = lr
        self.momentum = momentum
        self.user_factors = nn.Embedding(n_users, n_factors)
        self.product_factors = nn.Embedding(n_products, n_factors)
        self.user_bias = nn.Embedding(n_users, 1)
        self.product_bias = nn.Embedding(n_products, 1)

        self.activation = activation()
        self.loss_fn = loss_fn()
        self.optimizer = optimizer(
            self.parameters(), lr=self.lr, weight_decay=self.l2, momentum=self.momentum
        )

    def forward(self, user, item):
        """
        Matrix multiplication between user and product
        embedding vectors.
        """
        mat_mult = (self.user_bias(user) + self.product_bias(item)).squeeze(2)
        mat_mult += ((self.user_factors(user)) * (self.product_factors(item))).sum(2)

        return mat_mult

    def _prob_to_class(self, forward):
        """
        Convert the probabilities from the final activation into a
        binary classification.
        """
        predict_pos = self.activation(forward)
        predict_neg = 1 - predict_pos

        return torch.stack((predict_neg, predict_pos)).argmax(0).float()

    def prediction(self, user, item):
        """
        Use product and user embedding vectors to calculate
        a probability for positive interaction.
        """
        return self._prob_to_class(self(user, item))

    def loss(self, forward, rating):
        """Calculate the loss of the predicted ratings."""
        return self.loss_fn(forward, rating.float())

    def compute_accuracy(self, data_loader):
        """
        Compute the accuracy of our predictions against the true ratings.
        """
        correct = 0
        total = 0

        self.eval()
        with torch.no_grad():
            for user, item, true_rating in data_loader:
                predicted = self.prediction(user, item)
                total += predicted.numel()
                correct += (predicted == true_rating).sum().item()

        return total, correct

    def train_model(self, data_loader):
        """
        Train the model on the data generated by the dataloader and compute
        the training loss and training accuracy.
        """
        train_loss = 0
        correct = 0
        total = 0
        self.train()

        for user, item, rating in data_loader:
            self.optimizer.zero_grad()

            forward = self(user, item)
            predicted = self._prob_to_class(forward)
            loss = self.loss(forward, rating)

            train_loss += loss.item()
            total += predicted.numel()
            correct += (predicted == rating).sum().item()

            loss.backward()
            self.optimizer.step()

        return train_loss, f"{(100 * correct / total):.2f}"

    def evaluate(self, dataloader):
        """
        Calculate the loss and accuracy of the model on the validation
        or test data set.
        """
        val_loss = 0
        correct = 0
        total = 0

        self.eval()
        with torch.no_grad():
            for user, item, rating in dataloader:
                forward = self(user, item)
                predicted = self._prob_to_class(forward)

                val_loss += self.loss(forward, rating).item()
                total += predicted.numel()
                correct += (predicted == rating).sum().item()

        return val_loss, f"{(100 * correct / total):.2f}"


def ratings_dataloader(
    dataframe, batch_size=1, dev=torch.device("cpu"), num_negs=0, shuffle_train=True
):
    """
    Split the user, item, rating/weight dataframe into train, validate, and
    test dataloader objects.
    """
    split_dfs = dataframe_split(dataframe)

    id_prod_dict = list_to_indexed_dict(dataframe.product_id)
    id_user_dict = list_to_indexed_dict(dataframe.user_id)

    prod_dict = {key: value for value, key in id_prod_dict.items()}
    user_dict = {key: value for value, key in id_user_dict.items()}
    weight_dict = {val: 1.0 for val in dataframe.weight.unique()}

    n_users, n_products = len(user_dict), len(prod_dict)

    shuffle_list = [shuffle_train, False, False]
    loader_list = []

    for df, shuffle in zip(split_dfs, shuffle_list):
        loader_list.append(
            DataLoader(
                RatingsDataset(
                    df,
                    prod_dict,
                    user_dict,
                    reweighting=weight_dict,
                    dev=dev,
                    num_negs=num_negs,
                ),
                batch_size=batch_size,
                shuffle=shuffle,
            )
        )
    return loader_list, n_users, n_products
