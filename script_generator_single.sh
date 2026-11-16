#!/bin/bash
export PATH="/usr/local/bin/:$PATH"
start=$(date +%s) #脚本启始时间
echo "开始时间："`date` 

#设置文件的路�?#run_dir="/mnt/hdd/usr/xiefanfan/tools/mtDNA_pipeline/demo_v1/Combine_Analysis_rCRS-hg19-DNA_V1"
#result_dir="/mnt/hdd/usr/xiefanfan/tools/mtDNA_pipeline/demo_v1/"

result_dir=$1
run_dir=$2

#echo -e \"\\nsample:\t$data_type\t$sample\"
#### write the very sample analysis script 
cat ${run_dir}/input.info.txt|while read line
do
    arrary=(${line//})
    sample=${arrary[0]}
    barcode_R1=${arrary[1]}
    barcode_R2=${arrary[2]}
    data_type=${arrary[3]}
    analysis_type=${arrary[4]}
    mkdir -p $result_dir/$data_type/$analysis_type/$sample/ 
    echo "#!/bin/bash
    /usr/bin/python /mnt/hdd/usr/lishengjing/Code/Split_single_barcode.v1.py --samp ${sample} --samp_barcode1 ${barcode_R1} --samp_type ${data_type} --analysis_type ${analysis_type} --outdir ${result_dir} 
    cd $result_dir/$data_type/$analysis_type/$sample/ 
    mkdir $result_dir/$data_type/$analysis_type/$sample/tmp
    /mnt/hdd/usr/jiaohuanmin/home/jiaohm/Tool/anaconda3/bin/fastp -i ${sample}_filtered_R1.fq.gz -o ${sample}_R1.good.fq.gz -h ${sample}_fastp.html --length_required 50 -5 30 -M 30 -q 30 &>>${sample}_analysis.log    
    /mnt/hdd/usr/jiaohuanmin/home/jiaohm/bwa-0.7.17/bwa mem -t 10 -M -R '@RG\tID:$sample\tLB:mtDNA\tPL:ILLUMINA\tSM:$sample' /mnt/hdd/ref_data/modified_genome/hg19_mt.fa ${sample}_R1.good.fq.gz  2>>${sample}_analysis.log |samtools view -bS - -o ${sample}.raw.bam #&& echo "bwa is finished " 
    java -Xmx10g -Djava.io.tmpdir=$result_dir/$data_type/$analysis_type/$sample/tmp -jar /mnt/hdd/softs/picard/picard-tools-1.81/SortSam.jar I=${sample}.raw.bam O=${sample}.sort.picard.bam SO=coordinate VALIDATION_STRINGENCY=SILENT 2>>${sample}_analysis.log #&& echo "picard sort is finished " #&& date 
    java -Xmx10g -Djava.io.tmpdir=$result_dir/$data_type/$analysis_type/$sample/tmp -jar /mnt/hdd/softs/picard/picard-tools-1.81/BuildBamIndex.jar INPUT=${sample}.sort.picard.bam OUTPUT=${sample}.sort.picard.bam.bai VALIDATION_STRINGENCY=SILENT 2>>${sample}_analysis.log #&& echo "picard index ${sample}.sorted.bam is finished " #&& date
    java -Xmx10g -Djava.io.tmpdir=$result_dir/$data_type/$analysis_type/$sample//tmp -jar /mnt/hdd/softs/picard/picard-tools-1.81/MarkDuplicates.jar REMOVE_DUPLICATES=true I=${sample}.sort.picard.bam O=${sample}.rmdup.bam M=${sample}.dup.metric VALIDATION_STRINGENCY=SILENT 2>>${sample}_analysis.log #&& echo "picard mark duplicate is finished " #&& date 
    java -Xmx10g -Djava.io.tmpdir=$result_dir/$data_type/$analysis_type/$sample/tmp -jar /mnt/hdd/softs/picard/picard-tools-1.81/BuildBamIndex.jar INPUT=${sample}.rmdup.bam OUTPUT=${sample}.rmdup.bam.bai VALIDATION_STRINGENCY=SILENT 2>>${sample}_analysis.log #&& echo "picard index ${sample}.sorted.bam is finished " #&& date
    java -Xmx10g -Djava.io.tmpdir=$result_dir/$data_type/$analysis_type/$sample/tmp -jar /mnt/hdd/softs/GATK/GenomeAnalysisTK.jar -R /mnt/hdd/ref_data/modified_genome/hg19_mt.fa -T RealignerTargetCreator -o ${sample}.realn.intervals -I ${sample}.rmdup.bam 2>>${sample}_analysis.log #&& echo " GATK RealignerTargetCreator is finished " #&& date 
    java -Xmx10g -Djava.io.tmpdir=$result_dir/$data_type/$analysis_type/$sample/tmp -jar /mnt/hdd/softs/GATK/GenomeAnalysisTK.jar -R /mnt/hdd/ref_data/modified_genome/hg19_mt.fa -T IndelRealigner --maxReadsForRealignment 100000 -targetIntervals ${sample}.realn.intervals -o ${sample}.realn.bam -I ${sample}.rmdup.bam 2>>${sample}_analysis.log #&&  echo " GATK IndelRealigner is finished " #&& date 
    /mnt/hdd/usr/xiefanfan/tools/samtools-1.15.1/bin/samtools index ${sample}.realn.bam  
    /usr/bin/perl /mnt/hdd/usr/lishengjing/Code/fetch_mt_single.pl ${sample}.realn.bam |samtools view -bS - -o ${sample}.mt.bam  2>>${sample}_analysis.log #&& echo "fetch_mt.pl is finished "
    /mnt/hdd/usr/xiefanfan/tools/samtools-1.15.1/bin/samtools index ${sample}.mt.bam 
    /mnt/hdd/usr/xiefanfan/tools/samtools-1.15.1/bin/samtools depth -m 0 ${sample}.mt.bam > ${sample}.depth
    /mnt/hdd/usr/xiefanfan/tools/samtools-1.15.1/bin/samtools view ${sample}.mt.bam > ${sample}.mt.sam 
    /usr/bin/python /mnt/hdd/softs/DREEP/sam_to_pileup.py ${sample}.mt.sam /mnt/hdd/ref_data/modified_genome/human_mtDNA.fasta > ${sample}.old.pileup  #&& echo "sam_to_pileup.py is finished "
    /usr/bin/perl /mnt/hdd/softs/DREEP/pileup_appended.pl ${sample}.old.pileup > ${sample}.pileup #&& echo "pileup_appended.pl is finished "
    /usr/bin/perl /mnt/hdd/usr/lishengjing/Code/filter_and_summary_v3.pl -i ${sample}.pileup -d 3 -q 30 -m 20 -r 143 -s 5  > ${sample}.ssp 2>>${sample}_analysis.log #&& echo "filter_and_summary_v3.pl is finished "
    rm ${sample}.old.pileup
    rm ${sample}.mt.sam
    gzip -f ${sample}.pileup
    java -Xmx10g -Djava.io.tmpdir=$result_dir/$data_type/$analysis_type/$sample/tmp -jar /mnt/hdd/softs/picard/picard-tools-1.81/CollectInsertSizeMetrics.jar I=${sample}.realn.bam O=${sample}.insertsize.txt H=${sample}.insertsize.pdf VALIDATION_STRINGENCY=LENIENT 2>>${sample}_analysis.log
    java -Xmx10g -Djava.io.tmpdir=$result_dir/$data_type/$analysis_type/$sample/tmp -jar /mnt/hdd/softs/picard/picard-tools-1.81/CollectInsertSizeMetrics.jar I=${sample}.mt.bam O=${sample}.insertsize.mt.txt H=${sample}.insertsize.mt.pdf VALIDATION_STRINGENCY=LENIENT 2>>${sample}_analysis.log  #&&echo "CollectInsertSizeMetrics is finished "
    #rm -rf tmp
    " > $result_dir/$data_type/$analysis_type/$sample/${sample}_analysis.sh
done

### submit the script in parallel

mkdir -p ./tmp
tmp_file="/tmp/$$.fifo"
mkfifo $tmp_file
exec 6<>$tmp_file   
rm -f $tmp_file
thread=10 #设置并行运算的数�?          
for ((i=0;i<thread;i++))    
do
    echo >&6
done



#第二步：运行脚本
#sh $code_file_dir/run_task.sh  
#!/bin/bash
function feth_file(){
    for df in `ls -d $result_dir/*/*/*/`
    do  
    read -u6
   {
        if [ -f $df/*_analysis.sh ]
        then 
            cd $df
            bash *.sh
        fi
        echo >&6
   }&
    done
    wait        # 等待所有的后台子进程结�?  
    exec 6>&-   # 关闭fd6          
}
feth_file $result_dir
rm -rf $run_dir/tmp 
rm -rf $result_dir/*/*/*/*tmp


end=$(date +%s) #脚本终止时间
take=$(( end - start ))
h=$(( take / 3600 ))
m=$((( take - 3600 * h ) / 60 ))
s=$((( take - 3600 * h - 60 * m )))
echo "结束时间:"`date` 
echo "脚本运行完毕，用�?{h} 小时 ${m} 分钟 ${s}�?
