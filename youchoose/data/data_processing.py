# Copyright (c) 2019, Corey Smith
# Distributed under the MIT License.
# See LICENCE file in root directory for full terms.
"""
Data processing library.
"""
import pandas as pd
from typing import Tuple


def dataframe_split(
    df: pd.DataFrame, train_frac: float = 0.80, test_frac: float = 0.10
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Split dataframe into training, testing, and validation sets.

    Args:
        df (pd.DataFrame): A pandas dataframe with feature columns and examples as rows.
        train_frac (float, optional): Fraction of the data to use for training. Defaults
            to 0.80.
        test_frac (float, optional): Fraction of the data to use for testing. Defaults
            to 0.10.
    Raises:
        ValueError: The testing and training fractions must both be less than 1
            and their sum to be less than 1.
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]: A tuple of the training,
            validation, and testing dataframes.
    """
    if not (train_frac <= 1 and test_frac <= 1 and (train_frac + test_frac) <= 1):
        raise ValueError(
            "The testing and training fractions must both be less "
            "than 1 and sum to be less than 1."
        )
    train_df = df.sample(frac=train_frac, random_state=23)
    test_df = df.drop(train_df.index).sample(int(test_frac * len(df)), random_state=23)
    val_df = df.drop(pd.concat([train_df, test_df], axis=0).index)

    return train_df, val_df, test_df


def item_sets(df: pd.DataFrame, users: str = "user_id", items: str = "item_id") -> dict:
    """
    Generate sets for each user containing items that they have previously interacted
    with.

    Args:
        df (pd.DataFrame): Dataframe containing user_id and item_id columns.
        users (str, optional): [description]. Defaults to "user_id".
        items (str, optional): [description]. Defaults to "item_id".

    Returns:
        dict: Dictionary of users and a set of items that they have previously
            interacted with.
    """
    df_g = df[[users, items]].groupby([users])[items].agg(lambda x: {val for val in x})
    df_g = df_g.reset_index()
    df_g.columns = [users, "item_list"]
    prior_dict = df_g.set_index(users).to_dict()["item_list"]

    return prior_dict


def list_to_indexed_dict(list_: list) -> dict:
    """
    Map a list of objects to a sorted dict of indexes.

    Assign indexs to distinct objects in a list and return a dictionary with
    keys in range(num unique objects) maping to the object.

    Args:
        list_ (list): A list of objects to index.

    Returns:
        dict: Sorted dictionary indexing unique objects in input list.
    """
    return dict(enumerate(sorted(set(list_))))


def transform_data_ids(
    df: pd.DataFrame,
    user_col: str = "user_id",
    item_col: str = "item_id",
    weight_col: str = "interaction",
    reweight: bool = True,
) -> Tuple[pd.DataFrame, dict, dict]:
    """
    Transform the item and user IDs into the indicies needed during embedding.

    Args:
        df (pd.DataFrame): Dataframe containing user_id and item_id columns.
        user_col (str, optional): Column name for the users. Defaults to "user_id".
        item_col (str, optional): Column name for the items/products. Defaults to
            "item_id".
        weight_col (str, optional): Column name for interaction metric. Defaults to
            "interaction".
        reweight (bool, optional): Transform the interactions to binary yes or no
            interactions. Defaults to True.
    Return:
        Tuple[pd.DataFrame, dict, dict]: The transformed dataframe along with the
            lookup dicts used to translate between ID and index.
    """
    id_item_dict = list_to_indexed_dict(df[item_col])
    id_user_dict = list_to_indexed_dict(df[user_col])

    item_dict = {key: value for value, key in id_item_dict.items()}
    user_dict = {key: value for value, key in id_user_dict.items()}

    if reweight:
        weight_dict = {val: 1.0 for val in df[weight_col].unique()}
    else:
        weight_dict = {val: val for val in df[weight_col].unique()}

    df[user_col] = df[user_col].map(user_dict)
    df[item_col] = df[item_col].map(item_dict)
    df[weight_col] = df[weight_col].map(weight_dict)

    return (df, user_dict, item_dict)
