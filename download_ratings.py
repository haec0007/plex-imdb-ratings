import argparse
import os
import pathlib
import time

from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from read_config import read_config


def wait_for_download(filename, timeout=30):
    end_time = time.time() + timeout
    last_modified = os.path.getmtime(filename)
    while os.path.getmtime(filename) <= last_modified:
        time.sleep(1)
        if time.time() > end_time:
            raise Exception("File not downloaded in time.")
    if os.path.getmtime(filename) > last_modified:
        print(f"File saved to {os.path.abspath(filename)}")
        return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Downloads your user ratings from IMDb.")
    parser.add_argument("config", help="The YAML configuration file containing user-specific parameters.")
    args = parser.parse_args()
    CONFIG = read_config(args.config)

    user_data_dir = CONFIG['browser_options']['user_data_dir']
    profile_dir = CONFIG['browser_options']['profile_dir']
    imdb_ratings_page = 'https://www.imdb.com/list/ratings?ref_=nv_usr_rt_4'
    this_dir = pathlib.Path(__file__).parent.resolve()

    user_agent = UserAgent().edge
    options = webdriver.EdgeOptions()
    options.add_argument(f"--user-agent={user_agent}")
    options.add_argument(f"user-data-dir={user_data_dir}")
    options.add_argument(f"profile-directory={profile_dir}")
    options.add_argument("--headless")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])  # Silence DevTools messages

    prefs = {
        "profile.default_content_settings.popups": 0,
        "download.default_directory": str(this_dir),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True
    }
    options.add_experimental_option("prefs", prefs)

    driver_path = '...'
    driver = webdriver.Edge(options=options, service=Service(driver_path))
    driver.get(imdb_ratings_page)

    url = driver.current_url
    imdb_user_nbr = url.split('https://www.imdb.com/user/ur', 1)[1][:8]
    imdb_ratings_download = f"https://www.imdb.com/user/ur{imdb_user_nbr}/ratings/export"

    driver.get(imdb_ratings_download)
    wait_for_download('ratings.csv')
