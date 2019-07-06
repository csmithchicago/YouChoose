# Copyright (c) 2019, Corey Smith
# Distributed under the MIT License.
# See LICENCE file in root directory for full terms.
"""
Visualization library.

"""
import matplotlib.pyplot as plt


def scatter(tsne, ax, title=None):
    ax.scatter(tsne[:, 0], tsne[:, 1])
    ax.set_title(title)


def embedding_tsne(tsne1, tsne2, titles, figsize=(20, 10)):
    f, (ax1, ax2) = plt.subplots(ncols=2, figsize=figsize)
    scatter(tsne1, ax1, titles[0])
    scatter(tsne2, ax2, titles[1])

    return f, (ax1, ax2)
