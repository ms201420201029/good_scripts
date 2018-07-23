# 以各个个体获取的第一次样本作为第一轮样本
# 以各个个体获取的第最后一次样本作为第最后一轮样本
# example: sh top10_species.sh otu_table_L7.txt

otu=$1
out=$2

# 注：函数中数组的名称不能与外部的数组的名称一样，否则取到的数组不会是期望的数组
# 变量则没有此要求
function calculate_top10() {

s_arr=$1
otu=$2
otu_round=$3
out=$4

# 在丰度表中寻找样品的index放置于数组中
col_index=() ;
col_index[0]=1 ;
i=1 ;
for s in ${s_arr[*]} ;
do
    col_index[$i]=$( head -n 1 $otu | awk -F '\t' -v s=$s '{ for(i=1;i<=NF;i++) if($i==s) print i }' ) ;
    i=$[$i+1] ;
done

# sort arr 对索引的数组进行排序
col=$(echo ${col_index[*]} | tr ' ' '\n' | sort -g | sed '/^$/d' | xargs) ;
IFS=' ' col_index=($col) ;

# 根据索引找出对应的列，放置在新的文件中
awk -F '\t' -v "index1=${col_index[*]}" '{col_len=split(index1,index2," ") ; { for(i=1;i<=col_len;i++) printf $index2[i]"\t" } print "" }' $otu > $otu_round ;
sed -i '1,$s/\t$//g' $otu_round ;


# 输出用于此次计算的样品名
echo use these samples: >> $out ;
head -n 1 $otu_round | cut -f2- | tr '\t' '\n' >> $out ;
echo '****************************************************' >> $out ;
# 输出每种菌的和病排序取出前10个菌
echo top10 are: >> $out ;
less $otu_round | sed '1d' | while read line ;
do
    name=$(echo $line | cut -f1) ;
    name_sum=$(echo $line | cut -f2- | awk '{sum=0}{for(i=1;i<=NF;i++) sum+=$i}{print sum }') ;
    echo -e $name'\t'$name_sum ;
done | sort -k2 -rg | head -n 10 | cut -f1 >> $out ;

}


touch $out
> $out

# first round
# 将第一轮的样品放到数组中
sample=$(grep -oh ',[0-9]\+.\+-.\+' all_sample.info | cut -f2 -d, | tr '\n' ',')
IFS=',' sample_arr=($sample)

echo first round result: >> $out
calculate_top10 "${sample_arr[*]}" $otu $otu.round1 $out

echo -e '\n\n--------------------------------------------------\n\n' >> $out
# last round
sample=$(grep ',[0-9]\+.\+-.\+,[0-9]\+.\+-.\+' all_sample.info | cut -f2- -d, | awk -F ',' '{for(i=1;i<=NF;i++) if($i!="") s=$i}{print s}' | tr '\n' ',')
IFS=',' sample_arr=($sample)

echo last round result: >> $out
calculate_top10 "${sample_arr[*]}" $otu $otu.roundlast $out

