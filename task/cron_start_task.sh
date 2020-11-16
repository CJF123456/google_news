#!/bin/sh
ps -ef|grep -v 'grep'|grep 'cron_start_task.py'|awk '{print $2}'|xargs kill -9
cron_start_task=$(ps -ef|grep -v 'grep'|grep -c 'cron_start_task.py')

ulimit -c unlimited

echo "cron_start_task.sh"
if [ "$cron_start_task" -eq "0" ]
then
cd /data/python_server/google_news/task/

python cron_start_task.py &
cd /data/python_server/logs/
now=`date +%Y-%m-%d[%H:%M:%S]`
echo "at $now start cron_start_task.py\n">> cron_start_task.log
fi