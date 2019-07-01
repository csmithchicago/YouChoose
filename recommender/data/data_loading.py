# Copyright (c) 2019, Corey Smith
# Distributed under the MIT License.
# See LICENCE file in root directory for full terms.
"""
Data loading library.


"""
import numpy as np
import torch
import pandas as pd
from torch.utils.data import Dataset, DataLoader
from typing import Optional


def product_sets(df: pd.DataFrame) -> dict:
    """
    Generate sets for each user containing products that
    they have previously purchased.

    Args:
        df: Dataframe containing user_id and product_id columns.
    Return:
        prior_dict: Dictionary of users and a set of their purchased products.
    """
    df_g = (
        df[["user_id", "product_id"]]
        .groupby(["user_id"])["product_id"]
        .agg(lambda x: {val for val in x})
    )
    df_g = df_g.reset_index()
    df_g.columns = ["user_id", "product_list"]
    prior_dict = df_g.set_index("user_id").to_dict()["product_list"]

    return prior_dict


def list_to_indexed_dict(list_: list) -> dict:
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
        dataframe: pd.DataFrame,
        product_dict: dict,
        user_dict: dict,
        dev=torch.device("cpu"),
        reweighting: Optional[dict] = None,
        num_negs: int = 0,
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
        self.w_dict = reweighting if reweighting is not None else dict()
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
