from collections import defaultdict
from difflib import get_close_matches
from utils import parse_csv, process_title
from bs4 import BeautifulSoup
import requests
import csv
import traceback
import time

EBERT_FIELDS = [
    'title',
    'year',
    'ebert_score',
    'ebert_matched_title',
    'ebert_notes',
]
# def filter_year(movie_list, year):
#     if not year: return movie_list
#     result = [mov for mov in movie_list if mov.get('year', None) == int(year)]
#     return result or movie_list


def fetch_site(title, year):
    print "Processing {} - {}".format(title, year)
    try:
        # url = "http://www.rogerebert.com/reviews"
        if year:
            year1 = year2 = year
        else:
            year1 = '1914'
            year2 = '2014'
        proc_title = process_title(title)
        url = "http://www.rogerebert.com/reviews?filters%5Bgreat_movies%5D%5B%5D="\
        +"&filters%5Bno_stars%5D%5B%5D=&filters%5Bno_stars%5D%5B%5D=1"\
        +"&filters%5Btitle%5D={title}&filters%5Breviewers%5D=&filters%5Bgenres%5D="\
        +"&filters%5Byears%5D%5B%5D={year1}&filters%5Byears%5D%5B%5D={year2}&page=1"\
        +"&sort%5Border%5D=newest"
        url = url.format(title=proc_title, year1=year1, year2=year2)
        # params = {
        #     "filters[great_movies][]": "",
        #     "filters[no_stars][]": "",
        #     "filters[no_stars][]": 1,
        #     "filters[title]": title,
        #     "filters[reviewers]": "",
        #     "filters[genres]": "",
        #     "filters[years][]": year,
        #     "filters[years][]": year,
        #     "page": "1",
        #     "sort[order]": "newest",
        # }
        req = requests.get(url, headers={'referer': "http://www.rogerebert.com/reviews"})
        return req.text
    except Exception as e:
        print 'Error encountered while fetching {}: {}'.format(title, e)
        return None


def get_ebert_ratings(title, year, result=None):
    result = result or defaultdict(lambda: "N/A", {'title':title, 'year': year})
    notes = []
    try:
        html = fetch_site(title, year)
        soup = BeautifulSoup(html)
        review = soup.find(id='review-list').find('figure', class_='movie review')        
        
        if not review:
            raise Exception("No results found: {}".format(title))
        result['ebert_score'] = len(review.find_all(class_="icon-star-full")) + len(review.find_all(class_="icon-star-half")) * 0.5
        result['ebert_matched_title'] = review.find(class_="title").text.strip()

        print "{}: Matched {}, Score {}".format(title, 
            result['ebert_matched_title'], 
            result['ebert_score'])
    except KeyboardInterrupt as ki:
        raise ki
    except Exception as e:
        notes.append("Exception encountered: {}".format(e))
        # traceback.print_exc()
    finally:
        # result['Title'] = title
        # result['Year'] = year
        result['ebert_notes'] = '|'.join(notes)
        return result


def main():
    movies = parse_csv()
    with open("ebert.csv", 'w') as out:
        writer = csv.writer(out)
        writer.writerow(EBERT_FIELDS)
        for title, year in movies:
            result = get_ebert_ratings(title, year)
            writer.writerow([result[f] for f in EBERT_FIELDS])
            # time.sleep(1)

if __name__ == '__main__':
    main()

