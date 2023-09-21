#!/bin/bash -x
DIR=$(dirname ${0})
PYTHON=${PYTHON:-python}
${PYTHON} ${DIR}/data_collector.py |& tee -a ${DIR}/live-data-$(date +"%F").log