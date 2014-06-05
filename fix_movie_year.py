import csv

def get_year(value):
    if not value:
        return ''

    try:
        year = int(value)
        return unicode(year)
    except ValueError:
        try:
            tokens = value.split('-')
            if len(tokens) < 2:
                return ''
            year = int(tokens[0])
        except ValueError:
            try:
                year = int(tokens[1])
            except ValueError:
                return ''
    # If year is less than 14, assume it's 2014
    # Otherwise, assume it's 1915
    if year <= 14: 
        year += 2000
    else:
        year += 1900
    return unicode(year)


def fix_csv(input_file='script.csv', output_file='script_fixed.csv'):
    with open(input_file, 'r') as inp:
        with open(output_file, 'w') as out:
            csv_reader = csv.reader(inp)
            csv_writer = csv.writer(out)
            header = next(csv_reader, None)
            header.extend(['release_year', 'script_year'])
            csv_writer.writerow(header)
            for row in csv_reader:
                print row
                new_row = row
                release_year = get_year(row[2])
                script_year = get_year(row[3])
                row.extend([release_year, script_year])
                csv_writer.writerow(row)

if __name__ == '__main__':
    fix_csv()