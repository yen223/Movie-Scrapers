from utils import parse_csv
from collections import defaultdict

from box_office_mojo import get_box_office_mojo_results
from rottentomatoes_script import get_rottentomatoes_ratings
from ebert import get_ebert_ratings
from metacritic import get_metacritic_ratings
import csv

FIELDS = [
    'title',
    'year',

    'bo_lifetime_gross',
    'bo_opening_gross',

    'rt_audience_score',
    'rt_critics_score',

    'ebert_score',

    'metacritic_critic_score',
    'metacritic_user_score',

    # For debugging purposes.
    'bo_matched_title',
    'rt_matched_title',
    'ebert_matched_title',
    'metacritic_matched_title',
    'bo_notes',
    'rt_notes',
    'ebert_notes',
    'metacritic_notes',
]

def collect_data(input_file="script.csv", output_file="movies.csv"):
    movies = parse_csv(input_file)
    with open(output_file, "w") as out:
        writer = csv.writer(out)
        writer.writerow(FIELDS)
        for title, year in movies:
            result = defaultdict(lambda: "N/A", {'title':title, 'year': year})
            result = get_box_office_mojo_results(title, year, result)
            result = get_rottentomatoes_ratings(title, year, result)
            result = get_ebert_ratings(title, year, result)
            result = get_metacritic_ratings(title, year, result)
            writer.writerow([unicode(result[f]).encode("utf-8") for f in FIELDS])


if __name__ == '__main__':
    collect_data()
