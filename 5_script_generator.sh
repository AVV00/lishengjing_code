#!/bin/bash
shanshan@localhost numtref-1]$ vi i
start=$(date +%s) #脚本启始时间
echo "开始时间："`date` 

#设置文件的路�?
sample_dir="/mnt/data2/lishengjing/2_o_10_HCC/DNA/"
result_dir="/mnt/data2/lishengjing/2_o_10_HCC/DNA/"


cd $result_dir
for i in $(cat ${result_dir}/sample_name.txt)
do
    #mkdir ${i}
    echo "
    #!/bin/bash
    cd $result_dir/${i}
    mkdir tmp
    echo -e \"\\nsample:\"${i}
    java -Xmx10g -Djava.io.tmpdir=/mnt/data/guoshanshan/numt/20221027plasma/tmp -jar /mnt/hdd/guoshanshan/picard.jar FastqToSam F1=${i}.1_singleton.fq PL=illumina SM=${i} LB=${i} RG=${i} O=${i}.u.bam
    samtools merge -f ${i}.0.u.bam ${i}.u.bam ${i}.0.bam
    samtools merge -f ${i}.all.bam ${i}.0.u.bam ${i}.0.numt.rm.bam
    samtools flagstat ${i}.all.bam > ${i}.all.bam.stat
    samtools view -h ${i}.all.bam | samtools sort -n | samtools fastq -1 ${i}.all_R1.fq -2 ${i}.all_R2.fq -s $result_dir/${i}/${i}.all_singleton.fq -
    bwa mem -M -t 30 -K 10000000 -R '@RG\tID:${i}\tLB:mtDNA\tPL:ILLUMINA\tSM:${i}' modified.${i}.fa ${i}.all_R1.fq ${i}.all_R2.fq |samtools view -bS - -o ${i}.0.mapped.bam
    samtools flagstat ${i}.0.mapped.bam > ${i}.0.mapped.stat
    java -Xmx10g -Djava.io.tmpdir=/mnt/data/guoshanshan/numt/20221027plasma/tmp -jar /mnt/hdd/softs/picard/picard-tools-1.81/SortSam.jar I=${i}.0.mapped.bam O=${i}.0.sort.picard.bam SO=coordinate VALIDATION_STRINGENCY=SILENT 2>>${i}_analysis.log #&& echo picard sort is finished  #&& date 
    samtools index ${i}.0.sort.picard.bam
    samtools view ${i}.0.sort.picard.bam > ${i}.0.sort.picard.sam
    samtools depth -m 0 ${i}.0.sort.picard.bam > ${i}.numt.depth
    python /mnt/hdd/softs/DREEP/sam_to_pileup.py ${i}.0.sort.picard.sam modified.${i}.fa > ${i}.0.old.pileup  #&& echo "sam_to_pileup.py is finished "
    perl /mnt/hdd/softs/DREEP/pileup_appended.pl ${i}.0.old.pileup > ${i}.0.pileup #&& echo "pileup_appended.pl is finished "
    /usr/bin/perl /mnt/hdd/softs/DREEP/filter_and_summary_v3.pl -i ${i}.0.pileup -d 3 -q 30 -m 20 -r 143 -s 5  > ${i}.0.ssp 2>>${i}_analysis.log #&& echo "filter_and_summary_v3.pl is finished "
    rm -rf tmp
        " > ${i}/${i}.numt_mismatch.sh
done


#for循环并行运算
tmp_file="/tmp/$$.fifo"
mkfifo $tmp_file
exec 6<>$tmp_file   
rm -f $tmp_file
thread=10   #设置并行运算的数�?           
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
            bash *.numt_mismatch.sh
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
