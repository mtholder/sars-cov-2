#!/usr/bin/env python
import sys
import csv

regions = {
    'central asia': ['afghanistan', 'armenia', 'azerbaijan', 'bangladesh', 'bhutan', 'georgia', 'india', 'maldives', 'nepal', 'pakistan', 'sri lanka', 'russia',],
    'africa': ['algeria', 'cameroon', 'egypt', 'morocco', 'nigeria', 'senegal', 'south africa', 'togo', 'tunisia',],
    'europe': ['albania', 'andorra', 'austria', 'belarus', 'belgium', 'bosnia and herzegovina', 'bulgaria', 
               'croatia', 'cyprus', 'czech republic', 'denmark', 'estonia', 'faroe islands', 'finland', 'france', 'germany', 'gibraltar', 'greece', 'hungary', 'iceland', 'ireland', 'italy', 'latvia', 'liechtenstein', 'lithuania', 'luxembourg', 'malta', 'moldova', 'monaco', 'netherlands', 'north macedonia', 'norway', 'poland', 'portugal', 'republic of ireland', 'romania', 'san marino', 'serbia', 'slovakia', 'slovenia', 'spain', 'sweden', 'switzerland', 'uk', 'ukraine', 'vatican city', ],
    'south am': ['argentina', 'brazil', 'chile', 'colombia', 'ecuador', 'french guiana', 'paraguay', 'peru' ],
    'se asia': ['brunei', 'cambodia', 'indonesia', 'malaysia', 'philippines', 'thailand', 'vietnam', 'singapore'],
    'east asia': ['hong kong', 'japan', 'macau', 'mainland china', 'taiwan', 'south korea', ],
    'aust nz':  ['australia', 'new zealand'],
    'middle east':  ['bahrain', 'iran', 'iraq', 'israel', 'jordan', 'kuwait', 'lebanon', 'palestine', 'qatar', 'saudi arabia', 'oman', 'united arab emirates', ],
    'north am':  ['canada', 'mexico', 'us',],
    'central am':  ['costa rica', 'dominican republic', 'martinique', 'saint barthelemy', 'st. martin'],
}

def country_to_region(country):
    for region, country_list in regions.items():
        if country in country_list:
            return region
    raise NotImplementedError('Need to add a "{}" to a region!'.format(country))

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
    meta = set(['world'])
    region_of_china = country_to_region('mainland china')
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
            tag_list = ['world', ]
            country = raw_country.lower().strip()
            prov_name = row[name_ind].lower()
            other = None
            if ' ship' in prov_name:
                country = 'cruise ships'
            else:
                region = country_to_region(country)
                if region:
                    tag_list.append(region)
                if country != 'mainland china':
                    if region:
                        if region == region_of_china:
                            rstr = '{} without china'.format(region)
                            meta.add(rstr)
                            tag_list.append(rstr)
                        else:
                            rstr = 'world without {}'.format(region_of_china)
                            meta.add(rstr)
                            tag_list.append(rstr)
                    wochina = 'outside china and ships'
                    tag_list.append(wochina)
                    meta.add(wochina)
            tag_list.append(country)
            count_data = row[first_data_ind:]
            assert(len(count_data) == num_dates)
            for t in tag_list:
                if t is None:
                    continue
                dl = by_country.setdefault(t, [0]*num_dates)
                add_to_column(dl, count_data)

    return dates, by_country, meta

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

def _write_index_conf_row(outp, x, by_country, fmt_list):
    outp.write('<tr><td>{} ({:,})</td>'.format(x, by_country.get(x, [0])[-1]))
    for fmt in fmt_list:
        mog_x = fmt.format('-'.join(x.split(' ')))
        outp.write('<td><img src="{}" alt="{}"/></td>'.format(mog_x, x))
    outp.write('</tr>\n')

def write_index(keys, extra_locs, by_country, fn, fmt):
    print(keys)
    print(extra_locs)
    with open(fn, 'w', encoding='utf-8') as outp:
        outp.write('<html>\n<head>\n<title>confirmed cases</title>\n</head>\n<body>\n')
        outp.write('<table>')
        for x in extra_locs:
            _write_index_conf_row(outp, x, by_country, fmt)
        for reg_keys in regions.keys():
            _write_index_conf_row(outp, reg_keys, by_country, fmt)
        rk = list(regions.keys())
        rk.sort()
        for k in rk:
            countries = regions[k]
            for c in countries:
                _write_index_conf_row(outp, c, by_country, fmt)
        outp.write('</table>\n')
        outp.write('</body>\n</html>\n')

if __name__ == '__main__':
    tag = 'confirmed'
    dates, by_country, extra_locs = parse_input(sys.argv[1])
    out_keys = list(by_country.keys())
    out_keys.sort()
    bef_date = list(out_keys)
    out_keys.insert(0, 'date')
    by_country['date'] = dates
    dump_csv('{}.csv'.format(tag), out_keys, by_country, len(dates))
    fmt_list = ['{}/{}'.format(i, i) + '-{}.png' for i in ['confirmed', 'newcases']]
    write_index(bef_date, extra_locs, by_country, 'plots/index.html', fmt_list)
