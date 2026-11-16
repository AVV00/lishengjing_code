#!/bin/bash

# 检查是否提供了正确数量的参数
if [ "$#" -ne 2 ]; then
    echo "用法: $0 [原始文件夹路径] [新文件夹路径]"
    exit 1
fi

# 命令行参数
original_folder="$1"
new_folder="$2"

# 创建新文件夹，如果不存在的话
mkdir -p "$new_folder"

# 遍历原始文件夹中的所有.hetro_0.1.txt文件
for hetro_file in "$original_folder"/*.hetro_1.txt; do
  # 获取不包含后缀的文件名
    base_name=$(basename "$hetro_file" .hetro_1.txt)
  
  # 对应的.homo_0.1.txt文件路径
    homo_file="$original_folder/$base_name.homo_1.txt"

  # 如果配对的.homo_0.1.txt文件存在
    if [[ -f "$homo_file" ]]; then
    # 合并文件到新的文件夹中，并命名为【样本名】.txt
        cat "$hetro_file" "$homo_file" > "$new_folder/$base_name.txt"
    else
        echo "没有找到与$hetro_file 对应的 $homo_file 文件"
    fi
done

echo "文件合并完成"
