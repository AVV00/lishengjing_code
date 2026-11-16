#!bin/bash
start=$(date +%s) #start time
echo "start time: "`date` 
sed -i 's/\r//g' sample_path_list.txt
cat sample_path_list.txt | while read line
do

    inpath=${line}
    echo ${inpath}
    #cal endmotifs
    python /mnt/hdd/usr/jiaohuanmin/home/jiaohm/Tools/mtDNA_pipeline/fragment_stduy_pipeline/endmotifs_stat_v2.2.py ${inpath} 4
    
    #cal LS125 sam
    #python /mnt/hdd/usr/jiaohuanmin/home/jiaohm/Tools/mtDNA_pipeline/fragment_stduy_pipeline/split_mis10_by125_v1.1.py ${inpath}
    
    #cal depth
    #bash /mnt/hdd/usr/jiaohuanmin/home/jiaohm/Tools/mtDNA_pipeline/fragment_stduy_pipeline/chrM_depth_v1.1.sh ${inpath}
    
    #cal zfsd
    #python /mnt/hdd/usr/jiaohuanmin/home/jiaohm/Tools/mtDNA_pipeline/fragment_stduy_pipeline/concate_depth_v4.py ${inpath}
    
    #cal zfsd feature----------------------- no run
    ##python /mnt/hdd/usr/jiaohuanmin/home/jiaohm/Tools/mtDNA_pipeline/fragment_stduy_pipeline/fsd_feature_cal.py ${inpath}
    
    # cal insertsize------------------------ no run
    #bash /mnt/hdd/usr/jiaohuanmin/home/jiaohm/Tools/mtDNA_pipeline/fragment_stduy_pipeline/insertisize_find_mt.sh ${inpath}
    
    #concate insertsize
    #python /mnt/hdd/usr/jiaohuanmin/home/jiaohm/Tools/mtDNA_pipeline/fragment_stduy_pipeline/insertsize_concate_v3.1.py ${inpath}
    
    # ================four region split=========================
    #sh /mnt/hdd/usr/jiaohuanmin/home/jiaohm/Tools/mtDNA_pipeline/fragment_stduy_pipeline/mis10_region_split_v2.sh ${inpath}
    #compute mRNA endmotifs
    #python /mnt/hdd/usr/jiaohuanmin/home/jiaohm/Tools/mtDNA_pipeline/fragment_stduy_pipeline/endmotifs_stat_4region_v2.2.py ${inpath} 4 "*.mis.10.mRNA.bam" 0.2753 0.2247
    #compute tRNA endmotifs
    #python /mnt/hdd/usr/jiaohuanmin/home/jiaohm/Tools/mtDNA_pipeline/fragment_stduy_pipeline/endmotifs_stat_4region_v2.2.py ${inpath} 4 "*.mis.10.tRNA.bam" 0.3108 0.1892
    #compute rRNA endmotifs
    #python /mnt/hdd/usr/jiaohuanmin/home/jiaohm/Tools/mtDNA_pipeline/fragment_stduy_pipeline/endmotifs_stat_4region_v2.2.py ${inpath} 4 "*.mis.10.rRNA.bam" 0.2810 0.2190
    #compute Dloop endmotifs
    #python /mnt/hdd/usr/jiaohuanmin/home/jiaohm/Tools/mtDNA_pipeline/fragment_stduy_pipeline/endmotifs_stat_4region_v2.2.py ${inpath} 4 "*.mis.10.Dloop.bam" 0.2669 0.2331
    #compute depth
    #sh /mnt/hdd/usr/jiaohuanmin/home/jiaohm/Tools/mtDNA_pipeline/fragment_stduy_pipeline/chrM_depth_4region.sh ${inpath}
    #concate depth mRNA_rRNA_tRNA_Dloop
    #python /mnt/hdd/usr/jiaohuanmin/home/jiaohm/Tools/mtDNA_pipeline/fragment_stduy_pipeline/concate_depth_region_v4.1.py ${inpath} "mRNA"
    #python /mnt/hdd/usr/jiaohuanmin/home/jiaohm/Tools/mtDNA_pipeline/fragment_stduy_pipeline/concate_depth_region_v4.1.py ${inpath} "rRNA"
    #python /mnt/hdd/usr/jiaohuanmin/home/jiaohm/Tools/mtDNA_pipeline/fragment_stduy_pipeline/concate_depth_region_v4.1.py ${inpath} "tRNA"
    #python /mnt/hdd/usr/jiaohuanmin/home/jiaohm/Tools/mtDNA_pipeline/fragment_stduy_pipeline/concate_depth_region_v4.1.py ${inpath} "Dloop"
    #compute insertsize
    #sh /mnt/hdd/usr/jiaohuanmin/home/jiaohm/Tools/mtDNA_pipeline/fragment_stduy_pipeline/insertsize_region_v0.sh ${inpath}
    #comput mRNA_rRNA_tRNA_Dloop insertsize
    #python /mnt/hdd/usr/jiaohuanmin/home/jiaohm/Tools/mtDNA_pipeline/fragment_stduy_pipeline/insertsize_concate_region_v3.2.py ${inpath} "mRNA"
    #python /mnt/hdd/usr/jiaohuanmin/home/jiaohm/Tools/mtDNA_pipeline/fragment_stduy_pipeline/insertsize_concate_region_v3.2.py ${inpath} "rRNA"
    #python /mnt/hdd/usr/jiaohuanmin/home/jiaohm/Tools/mtDNA_pipeline/fragment_stduy_pipeline/insertsize_concate_region_v3.2.py ${inpath} "tRNA"
    #python /mnt/hdd/usr/jiaohuanmin/home/jiaohm/Tools/mtDNA_pipeline/fragment_stduy_pipeline/insertsize_concate_region_v3.2.py ${inpath} "Dloop"
done
