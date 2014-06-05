from collections import defaultdict
from rottentomatoes import RT
from difflib import get_close_matches
from utils import parse_csv, process_title
import csv
import traceback
import time

RT_API_KEY = 'bgcdtph7zqmpekwhg2um597g'
RT_FIELDS = [
    'title',
    'year',
    'rt_audience_score',
    'rt_critics_score',
    'rt_matched_title',
    'rt_notes',
]
def filter_year(movie_list, year):
    if not year: return movie_list
    result = [mov for mov in movie_list if mov.get('year', None) == int(year)]
    return result or movie_list

def get_rottentomatoes_ratings(title, year, result=None):
    print "Processing {} - {}".format(title, year)
    result = result or defaultdict(lambda: "N/A", {'title':title, 'year': year})
    notes = []
    try:
        rt = RT(RT_API_KEY)
        movie_list = rt.search(process_title(title))
        if year:
            movie_list = filter_year(movie_list, year)
        if not movie_list:
            raise Exception("No results found.")
        try:
            movie = movie_list[0]
            result['rt_matched_title'] = movie['title']
            result['rt_audience_score'] = movie['ratings']['audience_score']
            result['rt_critics_score'] = movie['ratings']['critics_score']
        except KeyError:
            notes.append("Results not found: {}".format(title))

    except Exception as e:
        notes.append("Exception encountered: {}".format(e))
        traceback.print_exc()
    finally:
        # result['Title'] = title
        # result['Year'] = year
        result['rt_notes'] = '|'.join(notes)
        return result


def main():
    movies = parse_csv()
    with open("rottentomatoes.csv", 'w') as out:
        writer = csv.writer(out)
        writer.writerow(RT_FIELDS)
        for title, year in movies:
            result = get_rottentomatoes_ratings(title, year)
            writer.writerow([result[f] for f in RT_FIELDS])
            time.sleep(1)

if __name__ == '__main__':
    main()

