#!/bin/bash
start=$(date +%s) #脚本启始时间
echo "开始时间："`date` 

#设置文件的路径 
#sample_dir="/mnt/data1/Seq_data/20230322/CRC_Plasma_DOU_mtDNA-CAP/Analysis_private-mtDNA_V1"
result_dir="/mnt/data2/Seq_data/20240423/HCS_Tissue_DOU_mtDNA-CAP/Analysis_private-mtDNA_V1"
fasta_path="/mnt/data2/Seq_data/20240423/Combine_Analysis_rCRS-hg19-DNA_V1/fasta"
source_path="/mnt/data2/Seq_data/20240423/HCS_Tissue_DOU_mtDNA-CAP/Analysis_rCRS-hg19-DNA_V1"


mkdir ${result_dir}
cd ${result_dir}
cp ${source_path}/sample_name.txt .
for i in $(cat ${result_dir}/sample_name.txt)
do
    echo ${i}
    mkdir ${i} 
    echo "
	#!/bin/bash
    cd ${result_dir}/${i}
    echo -e \"\\nsample:\"${i}
    #cat ${path1}/${i}/${i}_R1.good.fq.gz ${path2}/${i}/${i}_R1.good.fq.gz > ./${i}_R1.good.fq.gz
    #cat ${path1}/${i}/${i}_R2.good.fq.gz ${path2}/${i}/${i}_R2.good.fq.gz > ./${i}_R2.good.fq.gz
    cp ${fasta_path}/${i}.fa .
    Rscript /mnt/hdd/usr/xiefanfan/work/NUMT/script/modified.mt.genome.R
    bwa index modified.${i}.fa    
    bwa mem -t 10 -M -R '@RG\tID:${i}\tLB:mtDNA\tPL:ILLUMINA\tSM:${i}' ${result_dir}/${i}/modified.${i}.fa ${source_path}/${i}/${i}_R1.good.fq.gz ${source_path}/${i}/${i}_R2.good.fq.gz 2>>${i}_private_analysis.log | samtools view -bS - -o ${result_dir}/${i}/${i}.private.raw.bam #&& echo bwa is finished  
    java -Xmx10g -Djava.io.tmpdir=`pwd`/tmp -jar /mnt/hdd/softs/picard/picard-tools-1.81/SortSam.jar I=${i}.private.raw.bam O=${i}.private.sort.picard.bam SO=coordinate VALIDATION_STRINGENCY=SILENT 2>>${i}_private_analysis.log #&& echo picard sort is finished  #&& date 
    java -Xmx10g -Djava.io.tmpdir=`pwd`/tmp -jar /mnt/hdd/softs/picard/picard-tools-1.81/BuildBamIndex.jar INPUT=${i}.private.sort.picard.bam OUTPUT=${i}.private.sort.picard.bai VALIDATION_STRINGENCY=SILENT 2>>${i}_private_analysis.log #&& echo picard index ${i}.sorted.bam is finished  #&& date
    java -Xmx10g -Djava.io.tmpdir=`pwd`/tmp -jar /mnt/hdd/softs/picard/picard-tools-1.81/MarkDuplicates.jar REMOVE_DUPLICATES=true I=${i}.private.sort.picard.bam O=${i}.private.rmdup.bam M=${i}.private.dup.metric VALIDATION_STRINGENCY=SILENT 2>>${i}_private_analysis.log #&& echo picard mark duplicate is finished  #&& date 
    java -Xmx10g -Djava.io.tmpdir=`pwd`/tmp -jar /mnt/hdd/softs/picard/picard-tools-1.81/BuildBamIndex.jar INPUT=${i}.private.rmdup.bam  OUTPUT=${i}.private.rmdup.bam.bai VALIDATION_STRINGENCY=SILENT 2>>${i}_private_analysis.log #&& echo picard index ${i}.sorted.bam is finished  #&& date
    #samtools flagstat ${i}.private.raw.bam > ${i}.private.raw.stat
    samtools flagstat ${i}.private.rmdup.bam > ${i}.private.rmdup.stat
    perl /mnt/hdd/softs/mt_analysis/fetch_mt.pl ${i}.private.rmdup.bam |samtools view -bS - -o ${i}.private.mt.bam  2>>${i}_private_analysis.log #&& echo "fetch_mt.pl is finished "
    /mnt/hdd/usr/xiefanfan/tools/samtools-1.15.1/bin/samtools index ${i}.private.mt.bam 
    /mnt/hdd/usr/xiefanfan/tools/samtools-1.15.1/bin/samtools depth -m 0 ${i}.private.mt.bam > ${i}.private.depth
    perl /mnt/hdd/usr/jiaohuanmin/home/jiaohm/Tools/mtDNA_pipeline/routine_pipeline/02_get.sam.v01.pl -sample_name ${i}
    java -Xmx10g -Djava.io.tmpdir=`pwd`/tmp -jar /mnt/hdd/softs/picard/picard-tools-1.81/CollectInsertSizeMetrics.jar I=${i}.mis.10.bam O=${i}.mis.10.insertsize.txt H=${i}.mis.10.insertsize.pdf VALIDATION_STRINGENCY=LENIENT 2>>${i}_private_analysis.log
    rm -rf tmp
 
        " >> ${result_dir}/${i}/${i}_private.analysis.sh
    
done


#for循环并行运算
tmp_file="/tmp/$$.fifo"
mkfifo $tmp_file
exec 6<>$tmp_file   
rm -f $tmp_file
thread=10   #设置并行运算的数量            
for ((i=0;i<thread;i++))    
do
    echo >&6
done



#第二步：运行脚本
#sh $code_file_dir/run_task.sh  
#!/bin/bash
function feth_file(){
    for file in $(cat ${result_dir}/sample_name.txt)
    do  
    read -u6
   {
        df=$1"/"$file
        if [ -d $df ]
        then 
            cd $df
            bash *_private.analysis.sh
            cd ..
        fi
        echo >&6
   }&
    done
    wait        # 等待所有的后台子进程结束
    exec 6>&-   # 关闭fd6          
}
feth_file $result_dir  
rm -rf $result_dir/tmp


end=$(date +%s) #脚本终止时间
take=$(( end - start ))
h=$(( take / 3600 ))
m=$((( take - 3600 * h ) / 60 ))
s=$((( take - 3600 * h - 60 * m )))
echo "结束时间："`date` 
echo "脚本运行完毕，用时 ${h} 小时 ${m} 分钟 ${s} 秒"
