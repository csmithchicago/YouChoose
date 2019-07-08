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
from typing import Tuple, List

from .data_processing import item_sets, dataframe_split, transform_data_ids


class InteractionsDataset(Dataset):
    """
    A torch.Dataset for user-item interactions.
    """

    def __init__(
        self,
        df: pd.DataFrame,
        num_items: int,
        user_col: str = "user_id",
        item_col: str = "item_id",
        weight_col: str = "weight",
        dev=torch.device("cpu"),
        num_negs: int = 0,
    ):
        """
        A torch.utils.data.Dataset containing the user-item interactions.

        Args:
            df (pd.DataFrame): Dataframe containing user_id, item_id, and
                interaction (ratings).
            num_items (int): The number of items contained in the dataset.
            user_col (str, optional): Column name for the users.
            item_col (str, optional): Column name for the items/products.
            weight_col (str, optional): Column name for interaction metric.
            dev (torch.device, optional): Choose location to run the model.
                Defaults to torch.device("cpu").
            num_negs (int, optional): Number of negative interactions to sample
                for each positive interaction by a user. Defaults to 0.

        Raises:
            ValueError: If the number of negative samples is negative.
        """
        super(InteractionsDataset, self).__init__()

        if num_negs < 0:
            raise ValueError("The number of negative samples must be positive.")

        self.item_sets = item_sets(df, users=user_col, items=item_col)
        self.dev = dev
        self.num_negs = num_negs
        self.items = self.transform(df[item_col])
        self.users = self.transform(df[user_col])
        self.weights = self.transform(df[weight_col]).float()
        self.size = len(df)
        self.n_items = num_items

    def __len__(self):
        return self.size

    def __getitem__(self, idx):
        """
        Get and return Tensor for item, user, interaction triplet.
        """
        user = self.users[idx]
        item = self.items[idx]
        weight = self.weights[idx]

        if self.num_negs:
            users, neg_i, neg_r = self.negative_sampling(user)
            item = torch.cat((item.unsqueeze(0), neg_i.to(self.dev)))
            user = torch.cat((user.unsqueeze(0), users.to(self.dev)))
            weight = torch.cat((weight.unsqueeze(0), neg_r.to(self.dev)))

        return (user, item, weight)

    def transform(self, df_rows):
        """
        Convert pandas dataframe to a torch tensor and sent to computation device.
        """
        return torch.from_numpy(df_rows.to_numpy()).to(self.dev)

    def negative_sampling(self, user_ids):
        """
        For each user interaction randomly sample items that they
        have not previously purchased.

        Args:
            user_ids (torch.tensor): The user ids to sample negative interactions for.

        Returns:
            tuple(torch.tensor): A tuple of torch tensors for the users, items, negative
                interactions.
        """
        u_list = []
        i_list = []
        w_list = self.num_negs * [0.0]
        u_id = int(user_ids)

        neg_set = set(range(self.n_items)) - self.item_sets[u_id]
        neg_v = np.random.choice(tuple(neg_set), self.num_negs)

        for i_id in neg_v:
            u_list.append(u_id)
            i_list.append(i_id)

        return (torch.tensor(u_list), torch.tensor(i_list), torch.tensor(w_list))

    @classmethod
    def ratings_dataloader(
        cls,
        dataframe: pd.DataFrame,
        user_col: str = "user_id",
        item_col: str = "item_id",
        weight_col: str = "interaction",
        batch_size: int = 1,
        dev=torch.device("cpu"),
        num_negs: int = 0,
        shuffle_train: bool = True,
        reweight: bool = True,
        train_frac: float = 0.80,
        test_frac: float = 0.10,
        **kwargs
    ) -> Tuple[List[DataLoader], int, int]:
        """
        Split the user, item, interactions dataframe into train, validate, and
        test dataloader objects.

        Transform a dataframe into three torch.DataLoader opjects for training. Using
        DataLoaders allows for easy handling of batch sizes.

        Args:
            dataframe (pd.DataFrame): Dataframe containing the user-item interactions.
            user_col (str, optional): Column name for the users.
            item_col (str, optional): Column name for the items/products.
            weight_col (str, optional): Column name for interaction metric.
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
            **kargs (dict, optional): Additional arguments to pass to the
                torch.utils.data.DataLoading class.

        Returns:
            Tuple[Tuple[DataLoader], int, int]: A tuple containing a list of DataLoaders for the
                training, validation, and testing data, and the number of unique users
                and items.
        """
        df_transformed, user_dict, item_dict = transform_data_ids(
            dataframe,
            user_col=user_col,
            item_col=item_col,
            weight_col=weight_col,
            reweight=reweight,
        )
        split_dfs = dataframe_split(
            df_transformed, train_frac=train_frac, test_frac=test_frac
        )

        n_users, n_items = len(user_dict), len(item_dict)

        shuffle_list = [shuffle_train, False, False]
        loader_list = []

        for df, shuffle in zip(split_dfs, shuffle_list):
            data_set = cls(
                df,
                n_items,
                user_col=user_col,
                item_col=item_col,
                weight_col=weight_col,
                dev=dev,
                num_negs=num_negs,
            )
            loader_list.append(
                DataLoader(data_set, batch_size=batch_size, shuffle=shuffle, **kwargs)
            )

        return (loader_list, n_users, n_items)
