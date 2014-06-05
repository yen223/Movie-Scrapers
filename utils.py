import csv
def parse_csv(filename='script.csv'):
    movies = [] # List of (title, date) tuples
    with open(filename, 'rU') as f:
        csv_reader = csv.reader(f)
        next(csv_reader, None)
        for row in csv_reader:
            movies.append((row[1], row[-2]))

    return movies


def process_title(title):
    title = title.strip()

    # Lower case it.
    title = title.lower()
    # 'Addams Family, The'->'The Addams Family'
    if len(title) >= 5 and title[-5:] == ', the':
        title = 'the ' + title[:-5]

    if len(title) >= 3 and title[-3:] == ', a':
        title = 'a ' + title[:-3]

    # Remove apostrophes and commas: "Smokin' Aces" -> "Smokin Aces"
    tokens = title.split()
    title = " ".join([word.split("'")[0] for word in tokens])
    title = "".join(title.split(","))

    return title