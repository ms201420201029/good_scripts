# Memory Monitor

# get running jib ID 
job=$(qstat | grep ' r ' | awk '{printf "%d,",$1 }')
IFS=',' job_arr=($job)

# get time and create a folder
start_datetime="`date +%Y-%m-%d-%H-%M`"
echo $start_datetime
if [ -n "$job" ];then
    mkdir $start_datetime
fi

# put work path and set momery to each log file
for j in ${job_arr[@]}
do
    sample=$(qstat -j $j | grep 'cwd' | awk -F '/' '{print $NF}')
    touch $start_datetime/$sample-$j.log
    echo $start_datetime > $start_datetime/$sample-$j.log
    qstat -j $j | grep 'cwd' >> $start_datetime/$sample-$j.log
    qstat -j $j | grep 'virtual_free' >> $start_datetime/$sample-$j.log
    qstat -j $j | grep '^script_file:' >> $start_datetime/$sample-$j.log
done

# get real-time memory in every minute
# statistic interval is 60 second
interval=60

while [ -n "$job" ]
do
    cur_datetime="`date +%Y-%m-%d' '%H':'%M`"
    for j in ${job_arr[@]}
    do
        sample=$(qstat -j $j | grep 'cwd' | awk -F '/' '{print $NF}')
        if [ ! -f $start_datetime/$sample-$j.log ]
        then
            echo $cur_datetime > $start_datetime/$sample-$j.log
            qstat -j $j | grep 'cwd' >> $start_datetime/$sample-$j.log
            qstat -j $j | grep 'virtual_free' >> $start_datetime/$sample-$j.log
            qstat -j $j | grep '^script_file:' >> $start_datetime/$sample-$j.log
        fi
        echo $cur_datetime >> $start_datetime/$sample-$j.log
        qstat -j $j | grep 'maxvmem' >> $start_datetime/$sample-$j.log
    done
    sleep $interval
    job=$(qstat | grep ' r ' | awk '{printf "%d,",$1 }')
    IFS=',' job_arr=($job)
done

