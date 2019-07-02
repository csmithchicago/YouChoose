# Example Datasets to Test Recommendations

## Instacart Data

Released by Instacart in 2017 as part of a [Kaggle competition](https://www.kaggle.com/c/instacart-market-basket-analysis/overview). The following is directly from the competition overview.

> Instacart’s data science team plays a big part in providing this delightful shopping experience. Currently they use transactional data to develop models that predict which products a user will buy again, try for the first time, or add to their cart next during a session. Recently, Instacart open sourced this data - see their blog post on [3 Million Instacart Orders, Open Sourced](https://tech.instacart.com/3-million-instacart-orders-open-sourced-d40d29ead6f2).
> In this competition, Instacart is challenging the Kaggle community to use this anonymized data on customer orders over time to predict which previously purchased products will be in a user’s next order.

Submissions are evaluated based on the mean F1 score. The format of submissions need to follow the following format.

> For each order_id in the test set, you should predict a space-delimited list of product_ids for that order. If you wish to predict an empty order, you should submit an explicit 'None' value. You may combine 'None' with product_ids. The spelling of 'None' is case sensitive in the scoring metric. The file should have a header and look like the following:
>
> <p style="text-align: center;">order_id,products<br/>17,1 2 <br/>34,None<br/>137,1 2 3</p>

### Data Download

The transaction data can be downloaded in a zip file from Instacart at the following [link](https://www.instacart.com/datasets/grocery-shopping-2017). After downloading the unzipped data should be placed in `youchoose/data/external/`.

This can also be done by running `python youchoose/data_gen/get_instacart_data.py` from the command line. This will download the files and place them in the correct folder.

-   "The Instacart Online Grocery Shopping Dataset 2017", Accessed from [Instacart](https://www.instacart.com/datasets/grocery-shopping-2017) on 06-16-2019\*
