#!/bin/bash


#代码说明书
#创建时间：2021.10.30 by sulp
#修改时间：2021.11.04 by sulp
#修改时间：2021.04.23 by sulp (1) 修改get_output_true_file.R  (2) 添加突变阈值的参数，指定要使用的特定阈值的hetro和homo文件。(3) 修改工作路径出错 sample_dir 
#修改时间：2021.04.24 by sulp (1) 修改get_total_output_features.R  (2)删除当前路径下之前生成的结果文件(output_true_0.1 、output_feature_0.1 、 output_feature_0.1.tmp)

#用    途：利用机器学习模型识别低频真突变 特征提取的过程
#输    入：样式1：样本的(1) mt.bam (2) mt.bam.bai (3) hetro.txt (4) homo.txt 4个文件
#                 [所有的文件放在同一个文件夹路径下]
#          样式2：样本文件夹已经创建好，每个样本文件夹中都包含上述的4个文件。
#输    出：每个样本的output_feature_0.1 [0.1为突变阈值，和提供的hetro和homo文件一致]
#过    程：(1) 创建样本文件夹
#          (2) 特征提取前准备6列样本中突变位点的信息
#          (3) 特征的提取
#          (4) 特征的汇总

#使    用：bash /home/suliping/code/get_feature.sh path 2 10 [path表示样本的文件路径; 2表示输入的低频突变的最大突变频率; 10表示并行运算的进程数]

start=$(date +%s) #脚本启始时间
echo "开始时间："`date` 


sample_dir=$1         #样本路径
cutoff=$2             #cutoff表示待提取特征的最高突变频率,单位(%)
thread=$3             #提取特征的python 在shell中并行运算的并行数量            
vaf=$4                #输入文件hetro和homo的突变阈值

#删除当前路径下之前生成的结果文件
cd ${sample_dir}
find -name "output_true_${vaf}" -exec rm {} \;
find -name "output_feature_${vaf}" -exec rm {} \;
find -name "output_feature_${vaf}.tmp" -exec rm {} \;

#(1)创建样本文件夹
sample_dir=`pwd`
if [ ! -f sample_name.txt ];then
    find -name "*.bam" | grep ".mt.no.softclip.bam$" | sed 's/.mt.no.softclip.bam//g' | sed 's#.*/##' >sample_name.txt
fi
for i in $(cat sample_name.txt)
do  
    if [ ! -d ${i} ];then
        mkdir -p ${i}
        mv ${i}.* ${sample_dir}/${i}
    fi    
done


#(2)特征提取前准备6列样本中突变位点的信息
echo "get_output_true_file.R starts at `date`"
#Rscript /home/suliping/code/get_output_true_file.R ${sample_dir} ${cutoff} ${vaf}
for i in $(cat sample_name.txt)
do
    echo ${i}
    echo ${cutoff}
    echo ${vaf}
    python3 /mnt/hdd/usr/lishengjing/Code/get_output_true_file.py ${sample_dir}/${i} ${cutoff} ${vaf}
done

#(3) 特征的提取[并行运算]
echo "get_feature.py starts at `date`"
tmp_file="/tmp/$$.fifo"
mkfifo $tmp_file
exec 6<>$tmp_file   
rm -f $tmp_file
for ((i=0;i<thread;i++))    
do
    echo >&6
done

for i in $(cat ${sample_dir}/sample_name.txt)
do 
read -u6
{
    python3 /mnt/hdd/usr/lishengjing/Code/get_feature_mtDNApipe.py ${sample_dir} ${i}
    echo >&6
}&
done
wait        # 等待所有的后台子进程结束
exec 6>&-   # 关闭fd6  


#(4) 汇总特征至一个文件夹，输出Total_output_feature_vaf.txt 
echo "get_total_output_features.R starts at `date`"
Rscript /home/suliping/code/get_total_output_features.R ${sample_dir} ${cutoff}

end=$(date +%s) #脚本终止时间
take=$(( end - start ))
h=$(( take / 3600 ))
m=$((( take - 3600 * h ) / 60 ))
s=$((( take - 3600 * h - 60 * m )))
echo "结束时间："`date` 
echo "脚本运行完毕，用时 ${h} 小时 ${m} 分钟 ${s} 秒"
