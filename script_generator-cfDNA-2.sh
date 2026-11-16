#!/bin/bash
start=$(date +%s) #脚本启始时间
echo "开始时间："`date` 

#设置文件的路�?
sample_dir="/mnt/data2/lishengjing/20_plasma_numt/"
result_dir="/mnt/data2/lishengjing/20_plasma_numt/"

cd $result_dir
for i in $(cat ${sample_dir}/sample_name.txt)
do
    #mkdir ${i}
    echo "
    #!/bin/bash
    cd $result_dir/${i}
    mkdir tmp
    echo -e \"\\nsample:\"${i}
    #fastp -i $sample_dir/${i}/${i}_filtered_R1.fq.gz -o $result_dir/${i}/${i}_R1.good.fq.gz -I $sample_dir/${i}/${i}_filtered_R2.fq.gz -O $result_dir/${i}/${i}_R2.good.fq.gz  -h ${i}_fastp.html --length_required 50 -5 30 -M 30 -q 30 &>>${i}_analysis.log
    Rscript /mnt/hdd/usr/xiefanfan/work/NUMT/script/modified.mt.genome.R
    cat /mnt/hdd/ref_data/genomes/human/hg38/hg38_nochrM.fasta  modified.${i}.fa > ${i}.hg38.mt.fa
    bwa index ${result_dir}/${i}/${i}.hg38.mt.fa    
    bwa mem -t 10 -M -R '@RG\tID:$sample\tLB:mtDNA\tPL:ILLUMINA\tSM:$sample' ${i}.hg38.mt.fa ${i}_R1.good.fq.gz ${i}_R2.good.fq.gz 2>>${i}_analysis.log |samtools view -bS - -o ${i}.raw.bam #&& echo "bwa is finished "
    samtools index ${i}.raw.bam
    samtools view -f 4 -h ${i}.raw.bam > ${i}.unmapped.bam
    samtools view ${i}.unmapped.bam | awk '{print \$1}' > ${i}.unmapped.reads.txt
    java -Xmx10g -Djava.io.tmpdir=`pwd`/tmp -jar /mnt/hdd/softs/picard/picard-tools-1.81/SortSam.jar I=${i}.raw.bam O=${i}.sort.picard.bam SO=coordinate VALIDATION_STRINGENCY=SILENT 2>>${i}_analysis.log #&& echo "picard sort is finished " #&& date
    java -Xmx10g -Djava.io.tmpdir=`pwd`/tmp -jar /mnt/hdd/softs/picard/picard-tools-1.81/BuildBamIndex.jar INPUT=${i}.sort.picard.bam OUTPUT=${i}.sort.picard.bai VALIDATION_STRINGENCY=SILENT 2>>${i}_analysis.log #&& echo "picard index ${i}.sorted.bam is finished " #&& date
    java -Xmx10g -Djava.io.tmpdir=`pwd`/tmp -jar /mnt/hdd/softs/picard/picard-tools-1.81/MarkDuplicates.jar REMOVE_DUPLICATES=true I=${i}.sort.picard.bam O=${i}.rmdup.bam M=${i}.dup.metric VALIDATION_STRINGENCY=SILENT 2>>${i}_analysis.log #&& echo "picard mark duplicate is finished " #&& date 
    java -Xmx10g -Djava.io.tmpdir=`pwd`/tmp -jar /mnt/hdd/softs/picard/picard-tools-1.81/BuildBamIndex.jar INPUT=${i}.rmdup.bam  OUTPUT=${i}.rmdup.bai VALIDATION_STRINGENCY=SILENT 2>>${i}_analysis.log #&& echo "picard index ${i}.sorted.bam is finished " #&& date
    java -Xmx10g -Djava.io.tmpdir=`pwd`/tmp -jar /data/softs/GATK/GenomeAnalysisTK.jar -R /data/ref_data/modified_genome/hg19_mt.fa -T RealignerTargetCreator -o ${i}.realn.intervals -I ${i}.rmdup.bam 2>>${i}_analysis.log #&& echo " GATK RealignerTargetCreator  is finished " #&& date 
    java -Xmx10g -Djava.io.tmpdir=`pwd`/tmp -jar /data/softs/GATK/GenomeAnalysisTK.jar -R /data/ref_data/modified_genome/hg19_mt.fa -T IndelRealigner --maxReadsForRealignment 100000 -targetIntervals ${i}.realn.intervals -o ${i}.realn.bam -I ${i}.rmdup.bam 2>>${i}_analysis.log #&&  echo " GATK IndelRealigner is finished " #&& date 
    samtools index ${i}.realn.bam
    samtools view -b -h -F 256 ${i}.rmdup.bam chrM > ${i}.chrM.all.bam
    samtools view ${i}.chrM.all.bam | awk '{print \$1}' > ${i}.chrM.all.reads.txt
    samtools view -f 2 -F 256 -b -h ${i}.rmdup.bam chrM > ${i}.proper.chrM.bam
    samtools index ${i}.proper.chrM.bam
    samtools view -F 256 -h ${i}.proper.chrM.bam | grep -v \'chr1\' |grep -v \"chr2\" |grep -v \"chr3\" |grep -v \"chr4\" |grep -v \"chr5\" |grep -v \"chr6\" |grep -v \"chr7\" |grep -v \"chr8\" | grep -v \"chr9\" |grep -v \"chr10\" |grep -v \"chr11\" |grep -v \"chr12\" |grep -v \"chr13\" |grep -v \"chr14\" |grep -v \"chr15\" |grep -v \"chr19\"|grep -v \"chr20\" |grep -v \"chr21\" |grep -v \"chr22\" |grep -v \"chrX\" |grep -v \"chrY\" > ${i}.proper.NO2.chrM.sam
    samtools view ${i}.proper.NO2.chrM.sam | awk '{print \$1}' > ${i}.proper.NO2.chrM.reads.txt
    samtools view ${i}.chrM.all.bam |grep -e "chr1" -e "chr2" -e "chr3" -e "chr4" -e "chr5" -e "chr6" -e "chr7" -e "chr8" -e "chr9" -e "chr10" -e "chr11" -e "chr12" -e "chr13" -e "chr14" -e "chr15" -e "chr16" -e "chr17" -e "chr18" -e "chr19" -e "chr20" -e "chr21" -e "chr22" -e "chrX" -e "chrY" > ${i}.chrM.second.sam
    awk '{print \$1}' ${i}.chrM.second.sam > ${i}.second.chrM.reads.txt
    samtools view -b -h -F 256 ${i}.rmdup.bam chr1 chr2 chr3 chr4 chr5 chr6 chr7 chr8 chr9 chr10 chr11 chr12 chr13 chr14 chr15 chr16 chr17 chr18 chr19 chr20 chr21 chr22 chrX chrY > ${i}.nuclear.bam
    samtools index ${i}.nuclear.bam
    samtools view ${i}.nuclear.bam | awk '{print \$1}' > ${i}.nuclear.reads.txt
    samtools view -h -f 2 ${i}.nuclear.bam | grep -v "XA:Z:chrM" > ${i}.nuclear.proper.sam
    samtools view ${i}.nuclear.proper.sam | awk '{print \$1}' > ${i}.nuclear.proper.reads.txt
    samtools view -h ${i}.nuclear.bam | grep "XA:Z:chrM" > ${i}.nuclear.second.sam
    awk '{print \$1}' ${i}.nuclear.second.sam > ${i}.nuclear.second.reads.txt
    java -Xmx10g -Djava.io.tmpdir=`pwd`/tmp -jar /mnt/hdd/softs/picard/picard-tools-1.81/CollectInsertSizeMetrics.jar I=${i}.proper.chrM.bam O=${i}.proper.chrM.insertsize.txt H=${i}.proper.chrM.insertsize.pdf VALIDATION_STRINGENCY=LENIENT 2>>${sample}_analysis.log
    java -Xmx10g -Djava.io.tmpdir=`pwd`/tmp -jar /mnt/hdd/softs/picard/picard-tools-1.81/CollectInsertSizeMetrics.jar I=${i}.proper.NO2.chrM.sam O=${i}.proper.NO2.insertsize.txt H=${i}.proper.NO2.insertsize.pdf VALIDATION_STRINGENCY=LENIENT 2>>${sample}_analysis.log
    samtools view -H ${i}.raw.bam > ${i}.head.sam
    cat ${i}.head.sam ${i}.chrM.second.sam > ${i}.chrM.second-h.sam
    java -Xmx10g -Djava.io.tmpdir=`pwd`/tmp -jar /mnt/hdd/softs/picard/picard-tools-1.81/CollectInsertSizeMetrics.jar I=${i}.chrM.second-h.sam O=${i}.chrM.second.insertsize.txt H=${i}.chrM.second.insertsize.pdf VALIDATION_STRINGENCY=LENIENT 2>>${sample}_analysis.log
    java -Xmx10g -Djava.io.tmpdir=`pwd`/tmp -jar /mnt/hdd/softs/picard/picard-tools-1.81/CollectInsertSizeMetrics.jar I=${i}.nuclear.proper.sam O=${i}.nuclear.proper.insertsize.txt H=${i}.nuclear.proper.insertsize.pdf VALIDATION_STRINGENCY=LENIENT 2>>${sample}_analysis.log 
    samtools view ${i}.proper.chrM.bam > ${i}.mt.sam 
    samtools depth ${i}.proper.chrM.bam > ${i}.proper.chrM.depth
    samtools view -b ${i}.proper.NO2.chrM.sam > ${i}.proper.NO2.chrM.bam
    samtools depth ${i}.proper.NO2.chrM.bam > ${i}.proper.NO2.chrM.depth
    python /mnt/hdd/usr/lishengjing/Code/sam_to_pileup.py ${i}.mt.sam modified.${i}.fa > ${i}.old.pileup  #&& echo "sam_to_pileup.py is finished "
    perl /mnt/hdd/softs/DREEP/pileup_appended.pl ${i}.old.pileup > ${i}.pileup #&& echo "pileup_appended.pl is finished "
    /usr/bin/perl /mnt/hdd/softs/DREEP/filter_and_summary_v3.pl -i ${i}.pileup -d 3 -q 30 -m 20 -r 143 -s 5  > ${i}-hg38-all.ssp 2>>${i}_analysis.log #&& echo "filter_and_summary_v3.pl is finished "
    python /mnt/hdd/softs/DREEP/sam_to_pileup.py ${i}.proper.NO2.chrM.sam modified.${i}.fa > ${i}-2.old.pileup  #&& echo "sam_to_pileup.py is finished "
    perl /mnt/hdd/softs/DREEP/pileup_appended.pl ${i}-2.old.pileup > ${i}-2.pileup #&& echo "pileup_appended.pl is finished "
    /usr/bin/perl /mnt/hdd/softs/DREEP/filter_and_summary_v3.pl -i ${i}-2.pileup -d 3 -q 30 -m 20 -r 143 -s 5  > ${i}-2.ssp 2>>${i}_analysis.log #&& echo "filter_and_summary_v3.pl is finished "
    samtools view -h ${i}.chrM.all.bam | samtools sort -n | samtools fastq -1 ${i}.chrM.1_R1.fq -2 ${i}.chrM.2_R2.fq -s ${i}.chrM_singleton.fq -
    samtools view -h ${i}.nuclear.bam | samtools sort -n | samtools fastq -1 ${i}.nuclear.1_R1.fq -2 ${i}.nuclear.2_R2.fq -s ${i}.nuclear_singleton.fq -  
    java -Xmx10g -jar /mnt/hdd/guoshanshan/picard.jar FastqToSam F1=${i}.chrM_singleton.fq PL=illumina SM=${i} LB=${i} RG=${i} O=${i}.chrM_singleton.bam
    java -Xmx10g -jar /mnt/hdd/guoshanshan/picard.jar FastqToSam F1=${i}.nuclear_singleton.fq PL=illumina SM=${i} LB=${i} RG=${i} O=${i}.nuclear_singleton.bam
    cat ${i}.head.sam ${i}.nuclear.second.sam > ${i}.nuclear-h.second.sam
    samtools view -b -h ${i}.nuclear-h.second.sam > ${i}.nuclear.second.bam
    samtools merge -f ${i}.numt.bam ${i}.nuclear.second.bam ${i}.chrM_singleton.bam ${i}.nuclear_singleton.bam
    samtools view -h ${i}.numt.bam | samtools sort -n | samtools fastq -1 ${i}.numt.1_R1.fq -2 ${i}.numt.2_R2.fq -s ${i}.numt_singleton.fq -
    bwa index modified.${i}.fa
    bwa mem -t 10 -M -R '@RG\tID:$sample\tLB:mtDNA\tPL:ILLUMINA\tSM:$sample' modified.${i}.fa ${i}.numt.1_R1.fq ${i}.numt.2_R2.fq | samtools view -bS - -o ${i}.numt.raw.bam #&& echo "bwa is finished "
    samtools index ${i}.numt.raw.bam
    samtools view -f 4 -h ${i}.numt.raw.bam > ${i}.numt.unmapped.bam
    samtools view ${i}.numt.unmapped.bam | awk '{print \$1}' > ${i}.numt.unmapped.reads.txt
    java -Xmx10g -Djava.io.tmpdir=`pwd`/tmp -jar /mnt/hdd/softs/picard/picard-tools-1.81/SortSam.jar I=${i}.numt.raw.bam O=${i}.numt.sort.picard.bam SO=coordinate VALIDATION_STRINGENCY=SILENT 2>>${i}_analysis.log #&& echo "picard sort is finished " #&& date
    java -Xmx10g -Djava.io.tmpdir=`pwd`/tmp -jar /mnt/hdd/softs/picard/picard-tools-1.81/BuildBamIndex.jar INPUT=${i}.numt.sort.picard.bam OUTPUT=${i}.numt.sort.picard.bai VALIDATION_STRINGENCY=SILENT 2>>${i}_analysis.log #&& echo "picard index ${i}.sorted.bam is finished " #&& date
    java -Xmx10g -Djava.io.tmpdir=`pwd`/tmp -jar /mnt/hdd/softs/picard/picard-tools-1.81/MarkDuplicates.jar REMOVE_DUPLICATES=true I=${i}.numt.sort.picard.bam O=${i}.numt.rmdup.bam M=${i}.dup.metric VALIDATION_STRINGENCY=SILENT 2>>${i}_analysis.log #&& echo "picard mark duplicate is finished " #&& date
    java -Xmx10g -Djava.io.tmpdir=`pwd`/tmp -jar /mnt/hdd/softs/picard/picard-tools-1.81/BuildBamIndex.jar INPUT=${i}.numt.rmdup.bam  OUTPUT=${i}.numt.rmdup.bai VALIDATION_STRINGENCY=SILENT 2>>${i}_analysis.log #&& echo "picard index ${i}.sorted.bam is finished " #&& date
    perl /mnt/hdd/softs/mt_analysis/fetch_mt.pl ${i}.numt.rmdup.bam |samtools view -bS - -o ${i}.numt.mt.bam
    samtools view ${i}.numt.mt.bam > ${i}.numt.mt.sam
    python /mnt/hdd/softs/DREEP/sam_to_pileup.py ${i}.numt.mt.sam modified.${i}.fa > ${i}.numt.old.pileup  #&& echo "sam_to_pileup.py is finished "
    perl /mnt/hdd/softs/DREEP/pileup_appended.pl ${i}.numt.old.pileup > ${i}.numt.pileup #&& echo "pileup_appended.pl is finished "
    /usr/bin/perl /mnt/hdd/softs/DREEP/filter_and_summary_v3.pl -i ${i}.numt.pileup -d 3 -q 30 -m 20 -r 143 -s 5  > ${i}.numt.ssp 2>>${i}_analysis.log #&& echo "filter_and_summary_v3.pl is finished "
    rm ${i}-2.old.pileup
    rm ${i}-2.pileup

    " > ${i}/${i}.mt_analysis.sh
done


#for循环并行运算
tmp_file="/tmp/$$.fifo"
mkfifo $tmp_file
exec 6<>$tmp_file   
rm -f $tmp_file
thread=14   #设置并行运算的数�?           
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
            bash *mt_analysis.sh
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
