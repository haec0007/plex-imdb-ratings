import argparse
import csv
import datetime
import os

import plexapi.exceptions
from plexapi.server import PlexServer

from read_config import read_config

parser = argparse.ArgumentParser(description="Imports your IMDb user ratings into your Plex server.")
parser.add_argument("config", help="The YAML configuration file containing user-specific parameters.")
args = parser.parse_args()
CONFIG = read_config(args.config)

ratings_file = 'ratings.csv'
log_file = 'last_run.log'
plex_ip = CONFIG['plex']['ip']
plex_token = CONFIG['plex']['token']
lib_name = CONFIG['plex']['library']
plex_server = PlexServer(plex_ip, plex_token)

plex_lib = plex_server.library.section(lib_name)


def rate(imdb_id, imdb_year, rating):
    video = plex_lib.getGuid(f'imdb://{imdb_id}')

    # Search for other items in the Plex library with the same guid.
    # This ensures all editions of a movie get rated.
    search_results = plex_lib.search(guid=video.guid)
    for v in search_results:
        v.rate(rating)

    movie_title = video.title
    half_rating = rating / 2
    if half_rating == int(half_rating):
        half_rating = int(half_rating)
    print(f'{movie_title} ({imdb_year}) | {half_rating}/5')


def log_date():
    ratings_date = datetime.datetime.fromtimestamp(os.path.getmtime('ratings.csv')).date()
    f = open(log_file, 'w')
    f.write(str(ratings_date))
    f.close()


def last_run():
    try:
        f = open(log_file, 'r')
        dt = f.read()
        f.close()
    except FileNotFoundError:
        dt = '1970-01-01'
    return dt


def import_ratings():
    last_run_dt = last_run()
    last_run_dt = datetime.datetime.strptime(last_run_dt, '%Y-%m-%d')

    recently_added = plex_lib.search(filters={"addedAt>>=": last_run_dt})
    recently_added = [g.id[g.id.find('://') + 3:] for x in recently_added for g in x.guids if g.id[:4] == 'imdb']

    with open(ratings_file, "r") as csv_file:
        reader = csv.reader(csv_file)
        next(reader)  # Skip the first row (the header row)

        # Iterate through the rows of the CSV file
        for row in reader:
            # Get the movie title, rating, and IMDb id from the row
            date_rated = datetime.datetime.strptime(row[2], '%Y-%m-%d')
            rating = int(row[1])
            imdb_id = row[0]
            imdb_title = row[3]
            imdb_url = row[5]
            imdb_year = row[9]

            if (date_rated >= last_run_dt) or (imdb_id in recently_added):
                # Select movie in Plex library by IMDb id
                try:
                    rate(imdb_id, imdb_year, rating)
                except plexapi.exceptions.NotFound:
                    # The movie is not in the Plex library.
                    print(f'{imdb_title} ({imdb_year}) | {rating}/10 | {imdb_url}')
                    pass


if __name__ == '__main__':
    import_ratings()
    log_date()
