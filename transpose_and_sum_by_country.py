#!/usr/bin/env python
import sys
import csv
import os

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
           'china': 'mainland china',
           'korea, south': 'south korea',
           'united kingdom': 'uk',
           'czechia': 'czech republic',
           'taiwan*': 'taiwan',
           'congo (kinshasa)': 'congo',
           "cote d'ivoire": 'ivory coast',
           'fench guiana': 'french guiana',
           'gambia': 'the gambia',
           'gambia, the': 'the gambia',
           'bahamas, the': 'the bahamas',
           'bahamas': 'the bahamas',
           'cape verde': 'cabo verde',
           }

regions = {
    'central asia': ['afghanistan', 'armenia', 'azerbaijan', 'bangladesh', 'bhutan', 'georgia',
                     'india', 'kazakhstan', 'kyrgyzstan', 'maldives',
                     'nepal', 'pakistan', 'sri lanka', 'russia', 'uzbekistan',],
    'africa': ['algeria', 'angola', 'benin', 'burkina faso', 'cabo verde', 'cameroon', 'chad',
               'central african republic', 'congo', 'republic of the congo', 'congo (brazzaville)',
               'djibouti', 'egypt', 'equatorial guinea', 'eritrea', 'eswatini', 'ethiopia',
               'gabon', 'ghana', 'guinea', 'guinea-bissau', 'ivory coast', 'kenya', 'liberia', 'libya',
               'madagascar', 'mali', 'mauritania', 'mauritius',
               'mayotte', 'morocco', 'mozambique', 'namibia', 'niger', 'nigeria',
               'reunion', 'rwanda', 'senegal', 'seychelles', 'somalia', 'south africa', 'sudan', 'tanzania', 'the gambia',  'togo', 'uganda',
               'tunisia', 'zambia', 'zimbabwe'],
    'europe': ['albania', 'andorra', 'austria', 'belarus', 'belgium', 'bosnia and herzegovina', 'bulgaria',
               'channel islands', 'croatia', 'cyprus', 'czech republic',
               'denmark', 'estonia', 'faroe islands', 'finland', 'france',
               'germany', 'gibraltar', 'greece', 'guernsey', 'hungary',
               'iceland', 'ireland', 'italy', 'jersey', 'kosovo', 'latvia', 'liechtenstein', 'lithuania', 'luxembourg', 'malta', 'moldova',
               'monaco', 'montenegro', 'netherlands', 'north ireland', 'north macedonia', 'norway', 'poland', 'portugal',
               'romania', 'san marino', 'serbia', 'slovakia', 'slovenia', 'spain', 'sweden', 'switzerland', 'uk',
               'ukraine', 'vatican city', ],
    'south am': ['argentina', 'bolivia', 'brazil', 'chile', 'colombia', 'ecuador', 'french guiana',
                 'guyana', 'paraguay', 'peru', 'suriname', 'uruguay', 'venezuela'],
    'se asia': ['brunei', 'burma', 'cambodia', 'east timor', 'fiji', 'guam', 'indonesia', 'laos', 'malaysia',
                'philippines', 'thailand', 'vietnam', 'singapore', 'timor-leste'],
    'east asia without china': ['hong kong', 'japan', 'macau', 'mongolia', 'taiwan', 'south korea', ],
    'mainland china': ['mainland china', ],
    'aust nz': ['australia', 'french polynesia', 'new zealand', 'papua new guinea',],
    'middle east': ['bahrain', 'iran', 'iraq', 'israel', 'jordan', 'kuwait', 'lebanon', 'oman',  'palestine', 'qatar',
                    'saudi arabia', 'syria', 'turkey', 'united arab emirates', 'west bank and gaza', ],
    'north am': ['canada', 'greenland', 'mexico', 'us', ],
    'central am': ['antigua and barbuda', 'aruba', 'belize', 'barbados', 'cayman islands', 'costa rica', 'cuba', 'curacao', 'dominica',
                   'dominican republic', 'el salvador', 'grenada', 'guadeloupe', 'guatemala', 'haiti', 'honduras', 'jamaica',
                   'martinique', 'nicaragua', 'panama', 'puerto rico', 'saint barthelemy',
                   'saint kitts and nevis', 'saint lucia', 'st. martin', 'saint vincent and the grenadines',
                   'the bahamas', 'trinidad and tobago'],
    'cruise ships': ['cruise ships', 'diamond princess',  'ms zaandam', ]
}

state_name_to_abbrev = {
    'alabama': 'al',
    'alaska': 'ak',
    'arizona': 'az',
    'arkansas': 'ar',
    'california': 'ca',
    'colorado': 'co',
    'connecticut': 'ct',
    'delaware': 'de',
    'dc': 'dc',
    'florida': 'fl',
    'georgia': 'ga',
    'hawaii': 'hi',
    'idaho': 'id',
    'illinois': 'il',
    'indiana': 'in',
    'iowa': 'ia',
    'kansas': 'ks',
    'kentucky': 'ky',
    'louisiana': 'la',
    'maine': 'me',
    'maryland': 'md',
    'massachusetts': 'ma',
    'michigan': 'mi',
    'minnesota': 'mn',
    'mississippi': 'ms',
    'missouri': 'mo',
    'montana': 'mt',
    'nebraska': 'ne',
    'nevada': 'nv',
    'new hampshire': 'nh',
    'new jersey': 'nj',
    'new mexico': 'nm',
    'new york': 'ny',
    'north carolina': 'nc',
    'north dakota': 'nd',
    'northern mariana islands':'mp',
    'ohio': 'oh',
    'oklahoma': 'ok',
    'oregon': 'or',
    'palau': 'pw',
    'pennsylvania': 'pa',
    'puerto rico': 'pr',
    'rhode island': 'ri',
    'south carolina': 'sc',
    'south dakota': 'sd',
    'tennessee': 'tn',
    'texas': 'tx',
    'utah': 'ut',
    'vermont': 'vt',
    'virgin islands': 'vi',
    'virginia': 'va',
    'washington': 'wa',
    'west virginia': 'wv',
    'wisconsin': 'wi',
    'wyoming': 'wy',
    'guam': 'guam', # not a two-letter, code, I know...
    'american samoa': 'american samoa',
}
_abbrev_to_state_name = {v:k for k, v in state_name_to_abbrev.items()}
_abbrev_to_state_name['d.c.'] = 'dc'
_us_loc_to_state = {'chicago': 'illinois',
                    'district of columbia': 'dc',
                    'united states virgin islands': 'virgin islands',
                   }


ALL_COUNTRIES = set()
for cs in regions.values():
    ALL_COUNTRIES.update(cs)


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


def sum_lists(list_of_lists):
    loli = iter(list_of_lists)
    summed = list(next(loli))
    for cts in loli:
        # print('summing', summed, 'len=', len(summed), 'and', cts, 'len=', len(cts))
        for n, el in enumerate(cts):
            summed[n] += el
    return summed


def accum_by_country(raw_by_country):
    bc = {}
    _by_us_state = {}
    for country, prov_dict in raw_by_country.items():
        if country == 'us':
            for k, v in prov_dict.items():
                if ',' in k:
                    tla = k.split(',')[-1].strip()
                    try:
                        state_name = _abbrev_to_state_name[tla]
                    except:
                        if 'virgin islands' in k:
                            state_name = 'virgin islands'
                        else:
                            raise NotImplementedError('translating "{}"'.format(k))
                else:
                    state_name = _us_loc_to_state.get(k, k)
                    if state_name not in state_name_to_abbrev:
                        if state_name == 'us':
                            pass
                        elif state_name not in ('wuhan evacuee', 'recovered'):
                            raise NotImplementedError('recognition of state "{}" -> {}'.format(k, v))
                cv = _by_us_state.get(state_name)
                if cv:
                    _by_us_state[state_name] = sum_lists([cv, v])
                else:
                    _by_us_state[state_name] = list(v)
        # print(country, prov_dict)
        # for k, v in prov_dict.items():
        #     print('  ', k)
        #     print('  ', v)
        bc[country] = sum_lists(list(prov_dict.values()))
    for k, v in _by_us_state.items():
        bc['us-loc-{}'.format(k)] = v
    # print(_by_us_state)
    return bc


def accum_regions(by_country):
    # ['central asia', 'africa', 'europe', 'south am', 'se asia', 'east asia without china', 'mainland china', 'aust nz',
    #  'middle east', 'north am', 'central am']
    regional = {}
    reg_meta = []
    for k, v in regions.items():
        if len(v) == 1:
            sys.stderr.write('1 country region: {}\n'.format(k))
            regional[k] = list(by_country[v[0]])
        else:
            regional[k] = sum_lists([by_country[i] for i in v if i in v and i in by_country])
            reg_meta.append((k, list(v)))

    regional['world'] = sum_lists(list(regional.values()))
    east_asia_keys = ['mainland china', 'east asia without china']
    regional['east asia'] = sum_lists([regional[i] for i in east_asia_keys])
    by_country.update(regional)
    us_loc_label = 'us-loc'
    reg_order = ['east asia', 'europe', 'north am', 'middle east', 'se asia',
                 'central asia', 'africa', 'south am', 'aust nz', 'central am', us_loc_label]
    meta = [('world', reg_order), ('east asia', east_asia_keys)]
    meta.extend(reg_meta)
    us_loc_list = [i for i in by_country.keys() if i.startswith('us-loc-')]
    us_loc_list.sort()
    meta.append((us_loc_label, us_loc_list))
    return by_country, meta


def accum_by_country_and_region(raw_by_country):
    by_country = accum_by_country(raw_by_country)
    return accum_regions(by_country)


def parse_daily_rep(fp, num_prev, confirmed, dead, recovered):
    country_ind = 1
    prov_ind = 0
    conf_ind, dead_ind, rec_ind = 3, 4, 5
    with open(fp, 'r', encoding='utf-8') as csvfile:
        ship_ind = 0
        rdr = csv.reader(csvfile, delimiter=',')
        rit = iter(rdr)
        header = next(rit)
        if header[0].endswith('Province/State'):
            country_ind = 1
            conf_ind, dead_ind, rec_ind = 3, 4, 5
            last_up_ind = 2
            assert header[country_ind] == 'Country/Region'
        else:
            prov_ind = 2
            #FIPS,Admin2,Province_State,Country_Region,Last_Update,Lat,Long_,Confirmed,Deaths,Recovered,Active,Combined_Key
            assert header[prov_ind] == 'Province_State'
            country_ind = 3
            last_up_ind = 4
            conf_ind, dead_ind, rec_ind = 7, 8, 9
        ind_dest_list = [(conf_ind, confirmed), (dead_ind, dead), (rec_ind, recovered)]
        assert header[country_ind].startswith('Country') and header[country_ind].endswith('Region')
        assert header[last_up_ind].startswith('Last') and header[last_up_ind].endswith('Update')
        assert header[conf_ind] == 'Confirmed'
        assert header[dead_ind] == 'Deaths'
        assert header[rec_ind] == 'Recovered'

        for row in rit:
            country, prov, ship_ind = _proc_country_str(row[country_ind], row[prov_ind], ship_ind)

            for stat_ind, stat_dest in ind_dest_list:
                new_country = country not in stat_dest
                by_prov = stat_dest.setdefault(country, {})
                if new_country and stat_ind == conf_ind:
                    if country not in ALL_COUNTRIES:
                        raise RuntimeError("Need to add '{}' to a region".format(country))
                    # sys.stderr.write('"{}" new country in {}\n'.format(country, fp))
                elif prov not in by_prov:
                    pass  # sys.stderr.write('"{}" new part of {} in {}\n'.format(prov, country, fp))
                count_list = by_prov.setdefault(prov, [0] * num_prev)
                # print(fp, country, prov, stat_ind, num_prev, len(count_list), count_list)
                new_datum_str = row[stat_ind]
                new_datum = int(new_datum_str) if new_datum_str else 0
                if len(count_list) != num_prev:
                    assert len(count_list) == 1 + num_prev
                    count_list[-1] = new_datum + count_list[-1]
                else:
                    count_list.append(new_datum)
                # if country == 'us':
                #    print('added {} to {} for {} {}'.format(new_datum_str, count_list, country, prov))
        ndl = num_prev + 1
        for x in ind_dest_list:
            stat_dest = x[1]
            for by_prov in stat_dest.values():
                for count_by_prov in by_prov.values():
                    if len(count_by_prov) < ndl:
                        count_by_prov.append(0)
                        assert len(count_by_prov) == ndl


def parse_daily_rep_input(daily_rep_dir, confirmed, dead, recovered):
    sub = os.listdir(daily_rep_dir)
    dates = []
    num_prev = 0
    for month in range(1, 13):
        m_str = '{:02}'.format(month)
        for day in range(1, 31):
            d_str = '{:02}'.format(day)
            fn_str = '{}-{}-2020.csv'.format(m_str, d_str)
            if fn_str in sub:
                dates.append('{}/{}/20'.format(month, day))
                fp = os.path.join(daily_rep_dir, fn_str)
                parse_daily_rep(fp, num_prev, confirmed, dead, recovered)
                # print(fn_str, confirmed)
                num_prev += 1
    return dates


def _proc_country_str(raw_country, raw_prov, ship_ind):
    country = raw_country.lower().strip()
    if country in aliases:
        country = aliases[country]
    prov_name = raw_prov.lower()
    if ' ship' in prov_name or ' princess' in prov_name:
        country = 'cruise ships'
        ship_ind += 1
        prov_name = '{}record{}'.format(prov_name, ship_ind)
    if prov_name in ['hong kong', 'macau']:
        country = prov_name

    return country, prov_name, ship_ind


def parse_input(fn):
    by_country = {}
    ship_ind = 0
    with open(fn, 'r', encoding='utf-8') as csvfile:
        rdr = csv.reader(csvfile, delimiter=',')
        country_ind = None
        for row in rdr:
            if country_ind is None:
                blob = parse_headers(row)
                name_ind, country_ind, first_data_ind, dates = blob
                num_dates = len(dates)
                continue
            country, prov_name, ship_ind = _proc_country_str(row[country_ind], row[0], ship_ind)
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
    from xml.sax.saxutils import quoteattr
    ax = quoteattr(x)
    if x == 'us-loc':
        x = 'us'
    c_list = by_country['confirmed'].get(x, [0])
    d_list = by_country['dead'].get(x, [0])
    r = by_country['recovered'].get(x, [0])[-1]
    c = c_list[-1]
    if c < 5:
        return
    d = d_list[-1]
    trfmt = '<tr id={}><td><div align="right"> {}<br />cases: {:7,}{}<br />deaths: {:7,}{}'
    if r > 0:
        trfmt = trfmt + '<br />recovered: {:7,}<br />active: {:7,}'.format(r, c - d - r)
    cgrs = get_daily_growth_est_str(c_list, GROWTH_RATE_WINDOW)
    dgrs = get_daily_growth_est_str(d_list, GROWTH_RATE_WINDOW)
    outp.write(trfmt.format(ax, x, c, cgrs, d, dgrs))
    outp.write('</div></td>')
    for fmt in fmt_list:
        mog_x = fmt.format(c='-'.join(x.split(' ')))
        outp.write('<td><img src="{}" alt="{}"/></td>'.format(mog_x, x))
    outp.write('</tr>\n')

def get_daily_growth_est_str(c_list, window):
    grwinpone = window + 1
    c = c_list[-1]
    if len(c_list) < grwinpone or c_list[-grwinpone] < 10 or c_list[-grwinpone] >= c:
        return ''
    prior_c = float(c_list[-grwinpone])
    window_mult = c/prior_c
    per_day_growth = (window_mult ** (1.0 / window) - 1) * 100
    if per_day_growth > 0.05:
        return ' (+{:.1f}%)'.format(per_day_growth, window)
    return ''

def _rec_table_rows(outp, top_group, meta, by_country, fmt):
    group_key = top_group[0]
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



GROWTH_RATE_WINDOW = 7
# Thanks to https://www.w3schools.com/howto/howto_css_fixed_sidebar.asp  for the sidenav bar css.
PREFACE = '''<html>
<head>
  <title>Plots of data from Johns Hopkins CSSE</title>
<style>
.sidenav {
  height: 100%;
  width: 180px;
  position: fixed;
  z-index: 1;
  top: 0;
  left: 0;
  background-color: #111;
  overflow-x: hidden;
  padding-top: 20px;
}
.sidenav a {
  padding: 6px 8px 6px 16px;
  text-decoration: none;
  font-size: 20px;
  color: #818181;
  display: block;
}

.sidenav a:hover {
  color: #f1f1f1;
}

.main {
  margin-left: 180px; /* Same as the width of the sidebar */
  padding: 0px 10px;
}
</style>
</head>
<body>
<div class="sidenav">
  <a href="#intro">Notes+Credits</a>
  <a href="#east asia">East Asia</a>
  <a href="#europe">Europe</a>
  <a href="#north am">North America</a>
  <a href="#middle east">Middle East</a>
  <a href="#se asia">Southeast Asia</a>
  <a href="#central asia">Central Asia</a>
  <a href="#africa">Africa</a>
  <a href="#south am">South America</a>
  <a href="#aust nz">Australia+NZ+</a>
  <a href="#central am">Central Am.+Carib.</a>
  <a href="#us-loc">Within US</a>
</div>
<div class="main">

<h2 id="intro">Plots of covid-19 case count data</h2>
<p>The nextstrain collaborative effort has a nice FAQ if you want general information
about the COVID-19 coronavirus:
<a href="https://nextstrain.org/help/coronavirus/FAQ">https://nextstrain.org/help/coronavirus/FAQ</a>
</p> 
<p>Researchers at the Johns Hopkins University Center for Systems Science and Engineering have developed
a nice dashboard for viewing the case counts of covid-19 on a map.
Not only do they go through the very laborious task of compiling the counts daily, but they are kind enough
to share that data in easy-to-parse CSV files in a
<a href="https://github.com/CSSEGISandData/COVID-19">GitHub repository</a>.
Note their Terms of Use "This GitHub repo and its contents herein, including all data, mapping, and analysis,
copyright 2020 Johns Hopkins University, all rights reserved, is provided to the public strictly for educational and
 academic research purposes.
 The Website relies upon publicly available data from multiple sources, that do not always agree.
 The Johns Hopkins University hereby disclaims any and all representations and warranties with respect to the Website, 
 including accuracy, fitness for use, and merchantability.
Reliance on the Website for medical guidance or use of the Website in commerce is strictly prohibited."</p>
<p>
I found myself graphing the counts of cases by country on a log scale, frequently.
So I decided to generate those plots via scripts. 
My code for doing that is at <a href="https://github.com/mtholder/sars-cov-2">https://github.com/mtholder/sars-cov-2</a>, 
but it doesn't do a whole lot more than group their data by country and regions. 
All of the hard work need to generate these graphs is being done by the the Johns Hopkins CSSE folks; the thousands
of health care workers who are collecting the data; and large number of public health workers who are making
the data available. Some notes:</p>
  <ul>
    <li>Variation in the time of day that data is gathered makes the plots of new cases for a day <b>very</b> noisy, even at 
    large geographic scales.
    So, the new cases plots are the average number of new cases for the 3 days prior to the date shown on the x-axis.</li>
    <li>The regions I used for aggregating the countries are fairly arbitrary.
They reflect a mixture of geographic proximity and pragmatic considerations about what countries seem to be
affected in similar ways by the disease in early March, 2020
If you want to look at the python dictionaries I'm using to group countries into, see:
<a href="https://github.com/mtholder/sars-cov-2/blob/master/transpose_and_sum_by_country.py#L6-L70">transpose_and_sum_by_country.py#L6-L62</a></li>
    <li>Within each region, countries are listed alphabetically</li>
    <li>Countries with fewer than 5 cases are not plotted</li>
    <li>The data are currently being read from the 'csse_covid_19_data/csse_covid_19_daily_reports' directory of the JHU
git repo, because the data in the csse_covid_19_data/csse_covid_19_time_series underwent some change wrt how reporting was
done within countries. See <a href="https://systems.jhu.edu/research/public-health/2019-ncov-map-faqs/">their FAQ</a>
and <a href="https://github.com/CSSEGISandData/COVID-19/issues/382">issue-382</a>.</li>
    <li>The raw data do show some drops in the cumulative case counts in several countries. This would be impossible if
    the data were completely accurate. These errors creep in because the JHU researchers aggregating several different
    sources (as they note in their Terms of Use statement). My scripts do not attempt to correct these issues. They do 
    attempt to correct cases of the same locality having multiple names
    (see the <code>aliases</code> variable in transpose_and_sum_by_country.py)
     and some localities having duplicate entries in the daily reports (see the <code>known_dup</code> variable
    in my transpose_and_sum_by_country.py).</li>
    <li>The Johns Hopkins U. data is updated about once a day (usually in the late afternoon/evening in USA). See
    <a href="https://www.worldometers.info/coronavirus/">https://www.worldometers.info/coronavirus/</a> if you are
    looking for data that is updated more frequently.</li>
    <li>When "(+#%)" is reported, this is the percent daily growth rate of the count calculated over the last '''
PREFACE = PREFACE + str(GROWTH_RATE_WINDOW) + ''' days (for locations that had at least 10 counts
    at the earlier time point in that time range, and are showing appreciable growth in confirmed cases).</li>
 </ul>
<hr />
<p>
'''


def write_index(keys, meta, by_country, fn, fmt):
    with open(fn, 'w', encoding='utf-8') as outp:
        outp.write(PREFACE)
        outp.write('<table>\n')
        outp.write('<tr><th>Country/region</th><th><div align="center">cases in black solid<br />'
                   'active in black dashed<br/>'
                   '<font color="blue">recovered in blue</font><br />'
                   '<font color="red">deaths in red</font></div>'
                   '</th><th><div align="center">Mean # of new cases/day for the prior 3 days</div></th>'
                   '</th><th><div align="center">Mean # of new deaths/day for the prior 3 days</div></th>'
                   '<th><div align="center"># of new cases/day</div></th>' 
                   '<th><div align="center"># of new deaths/day</div></th>' 
                   '</tr>\n')
        top_group = meta.pop(0)
        _rec_table_rows(outp, top_group, meta, by_country, fmt)
        outp.write('</table>\n')
        outp.write('</div>\n</body>\n</html>\n')


def main(covid_dir):
    daily_rep_dir = os.path.join(covid_dir, 'csse_covid_19_data', 'csse_covid_19_daily_reports')
    confirmed, dead, recovered = {}, {}, {}
    dates = parse_daily_rep_input(daily_rep_dir, confirmed, dead, recovered)
    bdt = {}
    for coll, tag in [(confirmed, 'confirmed'), (dead, 'dead'), (recovered, 'recovered')]:
        by_country, groupings = accum_by_country_and_region(coll)
        out_keys = list(by_country.keys())
        out_keys.sort()
        bef_date = list(out_keys)
        out_keys.insert(0, 'date')
        by_country['date'] = dates
        dump_csv('{}.csv'.format(tag), out_keys, by_country, len(dates))
        bdt[tag] = by_country
    fmt_list = ['{}/{}'.format(i, i) + '-{c}.png' for i in ['confirmed', 'newcases']]
    fmt_list.append('deaths/newdeaths-{c}.png')
    fmt_list.append('newcases/newcases-nowindow-{c}.png')
    fmt_list.append('deaths/newdeaths-nowindow-{c}.png')
    write_index(bef_date, groupings, bdt, 'plots/index.html', fmt_list)


if __name__ == '__main__':
    main('COVID-19')
