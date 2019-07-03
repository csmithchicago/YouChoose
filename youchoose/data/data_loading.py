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

from .data_processing import item_sets, dataframe_split, list_to_indexed_dict


class InteractionsDataset(Dataset):
    """
    A torch.Dataset for user-item interactions.
    """

    def __init__(
        self,
        dataframe: pd.DataFrame,
        item_dict: dict,
        user_dict: dict,
        dev=torch.device("cpu"),
        reweighting: Optional[dict] = None,
        num_negs: int = 0,
    ):
        """
        A torch Dataset containing the user-item interactions.

        Args:
            dataframe (pd.DataFrame): Dataframe containing user_id, item_id, and
                interaction (ratings).
            item_dict (dict): Dictionary mapping item ids to indices.
            user_dict (dict): Dictionary mapping user ids to indices.
            dev (torch.device, optional): Choose location to run the model.
                Defaults to torch.device("cpu").
            reweighting (Optional[dict], optional): Dictionary mapping
                interactions to new values. Defaults to None.
            num_negs (int, optional): Number of negative interactions to sample
                for each positive interaction by a user. Defaults to 0.

        Raises:
            ValueError: If the number of negative samples is negative.
        """
        super(InteractionsDataset, self).__init__()

        if num_negs < 0:
            raise ValueError("The number of negative samples must be positive.")

        self.df = dataframe
        self.item_sets = item_sets(dataframe)
        self.i_dict = item_dict
        self.u_dict = user_dict
        self.w_dict = reweighting if reweighting is not None else dict()
        self.num_items = len(item_dict)
        self.num_users = len(user_dict)
        self.dev = dev
        self.num_negs = num_negs

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        """
        Get and return Tensor for item, user, interaction triplet.
        """
        user_ids = self.df["user_id"].iloc[idx]
        item = self.transform(self.df["item_id"].iloc[idx], self.i_dict)
        user = self.transform(user_ids, self.u_dict)
        rating = self.transform(self.df["interaction"].iloc[idx], self.w_dict).float()

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
        For each user interaction randomly sample items that they
        have not previously purchased.

        Args:
            user_ids (list, int): The user ids to sample negative interactions for.

        Returns:
            tuple(torch.tensor): A tuple of torch tensors for the users, items, negative
                interactions.
        """
        if isinstance(user_ids, np.int64):
            user_ids = [user_ids]

        u_list = []
        i_list = []
        w_list = self.num_negs * len(user_ids) * [0.0]

        for u_id in user_ids:
            neg_set = set(self.i_dict.keys()) - self.item_sets[u_id]
            neg_v = np.random.choice(tuple(neg_set), self.num_negs)

            for i_id in neg_v:
                u_list.append(self.u_dict[u_id])
                i_list.append(self.i_dict[i_id])

        return (torch.tensor(u_list), torch.tensor(i_list), torch.tensor(w_list))


def ratings_dataloader(
    dataframe: pd.DataFrame,
    batch_size: int = 1,
    dev=torch.device("cpu"),
    num_negs: int = 0,
    shuffle_train: bool = True,
    reweight: bool = True,
    train_frac: float = 0.80,
    test_frac: float = 0.10,
):
    """
    Split the user, item, interactions dataframe into train, validate, and
    test dataloader objects.

    Transform a dataframe into three torch.DataLoader opjects for training. Using
    DataLoaders allows for easy handling of batch sizes.

    Args:
        dataframe (pd.DataFrame): Dataframe containing the user-item interactions.
        batch_size (int, optional): Batch size to use during training, validation,
            and testing. Defaults to 1.
        dev (torch.device, optional): Location for the torch calculations.
            Defaults to torch.device("cpu").
        num_negs (int, optional): The number of negative samples drawn for each positive
            interaction. Defaults to 0.
        shuffle_train (bool, optional): During training, the training data can be
            shuffled for each epoch. Defaults to True.
        reweight (bool, optional): Transform the interactions to binary yes or no
            interactions. Defaults to True.
        train_frac (float, optional): The proportion of data that should be used for
            training the recommender. Defaults to 0.80.
        test_frac (float, optional): The proportion of data to test and evaluate the
            recommenders performance on. Defaults to 0.10.

    Raises:
        ValueError: The testing and training fractions must both be less than 1
            and their sum to be less than 1.

    Returns:
        ([DataLoaders], int, int): A tuple containing a list of DataLoaders for the
            training, validation, and testing data, and the number of unique users
            and items.
    """
    if not (train_frac <= 1 and test_frac <= 1 and (train_frac + test_frac) <= 1):
        raise ValueError(
            "The testing and training fractions must both be less "
            "than 1 and sum to be less than 1."
        )
    # for now, these are what the column names need to be
    item_col = "item_id"
    user_col = "user_id"
    interaction_col = "interaction"

    split_dfs = dataframe_split(dataframe, train_frac=train_frac, test_frac=test_frac)

    id_item_dict = list_to_indexed_dict(dataframe[item_col])
    id_user_dict = list_to_indexed_dict(dataframe[user_col])

    item_dict = {key: value for value, key in id_item_dict.items()}
    user_dict = {key: value for value, key in id_user_dict.items()}

    if reweight:
        weight_dict = {val: 1.0 for val in dataframe[interaction_col].unique()}
    else:
        weight_dict = {val: val for val in dataframe[interaction_col].unique()}

    n_users, n_items = len(user_dict), len(item_dict)

    shuffle_list = [shuffle_train, False, False]
    loader_list = []

    for df, shuffle in zip(split_dfs, shuffle_list):
        loader_list.append(
            DataLoader(
                InteractionsDataset(
                    df,
                    item_dict,
                    user_dict,
                    reweighting=weight_dict,
                    dev=dev,
                    num_negs=num_negs,
                ),
                batch_size=batch_size,
                shuffle=shuffle,
            )
        )
    return (loader_list, n_users, n_items)
