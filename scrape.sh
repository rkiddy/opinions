
cd /home/ray/opinions/

d=`date '+%Y%m%d_%H%M%S'`

log="opinions_log_$d.txt"

python3 scrape.py > logs/$log 2>&1

