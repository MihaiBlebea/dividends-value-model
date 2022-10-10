#!/bin/bash

export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="${PYTHONPATH}:${PWD}"
# export PROJECT_KEY=a0ayplvz_8jKHJ48ZZ3e34F5jAwMHzFTF8X2xyWxE
# export DEV_ENV=local
eval "./env/bin/python3 -u ${1} ${@:2}"