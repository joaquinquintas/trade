#!/bin/bash
#source /Users/joaquin/Documents/workspace/trade_env/bin/activate
python /Users/joaquin/Documents/workspace/trade/trade/manage.py syncdb
python /Users/joaquin/Documents/workspace/trade/trade/manage.py evolve --hint --execute
python /Users/joaquin/Documents/workspace/trade/trade/manage.py runserver 0.0.0.0:8888
