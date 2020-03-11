#!/usr/bin/env python
import sys
import csv
import re
aliases = {'iran (islamic republic of)': 'iran',
           'holy see': 'vatican city',
           'republic of ireland': 'ireland',
           'republic of moldova': 'moldova',
           'republic of korea': 'south korea',
           'hong kong sar': 'hong kong',
           'taipei and environs': 'taiwan',
           'viet nam': 'vietnam',
           'occupied palestinian territory': 'palestine',
           'macao sar': 'macau',
           'russian federation': 'russia',
           'saint martin': 'st. martin',
           }

regions = {
    'central asia': ['afghanistan', 'armenia', 'azerbaijan', 'bangladesh', 'bhutan', 'georgia', 'india', 'maldives',
                     'nepal', 'pakistan', 'sri lanka', 'russia', ],
    'africa': ['algeria', 'burkina faso', 'cameroon', 'egypt', 'morocco', 'nigeria', 'senegal', 'south africa', 'togo',
               'tunisia', ],
    'europe': ['albania', 'andorra', 'austria', 'belarus', 'belgium', 'bosnia and herzegovina', 'bulgaria',
               'channel islands', 'croatia', 'cyprus', 'czech republic',
               'denmark', 'estonia', 'faroe islands', 'finland', 'france',
               'germany', 'gibraltar', 'greece', 'hungary',
               'iceland', 'ireland', 'italy', 'latvia', 'liechtenstein', 'lithuania', 'luxembourg', 'malta', 'moldova',
               'monaco', 'netherlands', 'north macedonia', 'norway', 'poland', 'portugal',
               'romania', 'san marino', 'serbia', 'slovakia', 'slovenia', 'spain', 'sweden', 'switzerland', 'uk',
               'ukraine', 'vatican city', ],
    'south am': ['argentina', 'brazil', 'chile', 'colombia', 'ecuador', 'french guiana', 'paraguay', 'peru'],
    'se asia': ['brunei', 'cambodia', 'indonesia', 'malaysia', 'philippines', 'thailand', 'vietnam', 'singapore'],
    'east asia without china': ['hong kong', 'japan', 'macau', 'mongolia', 'taiwan', 'south korea', ],
    'mainland china': ['mainland china',],
    'aust nz': ['australia', 'new zealand'],
    'middle east': ['bahrain', 'iran', 'iraq', 'israel', 'jordan', 'kuwait', 'lebanon', 'palestine', 'qatar',
                    'saudi arabia', 'oman', 'united arab emirates', ],
    'north am': ['canada', 'mexico', 'us', ],
    'central am': ['costa rica', 'dominican republic', 'panama', 'martinique', 'saint barthelemy', 'st. martin'],
    'cruise ships': ['cruise ships']
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
        if el:
            dl[d_ind] += int(el)

_US_LOC_PAT = re.compile(r'^(.*), ([a-z][a-z]) *$')
_STATE_CODE_TO_NAME = {"ak": "alaska",
                       "az": "arizona",
                       "ar": "arkansas",
                       "ca": "california",
                       "co": "colorado",
                       "ct": "connecticut",
                       "de": "delaware",
                       "dc": "washington, d.c.",
                       "fl": "florida",
                       "ga": "georgia",
                       "hi": "hawaii",
                       "id": "idaho",
                       "il": "illinois",
                       "in": "indiana",
                       "ia": "iowa",
                       "ks": "kansas",
                       "ky": "kentucky", "la": "louisiana", "me": "maine", "md": "maryland",
                       "ma": "massachusetts", "mi": "michigan", "mn": "minnesota", "ms": "mississippi",
                       "mo": "missouri", "mt": "montana",
                       "ne": "nebraska", "nv": "nevada", "nh": "new hampshire", "nj": "new jersey",
                       "nm": "new mexico", "ny": "new york", "nc": "north carolina", "nd": "north dakota",
                       "oh": "ohio", "ok": "oklahoma", "or": "oregon",
                       "pa": "pennsylvania", "ri": "rhode island", "sc": "south carolina", "sd": "south dakota",
                       "tn": "tennessee", "tx": "texas", "ut": "utah",
                       "vt": "vermont", "va": "virginia", "wa": "washington",
                       "wv": "west virginia", "wi": "wisconsin", "wy": "wyoming",}

def normalize_us(raw_by_country):
    us_locs = raw_by_country['us']
    states_seen = set()
    highest_group = []
    for loc, counts in us_locs:
        if not _US_LOC_PAT.match(loc):
            states_seen.add(loc)
            highest_group.append((loc, counts))
    ss = list(states_seen)
    ss.sort()
    summed_from_locals = {}
    for loc, counts in us_locs:
        m = _US_LOC_PAT.match(loc)
        if m:
            st_code = m.group(2)
            state_name = _STATE_CODE_TO_NAME[st_code]
            if state_name not in states_seen:

                highest_group.append((loc, counts))
            if state_name in summed_from_locals:
                summed_from_locals[state_name] = sum_lists([counts, summed_from_locals[state_name]])
            else:
                summed_from_locals[state_name] = list(counts)
    by_higher_group_or_summed = []
    for k, v in highest_group:
        if k in summed_from_locals:
            sfl = summed_from_locals[k]
            by_higher_group_or_summed.append((k, sum_lists([v, sfl])))
        else:
            by_higher_group_or_summed.append((k, v))
        print(by_higher_group_or_summed[-1] )
    raw_by_country['us'] = by_higher_group_or_summed


def sum_lists(list_of_lists):
    summed = list(list_of_lists[0])
    for cts in list_of_lists[1:]:
        # print(summed, cts)
        for n, el in enumerate(cts):
            summed[n] += el
    return summed

def accum_by_country(raw_by_country):
    normalize_us(raw_by_country)
    by_country = {}
    for country, loc_list in raw_by_country.items():
        summed = sum_lists([i[1] for i in loc_list])
        by_country[country] = summed
    for k, v in by_country.items():
        print(k, v)
    return by_country

def accum_regions(by_country):
    #['central asia', 'africa', 'europe', 'south am', 'se asia', 'east asia without china', 'mainland china', 'aust nz',
    #  'middle east', 'north am', 'central am']
    regional = {}
    reg_meta = []
    for k, v in regions.items():
        if len(v) == 1:
            sys.stderr.write('1 country region: {}\n'.format(k))
            regional[k] = list(by_country[v[0]])
        else:
            regional[k] = sum_lists([by_country[i] for i in v if i in v])
            reg_meta.append((k, list(v)))

    regional['world'] = sum_lists(list(regional.values()))
    east_asia_keys = ['mainland china', 'east asia without china']
    regional['east asia'] = sum_lists([regional[i] for i in east_asia_keys])
    by_country.update(regional)
    reg_order = ['east asia', 'europe', 'north am', 'middle east', 'se asia',
                 'central asia', 'africa', 'south am', 'aust nz', 'central am', 'cruise ships']
    meta = [('world', reg_order), ('east asia', east_asia_keys)]
    meta.extend(reg_meta)
    return by_country, meta

def accum_by_country_and_region(raw_by_country):
    by_country = accum_by_country(raw_by_country)
    return accum_regions(by_country)

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
            if country in aliases:
                country = aliases[country]
            prov_name = row[name_ind].lower()
            if ' ship' in prov_name or ' princess' in prov_name:
                country = 'cruise ships'
            count_data = [0 if not i else int(i) for i in row[first_data_ind:]]
            assert (len(count_data) == num_dates)
            by_country.setdefault(country, []).append((prov_name, count_data))
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


def _write_index_conf_row(outp, x, by_country, fmt_list):
    outp.write('<tr><td>{} ({:,})</td>'.format(x, by_country.get(x, [0])[-1]))
    for fmt in fmt_list:
        mog_x = fmt.format('-'.join(x.split(' ')))
        outp.write('<td><img src="{}" alt="{}"/></td>'.format(mog_x, x))
    outp.write('</tr>\n')


def _rec_table_rows(outp, top_group, meta, by_country, fmt):
    group_key =  top_group[0]
    sub_keys = top_group[1]
    # outp = sys.stdout # TEMP
    _write_index_conf_row(outp, group_key, by_country, fmt)
    queued, next_lev = [], []
    for mk, mvl in meta:
        if mk in sub_keys:
            queued.append((mk, mvl))
        else:
            next_lev.append((mk, mvl))
    for k in sub_keys:
        qnl = [i for i in queued if i[0] == k]
        # print(k, qnl)
        if qnl:
            _rec_table_rows(outp, qnl[0], meta, by_country, fmt)
        else:
            _write_index_conf_row(outp, k, by_country, fmt)
    # for x in extra_locs:
    #     _write_index_conf_row(outp, x, by_country, fmt)
    # for reg_keys in regions.keys():
    #     _write_index_conf_row(outp, reg_keys, by_country, fmt)
    # rk = list(regions.keys())
    # rk.sort()
    # for k in rk:
    #     countries = regions[k]
    #     for c in countries:
    #         _write_index_conf_row(outp, c, by_country, fmt)

def write_index(keys, meta, by_country, fn, fmt):
    with open(fn, 'w', encoding='utf-8') as outp:
        outp.write('<html>\n<head>\n<title>confirmed cases</title>\n</head>\n<body>\n')
        outp.write('<table>')
        top_group = meta.pop(0)
        _rec_table_rows(outp, top_group, meta, by_country, fmt)
        outp.write('</table>\n')
        outp.write('</body>\n</html>\n')

def main(fp):
    tag = 'confirmed'
    dates, raw_by_country = parse_input(fp)
    by_country, groupings = accum_by_country_and_region(raw_by_country)
    out_keys = list(by_country.keys())
    out_keys.sort()
    bef_date = list(out_keys)
    out_keys.insert(0, 'date')
    by_country['date'] = dates
    dump_csv('{}.csv'.format(tag), out_keys, by_country, len(dates))
    fmt_list = ['{}/{}'.format(i, i) + '-{}.png' for i in ['confirmed', 'newcases']]
    write_index(bef_date, groupings, by_country, 'plots/index.html', fmt_list)


if __name__ == '__main__':
    main(sys.argv[1])
