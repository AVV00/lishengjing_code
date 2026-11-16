import os
import sys
import csv

def extract_insert_data(file_path):
    """
    从单个insertsize.txt文件中提取insert_size和对应的count数据
    """
    data_dict = {}
    start_extract = False
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line == "insert_size\tAll_Reads.fr_count":
                start_extract = True
                continue
            if start_extract:
                if not line or line.startswith("#") or line.startswith("##"):
                    continue
                parts = line.split("\t")
                if len(parts) != 2:
                    continue
                try:
                    insert_size = int(parts[0])
                    count = int(parts[1])
                    data_dict[insert_size] = count
                except ValueError:
                    continue
    return data_dict

def main(root_dir):
    # 1. 收集所有目标txt文件
    target_files = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".txt") and "insertsize" in file:
                file_path = os.path.join(root, file)
                target_files.append(file_path)
    
    if not target_files:
        print("未找到包含insertsize的txt文件", file=sys.stderr)
        sys.exit(1)
    
    # 2. 提取每个文件的数据，并汇总所有insert_size
    all_data = {}
    all_insert_sizes = set()
    for file_path in target_files:
        data = extract_insert_data(file_path)
        all_data[file_path] = data
        all_insert_sizes.update(data.keys())
    
    # 3. 确定片段大小范围：从1到最大insert_size
    min_size = 1
    max_size = max(all_insert_sizes) if all_insert_sizes else 1
    insert_sizes = list(range(min_size, max_size + 1))
    
    # 4. 准备输出数据
    output_rows = []
    # 表头：第一列是insert_size，后续是文件路径
    header = ["insert_size"] + target_files
    output_rows.append(header)
    
    # 填充每一行数据
    for size in insert_sizes:
        row = [size]
        for file_path in target_files:
            row.append(all_data[file_path].get(size, 0))
        output_rows.append(row)
    
    # 5. 写入输出文件
    output_file = "merged_insertsize.csv"
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerows(output_rows)
    
    print(f"合并完成！输出文件：{output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python3 脚本名.py 大文件夹路径", file=sys.stderr)
        sys.exit(1)
    root_directory = sys.argv[1]
    if not os.path.isdir(root_directory):
        print(f"错误: {root_directory} 不是有效的文件夹路径", file=sys.stderr)
        sys.exit(1)
    main(root_directory)
