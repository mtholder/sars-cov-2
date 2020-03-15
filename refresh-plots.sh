#!/bin/bash
for d in plots plots/confirmed plots/newcases ; do
  if ! test -d "${d}" ; then
    mkdir "${d}" || exit
  fi
done


# Pulls down data from 2019 Novel Coronavirus COVID-19 (2019-nCoV) Data Repository by Johns Hopkins CSSE
if test ${SKIP_COVID_PULL:-0} = 1 ; then
    echo 'skipping git pull'
else
    echo 'updating data from Johns Hopkins COVID-19 data repo...'
    if test -d COVID-19 ; then
        cd COVID-19 || exit
        git pull origin master || exit
        cd -
    else
        git clone https://github.com/CSSEGISandData/COVID-19.git
    fi
fi
echo 'See COVID-19 data terms of use at https://github.com/CSSEGISandData/COVID-19'
datadir="COVID-19/csse_covid_19_data/csse_covid_19_time_series"
fn="${datadir}/time_series_19-covid-Confirmed.csv"
python3 transpose_and_sum_by_country.py "${fn}" || exit
Rscript refresh-plots.R || exit