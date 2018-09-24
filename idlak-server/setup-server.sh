#!/bin/bash
TOREPLACE="from pip import main"
REPLACETO="from pip._internal import main"

echo "virtualenv venv"
virtualenv venv
echo "source venv/bin/activate"
source venv/bin/activate
echo "replace \"$TOREPLACE\" \"$REPLACETO\" -- venv/bin/pip3"
replace "$TOREPLACE" "$REPLACETO" -- venv/bin/pip3
echo "venv/bin/pip3 install -r requirements.txt"
venv/bin/pip3 install -r requirements.txt
echo "export FLASK_APP=runserver.py"
export FLASK_APP=runserver.py
