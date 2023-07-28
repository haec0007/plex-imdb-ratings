# plex-imdb-ratings
Python scripts for downloading your IMDb user ratings and importing them into Plex.
## Installation and Setup
Clone or download this project to a location on your computer.

Microsoft Edge must be installed. This project downloads your IMDb ratings using a Selenium Edge web driver.

Make sure you are logged in to IMDb.com on Edge under the profile specified in your configuration file. IMDb has measures that prevent the use of automated methods to login, so we must load a user profile that is already logged in to the site.
## Usage
```
python download_ratings.py <config_file>
python import_ratings.py <config_file>
```
The `download_ratings.py` script downloads a CSV of your ratings from IMDb.com into this project's folder. The `import_ratings.py` script then uses these ratings to rate all matching movies on your Plex server using the Plex API. Only movies that are in the library specified in the configuration file will be rated.
## Configuration File
This is a YAML file that contains user-specific parameters needed to run the download and import scripts. You will need to create one that contains the following information:
- **plex**
  - **ip:** The IP address and port of your Plex server.
  - **token:** Your Plex authentication token. This article will tell you how to find yours: https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/
  - **library:** The name of the Plex library containing videos you want to rate.
- **browser_options**
  - **user_data_dir:** The location of your Microsoft Edge User Data folder.
  - **profile_dir:** The Microsoft Edge profile you are running under.

`example_config.yml` contains an example of what a configuration should look like.
