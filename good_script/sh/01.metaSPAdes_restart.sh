# initialize dir based on initialize to which path, batch.list has sample info, clean.list dir which has reads after clean the reads
# example sh shell/00.metaSPAdes_pre.sh /data_center_11/Project/RY2017B20G01-1/03.assembly_metaSPAdes/ /data_center_11/Project/RY2017B20G01-1/sample_list/batch.list /data_center_11/Project/RY2017B20G01-1/01.clean_reads/01.clean_reads/

path=$1
batch=$2
clean_path=$3


# generate metaSPAdes.sh
mkdir -p $path/clean_fq
scrip_path=$(dirname $(readlink -f $0))
if [[ $(ls $path/assembly/*/output/scaffolds.fasta | wc -l) > 0 ]]
then
    touch $scrip_path/metaSPAdes_restart.sh
    > $scrip_path/metaSPAdes_restart.sh
    cat $( grep 'End$' $batch | cut -f2 ) | cut -f1 | sort | uniq | grep -E -v $(ls $path/assembly/*/output/scaffolds.fasta | awk -F '/' '{print $(NF-2)}' | xargs | tr ' ' '|') | while read sample
    do
        ls /data_center_11/Project/RY2017B20G01-1/01.clean_reads/01.clean_reads/$sample.{1,2,single}.fq.gz | while read file
        do
            fq=$(basename $file | sed 's/.gz$//g')
        done
        echo /data_center_01//home/mas/software/SPAdes/SPAdes-3.11.1-Linux/bin/spades.py -1 $path/clean_fq/$sample.1.fq -2 $path/clean_fq/$sample.2.fq -s $path/clean_fq/$sample.single.fq -m 60 -k 63 -o $path/assembly/$sample/output >> $scrip_path/metaSPAdes_restart.sh
        mkdir -p $path/assembly/$sample/output
    done
else
    touch $scrip_path/metaSPAdes.sh
    > $scrip_path/metaSPAdes.sh
    cat $( grep 'End$' $batch | cut -f2 ) | cut -f1 | uniq | while read sample
    do
        ls /data_center_11/Project/RY2017B20G01-1/01.clean_reads/01.clean_reads/$sample.{1,2,single}.fq.gz | while read file
        do
            fq=$(basename $file | sed 's/.gz$//g')
            echo '#' gunzip -c $file \> $path/clean_fq/$fq >> $scrip_path/metaSPAdes.sh
        done
        echo /data_center_01//home/mas/software/SPAdes/SPAdes-3.11.1-Linux/bin/spades.py -1 $path/clean_fq/$sample.1.fq -2 $path/clean_fq/$sample.2.fq -s $path/clean_fq/$sample.single.fq -m 60 -k 63 -o $path/assembly/$sample/output >> $scrip_path/metaSPAdes.sh
        mkdir -p $path/assembly/$sample/output
    done
fi

## qsub
#if [ -f $scrip_path/metaSPAdes_restart.sh ]
#then
#    jobs=$(wc -l $scrip_path/metaSPAdes_restart.sh | cut -f1 -d' ')
#    nohup perl /data_center_03/USER/zhongwd/bin/qsge --jobs $jobs --lines 1 --queue SJQ --memery 60G --prefix AS $scrip_path/metaSPAdes_restart.sh &
#else
#    jobs=$[$(wc -l $scrip_path/metaSPAdes.sh | cut -f1 -d' ')/4]
#    nohup perl /data_center_03/USER/zhongwd/bin/qsge --jobs $jobs --lines 4 --queue SJQ --memery 60G --prefix AS $scrip_path/metaSPAdes.sh &
#fi







