#!/bin/bash
work_dir=$1
cutoff=$2
cd ${work_dir}
mkdir mutation_${cutoff}
cp ./*/*_${cutoff}.txt mutation_${cutoff}
sh /mnt/hdd/usr/lishengjing/Code/SOB_merge_txt_${cutoff}.sh ${work_dir}/mutation_${cutoff} ${work_dir}/SOB_v1/input_mutation_file
/usr/bin/perl /mnt/hdd/usr/lishengjing/Code/cal_SOB.pl -d ${work_dir}
cp sample_name.txt ${work_dir}/SOB_v1/run/
sh /mnt/hdd/usr/lishengjing/Code/SOB_submit_run.sh ${work_dir}
python3 /mnt/hdd/usr/lishengjing/Code/merge-mutation-server.py ${work_dir}/SOB_v1/SOB_results/ ${work_dir}/SOB_v1/SOB_results.txt
