# Copyright (c) 2019, Corey Smith
# Distributed under the MIT License.
# See LICENCE file in root directory for full terms.
"""
Download and unzip instacart data.

"""
import os
import shutil
from datetime import datetime

import wget
import requests
from bs4 import BeautifulSoup


def main():
    project_dir = os.path.join(os.path.dirname(__file__), os.pardir)
    data_path = os.path.join(project_dir, "../data/")
    extract_dir = data_path + "external/"
    page_url = "https://www.instacart.com/datasets/grocery-shopping-2017"

    # only download files in the extracted directory doesn't exist.
    if not os.path.isdir(extract_dir + "instacart_2017_05_01/"):
        print("Getting files ...")

        download_zip_filename = data_path + "instacart_data.tar.gz"
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/73.0.3683.86 Safari/537.36"
            )
        }
        try:
            data = requests.get(page_url, headers=headers)
            data.raise_for_status()
        except Exception as e:
            print(
                f"Error: {e}. Unable to fetch URL for dataset. Please visit [{page_url}] to download the dataset."
            )

        instacart_html = BeautifulSoup(data.content, "html.parser")

        for anchor in instacart_html.select("a"):
            if anchor["href"].startswith("https://s3"):
                data_url = anchor["href"]

        print("Beginning file download ...")
        wget.download(data_url, download_zip_filename)

        print("\nUnzipping csv files ...")
        shutil.unpack_archive(download_zip_filename, extract_dir)
        os.remove(download_zip_filename)

    print("Add data attribution to README file ...")
    with open(project_dir + "/../README.md", "r") as f:
        content = f.readlines()

    attribution = (
        f'"The Instacart Online Grocery Shopping Dataset 2017", '
        f"Accessed from [Instacart]({page_url}) "
        f"on {datetime.now():%m-%d-%Y}"
    )

    for idx, line in enumerate(content):
        if repr(line) == repr("Project References\n"):
            ref_line = idx
            break

    first_item = ref_line + 3
    check_for = "The Instacart Online Grocery Shopping Dataset 2017"
    attribution_line = "* " + attribution

    # Is data attribution the first bullet item in references?
    if not content[first_item].startswith(check_for, 3):
        content.insert(first_item, "\n")
        content.insert(first_item, "\n")
        content.insert(first_item, attribution_line)
    # Check to make sure date is current to today.
    elif content[first_item] != attribution_line:
        content[first_item] = attribution_line

    with open(project_dir + "/../README.md", "w") as f:
        for line in content:
            f.write(line)


if __name__ == "__main__":
    main()
