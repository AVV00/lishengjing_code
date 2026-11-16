#!/bin/bash
rundir=$1
input_directory=${rundir}/fasta

cd ${rundir}
mkdir ${rundir}/haplogroup
output_directory=${rundir}/haplogroup

cd /mnt/hdd/usr/lishengjing/softs/haplogrep3/
for file in "$input_directory"/*.fa; do
    #echo "Processing $file"
    # 提取输入文件的文件名（不包含路径）
    filename=$(basename "$file")
    
    # 创建对应的输出文件路径和文件名
    output_file="$output_directory/$filename"_haplogroup.txt
    
    # 运行 haplogrep3 命令，并指定输出文件
    /mnt/hdd/usr/lishengjing/softs/haplogrep3/haplogrep3 classify --in "$file" --tree phylotree-rcrs@17.2 --out "$output_file"
done

output_file=${rundir}/haplogroup.txt
# 遍历目录下的所有文件
for file in "$output_directory"/*; do
    # 检查是否是普通文件
    if [ -f "$file" ]; then
        # 读取每个文件的第二行
        second_line=$(sed -n '2p' "$file")
        
        # 去掉双引号
        second_line=${second_line//\"/}
        
        # 将处理后的第二行追加到输出文件
        echo "$second_line" >> "$output_file"
    fi
done
