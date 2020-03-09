#!/usr/bin/env python
import sys
import csv

def parse_headers(row):
    dates = []
    first_date_ind = 4
    assert row[:first_date_ind] == ['Province/State', 'Country/Region', 'Lat', 'Long']
    name_ind = 0
    country_ind = 1
    for h in row[first_date_ind:]:
        dates.append(h)
    return name_ind, country_ind, first_date_ind, dates

def add_to_column(dl, count_data):
    for d_ind, el in enumerate(count_data):
        dl[d_ind] += int(el)

def parse_input(fn):
    by_country = {}
    with open(fn, 'r', encoding='utf-8') as csvfile:
        rdr = csv.reader(csvfile, delimiter=',')
        country_ind = None
        for row in rdr:
            if country_ind is None:
                blob = parse_headers(row)
                name_ind, country_ind, first_data_ind, dates = blob
                num_dates = len(dates)
                continue
            raw_country = row[country_ind]
            country = raw_country.lower().strip()
            prov_name = row[name_ind].lower()
            other = None
            if ' ship' in prov_name:
                country = 'cruise ships'
            elif country != 'mainland china':
                other = 'outside china and ships'
            count_data = row[first_data_ind:]
            assert(len(count_data) == num_dates)
            for t in [country, other, 'world']:
                if t is None:
                    continue
                dl = by_country.setdefault(t, [0]*num_dates)
                add_to_column(dl, count_data)

    return dates, by_country

def dump_csv(fn, key_order, data_dict, num_data_rows):
    with open(fn, 'w', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(key_order)
        for i in range(num_data_rows):
            curr_row = []
            for key in key_order:
                col = data_dict[key]
                curr_row.append(col[i])
            writer.writerow(curr_row)


if __name__ == '__main__':
    tag = 'confirmed'
    dates, by_country = parse_input(sys.argv[1])
    out_keys = list(by_country.keys())
    out_keys.sort()
    out_keys.insert(0, 'date')
    by_country['date'] = dates
    dump_csv('{}.csv'.format(tag), out_keys, by_country, len(dates))