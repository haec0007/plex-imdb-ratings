import argparse
import os
import pathlib
import sys
import traceback

from playwright.sync_api import sync_playwright
from playwright._impl._errors import Error as PlaywrightAPIError

from read_config import read_config


def cleanup(web_browser, web_page=None):
    if web_page is not None:
        web_page.close()
    web_browser.close()
    return None


def raise_error():
    # Force an error. Here for testing purposes.
    raise RuntimeError('A fake error occurred.')


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
        page = None
        chromium = p.chromium
        browser = chromium.launch_persistent_context(user_data_dir, headless=True)
        try:
            exit_code = 0
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
        except Exception:
            traceback.print_exc()
            exit_code = 1
        finally:
            cleanup(browser, page)
            sys.exit(exit_code)
