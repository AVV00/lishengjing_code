import os
import sys
import codecs

'''
文件解释：
（1）如果样本名称是一致的，则运行第29行，如果不一致，则运行28行
（2）第25行为样本名提取，注意观察文件名的分隔符是什么
'''

def detect_encoding(file_path):
    """尝试检测文件编码"""
    encodings = ['utf-8', 'latin-1', 'cp1252', 'gbk', 'iso-8859-1']
    for encoding in encodings:
        try:
            with codecs.open(file_path, 'r', encoding=encoding) as f:
                f.read(1024)  # 读取一小部分测试
            return encoding
        except UnicodeDecodeError:
            continue
    return 'utf-8'  # 默认使用utf-8

# 设定文件夹路径
folder_path = sys.argv[1]
merged_file_path = sys.argv[2]

# 获取所有的txt文件
txt_files = [f for f in os.listdir(folder_path) if f.endswith('.txt')]

# 打开合并后的文件，准备写入
with open(merged_file_path, 'w', encoding='utf-8') as outfile:
    # 遍历每个txt文件
    for file in txt_files:
        file_path = os.path.join(folder_path, file)
        problem_lines = []  # 记录有问题的行号
        
        try:
            # 检测文件编码
            encoding = detect_encoding(file_path)
            
            # 打开文件进行读取
            with codecs.open(file_path, 'r', encoding=encoding, errors='replace') as infile:
                # 遍历文件中的每一行
                for line_num, line in enumerate(infile, 1):
                    try:
                        if line.strip():
                            parts = line.strip().split('\t')
                            if len(parts) < 3:
                                print(f"警告: 文件 {file} 第 {line_num} 行字段不足: {line.strip()}")
                                continue
                            
                            type = parts[1] + '>' + parts[2]
                            sample = os.path.splitext(file)[0].split('.')[0]  # 样本名
                            
                            # 写入处理后的行
                            outfile.write(f"{os.path.splitext(file)[0]}\t{sample}\t{line.strip()}\t{type}\n")
                    except Exception as e:
                        problem_lines.append(line_num)
                        print(f"错误: 处理文件 {file} 第 {line_num} 行时出错: {str(e)}")
                        print(f"问题行内容: {line}")
            
            # 如果有问题行，打印报告
            if problem_lines:
                print(f"警告: 文件 {file} 有以下行处理失败: {problem_lines}")
        
        except Exception as e:
            print(f"严重错误: 无法处理文件 {file}: {str(e)}")
            # 尝试使用二进制模式读取以查看问题内容
            try:
                with open(file_path, 'rb') as binfile:
                    content = binfile.read(500)
                    print(f"文件 {file} 开头内容(十六进制): {content[:100].hex()}")
            except Exception as bin_err:
                print(f"无法读取文件 {file} 的二进制内容: {str(bin_err)}")

# 输出完成
print(f"文件合并完成，结果保存到: {merged_file_path}")
