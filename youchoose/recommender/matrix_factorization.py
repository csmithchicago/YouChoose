# Copyright (c) 2019, Corey Smith
# Distributed under the MIT License.
# See LICENCE file in root directory for full terms.
"""
Matrix factorization recommender.

"""
# import torch
# import torch.nn as nn
from .recommender import Recommender


class MatrixFactorization(Recommender):
    """
    Recommendation class that makes recommendations based on methods
    that use matrix factorization.
    """

    def __init__(
        self,
        method,
        data,
        use_cuda,
        embedding_dimension,
        train_frac,
        test_frac,
        epochs,
        reg,
        optimizer,
    ):
        """
        Initialize the latent matrices and optimization parameters.

        Args:
            method (str): The type of matrix factorization to use.
            reg (float, optional): If reg is greater than 0, add L2 regularization on the latent dimensions.
            optimizer (str, optional): sgd, adam, etc
            loss (str): ranking, pointwise, mse
            neg_samples (int, optional): for pairwise ranking, the number of negative samples to use.
        """
        assert method in ["nn", "als"]

    def create(self):
        pass

    def train(self):
        pass

    def evaluate(self):
        pass

    def save(self):
        pass

    def load(self):
        pass

    def deploy(self):
        pass

    def recommend_top(self):
        pass
