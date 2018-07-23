# bak good script
# example sh bak.sh script1.name script2.name ······

scripts=$* ;
IFS=' ' scripts_arr=($scripts) ;


# echo help info
if [[ ${#scripts_arr[*]} == 0 || ${#scripts_arr[*]} == 1 && ${scripts_arr[0]} == '-h' || ${scripts_arr[0]} == '--help' ]]
then
    echo
    echo 'usage: bak [file ..]              bak scripts, files are separated by a space'
    echo '       bak -l/list || -ll/llist   print bak scripts listi(no link, has link use -ll/llist)'
    echo '       bak del [file/folder ..]   del bak scripts/folder, files are separated by a space'
    echo '       bak -h/--help              print this help info'
    echo
    echo '       This script is to bak good scripts, will create bak file to /data_center_01/home/mas/good_script/ .'
    echo '       Scripts will be auto classified to diff folder by their suffix. Example: test.py will be backupsed to folder py .'
    echo
    echo 'example:'
    echo '       bak script1 script2 script3'
    echo '       bak list'
    echo '       bak del script1 script3 folder'
    echo 
    exit 2
fi


# output bak scripts list
echo
echo bak dir: /data_center_01/home/mas/good_script/
echo
if [[ ${#scripts_arr[*]} == 1 && ${scripts_arr[0]} == list || ${scripts_arr[0]} == '-l' || ${scripts_arr[0]} == '-ll' || ${scripts_arr[0]} == 'llist' ]]
then
    ls -d /data_center_01/home/mas/good_script/*/ | while read line
    do
        type=$(basename $line)
        if [[ $(ls -f /data_center_01/home/mas/good_script/$type/ | grep $type'$' | wc -l) > 0 ]]
        then
            echo $type
            ls -rt /data_center_01/home/mas/good_script/$type/*$type | while read script
            do
                time=$(ls --full-time $script | grep -E -o '[0-9]{4}-[0-9]{2}-[0-9]{2}')
                # time=$(ls --full-time $script | grep -E -o '[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}')
                script_name=$(basename $script)
                ln_s=$(readlink -f $script.bak)
                if [[ ${scripts_arr[0]} == '-ll' || ${scripts_arr[0]} == 'llist' ]]
                then
                    echo -e '  '$time' '$script_name'    <--- '$ln_s
                else
                    echo -e '  '$time' '$script_name
                fi
            done
            echo '---------------------------------------------'
        fi
    done
    exit 2
fi


# del bak scripts
if [[ ${scripts_arr[0]} == del ]]
then
    echo 'log:' 
    for s in ${scripts_arr[*]:1} ;
    do
        if [ -d /data_center_01/home/mas/good_script/$s ]
        then
            read -p "    "$s"是一个文件夹，是否删除（y/n）：" choose
            if [ $choose == 'y' ]
            then
                rm -rf /data_center_01/home/mas/good_script/$s && echo '    --->' del folder: [ $s ] ;
            fi
        continue
        fi

        type=$(echo $s | awk -F '.' '{print $NF}') ;
        s_name=$(basename $s)
        if [ -f /data_center_01/home/mas/good_script/$type/$s_name ]
        then
            rm /data_center_01/home/mas/good_script/$type/$s_name /data_center_01/home/mas/good_script/$type/$s_name.bak && echo -e '    --->' del bak file: [ $s_name , $s_name.bak ] ;
        else
            echo $s is not in bak files
        fi
    done
    echo
    exit 2
fi


# bak scripts
echo 'log:'
for s in ${scripts_arr[*]} ;
do
    s_path=$(readlink -f $s) ;
    s_name=$(basename $s)
    type=$(echo $s | awk -F '.' '{print $NF}') ;
    if [ -f $s ]
    then
        mkdir -p /data_center_01/home/mas/good_script/$type ;
        if [ -f /data_center_01/home/mas/good_script/$type/$s_name ]
        then
            read -p "    文件夹中已存在需要备份的文件，是否覆盖（y/n）：" choose
            if [ $choose == 'y' ]
            then
                cp $s_path /data_center_01/home/mas/good_script/$type && ln -fs $s_path /data_center_01/home/mas/good_script/$type/$s_name.bak && echo -e '    --->' cover bak file: [ $s_name , $s_name.bak ] ;
            fi
        else
            cp $s_path /data_center_01/home/mas/good_script/$type && ln -s $s_path /data_center_01/home/mas/good_script/$type/$s_name.bak && echo -e '    --->' create bak file: [ $s_name , $s_name.bak ] ;
        fi
    else
        echo '    '$s' is not exist!'
    fi
done
echo

