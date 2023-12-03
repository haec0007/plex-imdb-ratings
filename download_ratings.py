import argparse
import os
import pathlib

from playwright.sync_api import sync_playwright
from playwright._impl._errors import Error as PlaywrightAPIError

from read_config import read_config


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Downloads your user ratings from IMDb.")
    parser.add_argument("config", help="The YAML configuration file containing user-specific parameters.")
    args = parser.parse_args()
    CONFIG = read_config(args.config)

    user_data_dir = CONFIG['browser_options']['user_data_dir']
    profile_dir = CONFIG['browser_options']['profile_dir']
    imdb_ratings_page = 'https://www.imdb.com/list/ratings?ref_=nv_usr_rt_4'
    this_dir = pathlib.Path(__file__).parent.resolve()

    with sync_playwright() as p:
        chromium = p.chromium
        browser = chromium.launch_persistent_context(user_data_dir, headless=True)
        api_request_context = browser.request
        page = browser.new_page()
        page.goto(imdb_ratings_page)
        url = page.url
        imdb_user_nbr = url.split('https://www.imdb.com/user/ur', 1)[1][:8]
        imdb_ratings_download = f"https://www.imdb.com/user/ur{imdb_user_nbr}/ratings/export"
        with page.expect_download() as download_info:
            try:
                page.goto(imdb_ratings_download)
            except PlaywrightAPIError:
                pass
        download = download_info.value
        download.save_as(os.path.join(this_dir, 'ratings.csv'))
        browser.close()
