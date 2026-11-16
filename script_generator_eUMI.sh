#!/bin/bash
start=$(date +%s) #脚本启始时间
echo "开始时间："`date` 

#设置文件的路径 
sample_dir="/mnt/data2/lishengjing/tissue_10_eUMI/"
result_dir="/mnt/data2/lishengjing/tissue_10_eUMI/"



cd $result_dir
for i in $(cat ${sample_dir}/sample_name.txt)
do
    #mkdir ${i}
    echo "
    #!/bin/bash
    cd $result_dir/${i}
    mkdir tmp
    echo -e \"\\nsample:\"${i}
    java -Xmx10g -Djava.io.tmpdir=`pwd`/tmp -jar /mnt/hdd/softs/picard/picard-tools-1.81/SortSam.jar I=${i}.raw.bam O=${i}.sort.picard.bam SO=coordinate VALIDATION_STRINGENCY=SILENT 2>>${i}_analysis.log #&& echo "picard sort is finished " #&& date 
    java -Xmx10g -Djava.io.tmpdir=`pwd`/tmp -jar /mnt/hdd/softs/picard/picard-tools-1.81/BuildBamIndex.jar INPUT=${i}.sort.picard.bam OUTPUT=${i}.sort.picard.bai VALIDATION_STRINGENCY=SILENT 2>>${i}_analysis.log #&& echo "picard index ${i}.sorted.bam is finished " #&& date
    perl /mnt/hdd/softs/mt_analysis/fetch_mt.pl ${i}.sort.picard.bam |samtools view -bS - -o ${i}.mt.bam  2>>${i}_analysis.log #&& echo "fetch_mt.pl is finished "
    samtools index ${i}.mt.bam 
    samtools depth -m 0 ${i}.mt.bam > ${i}.depth

    python3 /mnt/hdd/usr/lishengjing/Code/mito-Consensus-noBarcode.py ${i} ${i}.mt.bam ${result_dir} 30
    rm -rf tmp
        " > ${i}/${i}_analysis.sh
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
    for file in $(cat ${sample_dir}/sample_name.txt)
    do  
    read -u6
   {
        df=$1"/"$file
        if [ -d $df ]
        then 
            cd $df
            bash *.sh
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

