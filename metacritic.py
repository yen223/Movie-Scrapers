from urllib import quote
from collections import defaultdict
from difflib import get_close_matches
from utils import parse_csv, process_title
from bs4 import BeautifulSoup
import requests
import csv
import traceback
import time

METACRITIC_FIELDS = [
    'title',
    'year',
    'metacritic_critic_score',
    'metacritic_user_score',
    'metacritic_matched_title',
    'metacritic_notes',
]

def filter_year(movie_list, year):
    if not year: return movie_list
    result = []
    for mov in movie_list:
        date_tag = mov.find('li', class_='release_date')
        if date_tag:
            date_data = date_tag.find('span', class_='data').text.strip()
            if year in date_data:
                result.append(mov)
        else:
            result.append(mov)
    return result or movie_list


def fetch_site(title, year):
    print "Processing {} - {}".format(title, year)
    try:
        # url = "http://www.rogerebert.com/reviews"
        proc_title = process_title(title)
        proc_title = '+'.join(proc_title.split())
        # print "Proc_title:", proc_title
        print "Query: {}".format(proc_title)
        url = "http://www.metacritic.com/search/movie/{}/results".format(proc_title)
        req = requests.get(url)
        return req.text
    except Exception as e:
        print 'Error encountered while fetching {}: {}'.format(title, e)
        traceback.print_exc()
        return None


def get_metacritic_ratings(title, year, result=None):
    result = result or defaultdict(lambda: "N/A", {'title':title, 'year': year})
    notes = []
    try:
        html = fetch_site(title, year)
        soup = BeautifulSoup(html)
        reviews = soup.find_all('li', class_='result')
        reviews = filter_year(reviews, year)
        if reviews:
            review = reviews[0].find(class_="basic_stats")
            result['metacritic_matched_title'] = review.find(class_="product_title").text.strip()
            result['metacritic_critic_score'] = review.find(class_="metascore_w").text.strip()
            result['metacritic_user_score'] = review.find(class_="product_avguserscore").find(class_="data").text.strip()
        else:
            raise Exception("No results found")
        
        print '-'*50
        print u"Matched {}".format(result['metacritic_matched_title'])
        print '-'*50
        print u"Critic Score: {}".format(result['metacritic_critic_score'])
        print u"User Score: {}".format(result['metacritic_user_score'])

    except KeyboardInterrupt as ki:
        raise ki
    except Exception as e:
        notes.append("Exception encountered: {}".format(e))
        traceback.print_exc()
    finally:
        # result['Title'] = title
        # result['Year'] = year
        result['metacritic_notes'] = '|'.join(notes)
        return result


def main():
    movies = parse_csv()
    with open("metacritic.csv", 'w') as out:
        writer = csv.writer(out)
        writer.writerow(METACRITIC_FIELDS)
        for title, year in movies:
            result = get_metacritic_ratings(title, year)
            writer.writerow([result[f].encode("utf-8") for f in METACRITIC_FIELDS])
            # time.sleep(1)

if __name__ == '__main__':
    main()

