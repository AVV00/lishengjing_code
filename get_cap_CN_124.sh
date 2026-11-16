#!/bin/bash

#设置路径
run_dir=${1}        #"/data/liuyang-data/wangmengxin-20201205"
result_dir=${2}              #"/data/liuyang-data/wangmengxin-20201205"

#创建文件夹
mkdir ${result_dir}/neicandepth/
mkdir ${result_dir}/neicandepth/depth1
mkdir ${result_dir}/neicandepth/depth2
#mkdir ${result_dir}/neicandepth/depth3
mkdir ${result_dir}/neicandepth/depth4
#mkdir ${result_dir}/neicandepth/depth5
#mkdir ${result_dir}/neicandepth/depth6




tmp_file="/tmp/$$.fifo"
mkfifo $tmp_file
exec 6<>$tmp_file   
rm -f $tmp_file
thread=6            
for ((i=0;i<thread;i++))    
do
    echo >&6
done

#计算核基因组的depth
#cat ${result_dir}/input.info.txt|while read line
for i in $(cat ${result_dir}/input.info.txt|cut -f1)
do
read -u6
{
    samtools depth -m 0 -b /mnt/hdd/neican/tiqu1.bed ${run_dir}/*/Analysis_rCRS-hg19-DNA_V1/${i}/${i}.realn.bam > ${result_dir}/neicandepth/depth1/${i}.realn.bam.txt
    samtools depth -m 0 -b /mnt/hdd/neican/tiqu2.bed ${run_dir}/*/Analysis_rCRS-hg19-DNA_V1/${i}/${i}.realn.bam > ${result_dir}/neicandepth/depth2/${i}.realn.bam.txt
    #samtools depth -m 0 -b /mnt/hdd/neican/tiqu3.bed ${sample_dir}/${i}/${i}.realn.bam > ${result_dir}/neicandepth/depth3/${i}.realn.bam.txt
    samtools depth -m 0 -b /mnt/hdd/neican/tiqu4.bed ${run_dir}/*/Analysis_rCRS-hg19-DNA_V1/${i}/${i}.realn.bam > ${result_dir}/neicandepth/depth4/${i}.realn.bam.txt
    #samtools depth -m 0 -b /mnt/hdd/neican/tiqu5.bed ${sample_dir}/${i}/${i}.realn.bam > ${result_dir}/neicandepth/depth5/${i}.realn.bam.txt
    #samtools depth -m 0 -b /mnt/hdd/neican/tiqu6.bed ${run_dir}/*/Analysis_rCRS-hg19-DNA_V1/${i}/${i}.realn.bam > ${result_dir}/neicandepth/depth6/${i}.realn.bam.txt
    cat ${result_dir}/neicandepth/depth1/${i}.realn.bam.txt | awk '{sum+=$3} END {print "'${i}'", sum/NR}' OFS="\t"  >> ${result_dir}/neicandepth/1.txt
    cat ${result_dir}/neicandepth/depth2/${i}.realn.bam.txt | awk '{sum+=$3} END {print "'${i}'", sum/NR}' OFS="\t"  >> ${result_dir}/neicandepth/2.txt
    #cat ${result_dir}/neicandepth/depth3/${i}.realn.bam.txt | awk '{sum+=$3} END {print "'${i}'", sum/NR}' OFS="\t"  >> ${result_dir}/neicandepth/3.txt
    cat ${result_dir}/neicandepth/depth4/${i}.realn.bam.txt | awk '{sum+=$3} END {print "'${i}'", sum/NR}' OFS="\t"  >> ${result_dir}/neicandepth/4.txt
    #cat ${result_dir}/neicandepth/depth5/${i}.realn.bam.txt | awk '{sum+=$3} END {print "'${i}'", sum/NR}' OFS="\t"  >> ${result_dir}/neicandepth/5.txt
    #cat ${result_dir}/neicandepth/depth6/${i}.realn.bam.txt | awk '{sum+=$3} END {print "'${i}'", sum/NR}' OFS="\t"  >> ${result_dir}/neicandepth/6.txt
    echo >&6
}&
done
wait        
exec 6>&-            


#输出拷贝数的文件
echo -e 'sample'\\t'mt_depth'\\t'hg19_depth(1 2 6)'\\t'copy number'\\t >>${result_dir}/neicandepth/copy_number.txt
#cat ${result_dir}/input.info.txt|while read line
for i in $(cat ${result_dir}/input.info.txt|cut -f1)
do
    mt_depth=$(samtools depth -m 0 ${run_dir}/*/Analysis_rCRS-hg19-DNA_V1/${i}/${i}.mt.bam |awk '{sum+=$3} END {print sum/16569}')
    depth1=$(cat ${result_dir}/neicandepth/depth1/${i}.realn.bam.txt | awk '{sum+=$3} END {print sum/NR}')
    depth2=$(cat ${result_dir}/neicandepth/depth2/${i}.realn.bam.txt | awk '{sum+=$3} END {print sum/NR}')
    depth4=$(cat ${result_dir}/neicandepth/depth4/${i}.realn.bam.txt | awk '{sum+=$3} END {print sum/NR}')
    hg_depth=$(echo "scale=4; ($depth1+$depth2+$depth4)/3 "| bc)
    CN=$(echo "scale=4;$mt_depth*2/$hg_depth"| bc)
    echo -e ${i}\\t$mt_depth\\t$hg_depth\\t$CN\\t >>${result_dir}/neicandepth/copy_number.txt
done

