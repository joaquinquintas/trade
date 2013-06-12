#!/bin/bash
source /Users/joaquin/Documents/workspace/trade_env/bin/activate
python /Users/joaquin/Documents/workspace/trade/trade/manage.py syncdb
python /Users/joaquin/Documents/workspace/trade/trade/manage.py shell