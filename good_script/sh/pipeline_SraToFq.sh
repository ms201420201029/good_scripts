#!/usr/bin/env bash
# Author:              masheng
# Version:             1.0.1
# Function:            Pipeline of sra to fq and configuration file before 16S analyse
# Way2use:             sh pipeline_SraToFq.sh configuration_file (first_col:sra_name , second_col:sample_name , third_col:label)

echo The version is v1.0.1
echo author is mas
echo you should configure the configuration to the right way
echo the first column are all the sra_name 
echo the second column are all the sample name
echo the third column are all the label of every sample

path_sra=$PWD
config=$1

if [ ! -d $PWD/fastq ];then
        mkdir $PWD/fastq
fi
if [ ! -d $PWD/pandaseq ];then
        mkdir $PWD/pandaseq
fi
if [ ! -d $PWD/group ];then
        mkdir $PWD/group
fi
if [ ! -d $PWD/rawdata ];then
        mkdir $PWD/rawdata
fi
if [ ! -d $PWD/analyse ];then
        mkdir $PWD/analyse
fi

## 00.creat configuration file of 16S analyse
echo The first step is create configuration file of 16S pipeline
echo --------------------------creat Configuration file--------------------------
i=1
less $config | while read line
    do if [ "$line" != "" ]
    then
        echo $line S$i
        i=$[$i+1]
    fi
done > sample.info
if [ ! -f $PWD/group/groupqb.txt ];then
        touch $PWD/group/groupqb.txt
fi
if [ ! -f $PWD/rawdata/name.list ];then
        touch $PWD/rawdata/name.list
fi

awk '{print $2,$3}' sample.info > group/groupqb.txt
cp group/groupqb.txt group/groupqb_alpha.txt
awk '{print $4,$2}' sample.info > rawdata/name.list
sed -i '1,$s/ /\t/g' group/groupqb.txt group/groupqb_alpha.txt rawdata/name.list
echo successful
echo --------------------------Ending creat Configuration file--------------------------

## 01.sra file to fastq under sra
echo The second step is split the sra file to fastq file
echo --------------------------sra file split to fastq file--------------------------
cd $path_sra/sra/
if [ ! -f $PWD/sraTofastq.sh ];then
        touch $PWD/sraTofastq.sh
fi

ls *.sra | awk -F '.' '{print $1}' | while read line
    do echo fastq-dump --split-3 $line\.sra
done | cat > sraTofastq.sh
sh sraTofastq.sh
mv *.fastq ../fastq/
echo successful
echo --------------------------Ending : sra file split to fastq file--------------------------

## 02.pandaseq fastq file under ./fastq/
echo The third step is pandaseq the pair sequence if have
echo --------------------------pandaseq fastq file--------------------------
cd ../fastq/

ifHavePairs=$(ls *.fastq | grep '_[12].fastq' | wc -l)
if [ ! -f $PWD/pandaseq.sh ];then
        touch $PWD/pandaseq.sh
fi

if [ $ifHavePairs != 0 ]; then
	ls | grep '_[12].fastq' |awk -F '_[12].fastq' '{print $1}' | uniq | while read line
    do echo pandaseq -f $line\_1.fastq -r $line\_2.fastq -F -w $PWD/$line\.fastq
done | cat > pandaseq.sh
	sh pandaseq.sh
else
	echo --------------------------these are single reads--------------------------
fi
awk '{print $1}' ../$config | awk -F '.' '{print $1}' | while read line
    do mv $line\.fastq ../pandaseq/
done
echo successful
echo --------------------------Ending pandaseq fastq file--------------------------

## 03.connect all the fastq file
echo The fourth step is connect all the fastq file to a big fastq file
echo --------------------------connect all the fastq file--------------------------
cd ../pandaseq/
if [ ! -f $PWD/ERR.info ];then
        touch $PWD/ERR.info
fi

awk '{print $1,$4}' ../sample.info > ERR.info
ls *.fastq | awk -F '.' '{print $1}' | while read line
    do SX=$(grep $line ERR.info | awk '{print $2}')
    awk -v sx=$SX '{  if( NR%4==1 ) { print $0,sx"_"(NR+3)/4 } else if( NR%4==3 ) { print "+" } else { print $0 } }' $line\.fastq
done | cat > ../rawdata/16S.fq
cd ..
echo successful
echo --------------------------Ending connect all the fastq file--------------------------

## move group and rawdata to analyse ; copy work.sh and work.cfg to analyse
echo The fifth step is move the configuration and big fastq file to the right path
mv group/ rawdata/ analyse/
cp /data_center_10/Publicdata/pipeline/work* analyse/
echo successful
echo --------------------------Ending! Please start to configure work.cfg--------------------------

