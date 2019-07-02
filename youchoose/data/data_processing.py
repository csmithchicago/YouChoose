# Copyright (c) 2019, Corey Smith
# Distributed under the MIT License.
# See LICENCE file in root directory for full terms.
"""
Data processing library.
"""
import pandas as pd


def dataframe_split(df, train_frac=0.80, test_frac=0.10):
    """
    Split dataframe into training, testing, and validation sets.
    """
    train_df = df.sample(frac=train_frac, random_state=23)
    test_df = df.drop(train_df.index).sample(int(test_frac * len(df)), random_state=23)
    # All samples not in test or train sets are used for validation
    val_df = df.drop(pd.concat([train_df, test_df], axis=0).index)

    return train_df, val_df, test_df


def item_sets(df: pd.DataFrame) -> dict:
    """
    Generate sets for each user containing products that
    they have previously purchased.

    Args:
        df: Dataframe containing user_id and item_id columns.
    Return:
        prior_dict: Dictionary of users and a set of items that they have previously
            interacted with.
    """
    df_g = (
        df[["user_id", "item_id"]]
        .groupby(["user_id"])["item_id"]
        .agg(lambda x: {val for val in x})
    )
    df_g = df_g.reset_index()
    df_g.columns = ["user_id", "item_list"]
    prior_dict = df_g.set_index("user_id").to_dict()["item_list"]

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
