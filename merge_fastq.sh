#!/bin/bash

# 设置文件夹路径参数
dir_path="$1"

# 检查参数是否提供
if [[ -z "$dir_path" ]]; then
    echo "错误：请提供文件夹路径作为参数。"
    exit 1
fi

# 检查文件夹是否存在
if [[ ! -d "$dir_path" ]]; then
    echo "错误：文件夹 '$dir_path' 不存在。"
    exit 1
fi

# 设置nullglob避免无匹配时的通配符展开问题
shopt -s nullglob

declare -A file_groups  # 声明关联数组用于分组文件

# 遍历目录下所有R1/R2文件并分组
for file in "$dir_path"/*.R[12].fastq.gz; do
    filename=$(basename "$file")
    # 使用正则解析文件名格式
    if [[ $filename =~ ^([^_]+)_([^_]+)_([^_]+)\.(R[12])\.fastq\.gz$ ]]; then
        sample="${BASH_REMATCH[1]}"
        end="${BASH_REMATCH[4]}"
        key="${sample}_${end}"  # 分组键（样本名+端）
        file_groups["$key"]+="$file|"  # 使用|分隔文件路径以处理空格
    else
        echo "注意：文件 '$filename' 不符合命名格式，已跳过。"
    fi
done

# 处理每个文件分组
for key in "${!file_groups[@]}"; do
    files_str="${file_groups[$key]%|}"  # 移除末尾分隔符
    IFS='|' read -ra files <<< "$files_str"  # 分割为数组
    
    if (( ${#files[@]} > 1 )); then
        # 解析样本名和端
        IFS='_' read -ra key_parts <<< "$key"
        sample="${key_parts[0]}"
        end="${key_parts[1]}"
        
        # 生成唯一的新文件名（使用时间戳确保唯一性）
        new_ident1="merged"
        new_ident2=$(date +%s)
        new_filename="${sample}_${new_ident1}_${new_ident2}.${end}.fastq.gz"
        new_filepath="$dir_path/$new_filename"
        
        # 合并文件
        echo "正在合并 ${#files[@]} 个文件到 $new_filename..."
        cat "${files[@]}" > "$new_filepath"
        
        # 验证合并结果并删除原文件
        if [[ -s "$new_filepath" ]]; then
            echo "合并成功，正在删除原始文件..."
            rm "${files[@]}"
        else
            echo "错误：合并失败，保留原始文件。"
            rm -f "$new_filepath"
            exit 1
        fi
    else
        echo "信息：$key 无补测数据，无需合并。"
    fi
done

shopt -u nullglob  # 恢复nullglob设置
