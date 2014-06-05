from urllib import urlencode
from bs4 import BeautifulSoup
from collections import defaultdict
from difflib import get_close_matches
from utils import parse_csv, process_title
import requests
import csv
import re
import traceback

result_fields=  [
    'title',
    'year',
    'bo_matched_title',
    'bo_matched_link', 
    'bo_studio',
    'bo_lifetime_gross',
    'bo_lifetime_theaters',
    'bo_opening_gross',
    'bo_opening_theaters',
    'bo_release_date',
    'bo_notes',
]


def filter_year(tags, year):
    if not year: return tags
    new_tags = []
    for tag in tags:
        year_link = tag.find('a', text=re.compile('\d+/\d+/\d+'))
        if year_link and year in year_link.text:
            new_tags.append(tag)
    return new_tags or tags


def fetch_site(title, year):
    print "Processing {} - {}".format(title, year)
    try:
        url = "http://www.boxofficemojo.com/search/"
        proc_title = process_title(title)
        param = {'q': proc_title}

        req = requests.get(url, params=param)
        return req.text
    except Exception as e:
        print 'Error encountered while fetching {}: {}'.format(title, e)
        return None


def process_site(html, title, year, result=None):
    result = result or defaultdict(lambda: "N/A",  {'title':title, 'year': year})
    notes = []
    try:
        soup = BeautifulSoup(html)
        label = soup.find('b', text=re.compile('\d+ Movie Matches'))
        # if title == '2012':
        #     # 2012 returned every movie released in 2012!
        #     raise Exception("2012 returned too many results.")

        if not label:
            # No results found...
            notes.append('No results: {}'.format(title))
        else:
            # Yes, I use row colours to get the result
            # Ugly hack, but it works.
            results = label.find_all_next('tr',bgcolor=["#FFFF99","#F4F4FF", "#FFFFFF"])
            results = filter_year(results, year)

            notes.append("{} results found".format(len(results)))
            if len(results) > 1:
                # Sprinkle some magic to find closest match.
                result_dict = {r.find('td').text.strip():r for r in results}
                try:
                    proc_title = process_title(title)
                    matched_title = get_close_matches(proc_title, result_dict.keys(), cutoff=0.0)[0]
                    matched_row = result_dict[matched_title]
                except IndexError:
                    notes.append("No good matches found.")
                    matched_row = results[0]
            elif len(results) == 1:
                matched_row = results[0]
            else:
                raise Exception("No results were found.")

            try:
                data = [x.text.strip() for x in matched_row.find_all('td')]
                m_link = matched_row.find('td').find('a')['href']

                result['bo_matched_title'] = data[0]
                result['bo_studio'] = data[1]
                result['bo_lifetime_gross'] = data[2]
                result['bo_lifetime_theaters'] = data[3]
                result['bo_opening_gross'] = data[4]
                result['bo_opening_theaters'] = data[5]
                result['bo_release_date'] = data[6]
                
                result['bo_matched_link'] = m_link
                
            except Exception as e:
                # print "Exception:", row
                notes.append("Exception encountered: {}".format(e))

    except Exception as e:
        notes.append("Exception encountered: {}".format(e))
        traceback.print_exc()
    finally:
        # result['Title'] = title
        # result['Year'] = year
        result['bo_notes'] = '|'.join(notes)
        return result


def get_box_office_mojo_results(title, year, result=None):
    html = fetch_site(title, year)
    result = process_site(html, title, year, result)
    return result

def main():
    movies = parse_csv()
    with open('box_office_mojo.csv', 'w') as out:
        writer = csv.writer(out)
        writer.writerow(result_fields)
        for m in movies:
            title, year = m
            html = fetch_site(title, year)
            result = process_site(html, title, year)
            writer.writerow([result[f] for f in result_fields])

if __name__ == '__main__':
    main()