# Copyright (c) 2019, Corey Smith
# Distributed under the MIT License.
# See LICENCE file in root directory for full terms.
"""
Neural network layer library.

"""
import torch.nn as nn


class ScaledEmbedding(nn.Embedding):
    """
    Embedding layer that initialises its values with a normal distribution.
    The variance is set to the inverse of the embedding dimension squared.

    .. math:: weights ~ N(0, (\frac{1}{n_d})^2)
    """

    def reset_parameters(self):
        """
        Initialize parameters.
        """
        self.weight.data.normal_(0, 1.0 / self.embedding_dim)


class ZeroEmbedding(nn.Embedding):
    """
    Embedding layer that initialises its values
    to zero. Used for biases.
    """

    def reset_parameters(self):
        """
        Initialize parameters.
        """
        self.weight.data.zero_()
