#!/bin/bash
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
