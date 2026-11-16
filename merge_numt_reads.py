import os
import sys 

folder_path = sys.argv[1]
output_filename = sys.argv[2]

def process_folder(folder_path, output_filename):
    # 存储每个文件的计数结果，格式为 [(文件名, 出现一次的数据个数, 出现两次的数据个数), ...]
    results = []

    # 遍历文件夹中的所有文件
    for filename in os.listdir(folder_path):
        # 构建完整的文件路径并确保是txt文件
        if filename.endswith('.txt'):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                # 读取文件内容并计算每行内容的出现次数
                lines = file.readlines()
                line_counts = {}
                for line in lines:
                    line = line.strip()  # 去除两端空白字符
                    if line in line_counts:
                        line_counts[line] += 1
                    else:
                        line_counts[line] = 1

                # 计算每个文件中出现一次和出现两次的数据个数
                count_once = sum(1 for count in line_counts.values() if count == 1)
                count_twice = sum(1 for count in line_counts.values() if count == 2)

                # 将计数结果添加到results列表中
                results.append((filename, count_once, count_twice))

    # 将每个文件的计数结果写入新的输出文件
    with open(output_filename, 'w', encoding='utf-8') as output_file:
        for filename, count_once, count_twice in results:
            output_file.write(f'{filename}\t{count_once}\t{count_twice}\n')


# 使用示例
  # 请修改为你的文件夹路径
  # 结果文件名
process_folder(folder_path, output_filename)

