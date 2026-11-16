run_dir=''
perl /mnt/hdd/usr/lishengjing/softs/igenetech_bus_InsertUMIv3/rundocker.pl \
-i ${run_dir}/UMI_Rawdata/ \
-o ${run_dir}/UMI_analysis/ \
-d /mnt/hdd/usr/lishengjing/softs/igenetech_bus_InsertUMIv3/database/ \
-s sample_name.txt \
-pd /mnt/hdd/usr/lishengjing/softs/igenetech_bus_InsertUMIv3 \
-p T033 \
-th 8



target_dir=$run_dir/UMI_analysis/IGT/
reference_file=$run_dir/sample_name.txt

# 检查目标文件夹是否存在
if [ ! -d "$target_dir" ]; then
    echo "错误: 目标文件夹 '$target_dir' 不存在"
    exit 1
fi

# 检查参考文件是否存在
if [ ! -f "$reference_file" ]; then
    echo "错误: 参考文件 '$reference_file' 不存在"
    exit 1
fi

# 计算目标文件夹下的子文件夹数量（不包括隐藏文件夹）
folder_count=$(find "$target_dir" -maxdepth 1 -type d ! -name ".*" | wc -l)
# 减去1是因为find命令会包含目标文件夹本身
folder_count=$((folder_count - 1))

# 计算参考文件的行数
line_count=$(wc -l < "$reference_file")

echo "子文件夹数量: $folder_count"
echo "参考文件行数: $line_count"

# 比较数量是否相等
if [ $folder_count -eq $line_count ]; then
    echo "数量相等，执行指定指令..."
    cd $run_dir
    mkdir UMI_summary
    cd UMI_summary
    mkdir mutation
    mkdir tag_size
    mkdir tag_size_pdf
    mkdir depth

    cp $target_dir/*/*.snp_indel.anno.xls $run_dir/UMI_summary/mutation
    python3 /mnt/hdd/usr/lishengjing/Code/merge_mutation_UMI.py $run_dir/UMI_summary/mutation
    cat $target_dir/*/*.statistic.xls > statistic.xls
    cp $run_dir/UMI_analysis/*/static/*.tag_family_size.txt $run_dir/UMI_summary/tag_size
    cp $run_dir/UMI_analysis/*/static/*.tag_family_size.top50.pdf $run_dir/UMI_summary/tag_size_pdf
    cp $run_dir/UMI_analysis/*/static/*.depth.stat $run_dir/UMI_summary/depth
    python3 /mnt/hdd/usr/lishengjing/Code/merge_tag_family.py $run_dir/UMI_summary/tag_size $run_dir/UMI_summary/tag_size.txt
    python3 /mnt/hdd/usr/lishengjing/Code/merge-depth.py $run_dir/UMI_summary/depth $run_dir/UMI_summary/

else
    echo "数量不相等，不执行指令"
fi

exit 0

