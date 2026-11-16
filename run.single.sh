## copy data
run_dir="/mnt/data2/Seq_data/20250509/"
sed -i 's/\r//g' input.info.txt
perl /mnt/hdd/usr/xiefanfan/tools/mtDNA_pipeline/script/classify_data.pl -i ${run_dir}/Combine_Analysis_rCRS-hg19-DNA_V1/input.info.txt -o ${run_dir}/

## count the barcode
python /mnt/hdd/usr/xiefanfan/tools/mtDNA_pipeline/script/get_barcode_v1.py --infile ${run_dir}/Combine_Analysis_rCRS-hg19-DNA_V1/input.info.txt --outdir ${run_dir}/

## run the main script
sh /mnt/hdd/usr/lishengjing/Code/script_generator_single.sh ${run_dir}/ ${run_dir}/Combine_Analysis_rCRS-hg19-DNA_V1/

## run ssp  need to switch to root
#sh /mnt/hdd/usr/lishengjing/Code/script_generator_v2_ssp.sh ${run_dir}/ ${run_dir}/Combine_Analysis_rCRS-hg19-DNA_V1/


## call mutaion
sh /mnt/hdd/usr/xiefanfan/tools/mtDNA_pipeline/script/get_mutation.sh ${run_dir}/ ${run_dir}/Combine_Analysis_rCRS-hg19-DNA_V1

## get fasta file
/usr/bin/perl /mnt/hdd/usr/xiefanfan/tools/mtDNA_pipeline/script/get_fasta.pl -indir ${run_dir}/ -outdir ${run_dir}/Combine_Analysis_rCRS-hg19-DNA_V1

##get haplogroup
sh /mnt/hdd/usr/lishengjing/Code/get_haplogroup.sh ${run_dir}/Combine_Analysis_rCRS-hg19-DNA_V1

## data summury
#/usr/bin/perl /mnt/hdd/usr/xiefanfan/tools/mtDNA_pipeline/script/alignment_stat_v1.pl -a ${run_dir}/ -b mitotools.csv
/usr/bin/perl /mnt/hdd/usr/lishengjing/Code/alignment_stat_v2.pl -a ${run_dir}/ -b haplogroup.txt

## get CN
sh /mnt/hdd/usr/lishengjing/Code/get_cap_CN_124.sh ${run_dir}/ ${run_dir}/Combine_Analysis_rCRS-hg19-DNA_V1

