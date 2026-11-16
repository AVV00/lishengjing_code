#!/bin/bash
start=$(date +%s) #脚本启始时间
echo "开始时间："`date` 

#设置文件的路�?
sample_dir="/mnt/data2/lishengjing/2_o_10_HCC/DNA/"
result_dir="/mnt/data2/lishengjing/2_o_10_HCC/DNA/"

cd $result_dir/${i}
for i in $(cat ${sample_dir}/sample_name.txt)
do
    mkdir ${i}
    echo "
	#!/bin/bash
    cd $result_dir/${i}
    mkdir tmp
    echo -e \"\\nsample:\"${i}
    samtools view -h $sample_dir/${i}/${i}.1.bam | samtools sort -n | samtools fastq -1 ${i}.1_R1.fq -2 ${i}.1_R2.fq -s $result_dir/${i}/${i}.1_singleton.fq -
    bwa mem -M -t 30 -K 10000000 -R '@RG\tID:${i}\tLB:mtDNA\tPL:ILLUMINA\tSM:${i}' /mnt/hdd/usr/xiefanfan/work/NUMT/reference/numt_combine_uniq/Calabrese_Dayama_Smart_HCC_GC_chm13_Numts.uniq.fa ${i}.1_R1.fq ${i}.1_R2.fq | samtools view -bS - -o ${i}.numt.bam
    samtools flagstat ${i}.numt.bam > ${i}.numt.bam.txt
    
 
        " > ${i}/${i}.numt_analysis.sh
done


#for循环并行运算
tmp_file="/tmp/$$.fifo"
mkfifo $tmp_file
exec 6<>$tmp_file   
rm -f $tmp_file
thread=5   #设置并行运算的数�?           
for ((i=0;i<thread;i++))    
do
    echo >&6
done



#第二步：运行脚本
#sh $code_file_dir/run_task.sh  
#!/bin/bash
function feth_file(){
    for file in $(cat ${sample_dir}/sample_name.txt)
    do  
    read -u6
   {
        df=$1"/"$file
        if [ -d $df ]
        then 
            cd $df
            bash *numt_analysis.sh
            cd ..
        fi
        echo >&6
   }&
    done
    wait        # 等待所有的后台子进程结�?    exec 6>&-   # 关闭fd6          
}
feth_file $result_dir  
rm -rf $result_dir/tmp


end=$(date +%s) #脚本终止时间
take=$(( end - start ))
h=$(( take / 3600 ))
m=$((( take - 3600 * h ) / 60 ))
s=$((( take - 3600 * h - 60 * m )))
echo "结束时间�?`date` 
echo "脚本运行完毕，用�?${h} 小时 ${m} 分钟 ${s} �?
