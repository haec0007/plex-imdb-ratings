import argparse
import csv
import datetime

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

movies = plex_server.library.section(lib_name)


def rate(imdb_id, rating):
    video = movies.getGuid(f'imdb://{imdb_id}')
    movie_title = video.title
    video.rate(rating)
    half_rating = rating / 2
    if half_rating == int(half_rating):
        half_rating = int(half_rating)
    print(f'"{movie_title}": {half_rating}/5')


def log_date():
    f = open(log_file, 'w')
    f.write(str(datetime.datetime.now().date()))
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

    with open(ratings_file, "r") as csv_file:
        reader = csv.reader(csv_file)
        next(reader)  # Skip the first row (the header row)

        # Iterate through the rows of the CSV file
        for row in reader:
            # Get the movie title, rating, and IMDb id from the row
            date_rated = datetime.datetime.strptime(row[2], '%Y-%m-%d')
            rating = int(row[1])
            imdb_id = row[0]

            if date_rated >= last_run_dt:
                # Select movie in Plex library by IMDb id
                try:
                    rate(imdb_id, rating)
                except plexapi.exceptions.NotFound:
                    # The movie is not in the Plex library.
                    pass


if __name__ == '__main__':
    import_ratings()
    log_date()
