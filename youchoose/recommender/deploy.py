# Copyright (c) 2019, Corey Smith
# Distributed under the MIT License.
# See LICENCE file in root directory for full terms.
"""
 The deploy module can be used to deploy a trained model to be used for inferance.
"""
from .recommender import Recommender


def aws_s3(model: Recommender):
    model.save()
    pass


def aws_sagemaker(model: Recommender):
    model.save()
    pass


def gcp_cloudstorage(model: Recommender):
    model.save()
    pass
