import os
import sys
'''
文件解释：
（1）如果样本名称是一致的，则运行第29行，如果不一致，则运行28行
（2）第25行为样本名提取，注意观察文件名的分隔符是什么
'''
# 设定文件夹路径
#folder_path = r'D:\数据分析\2024\数据分析+结果+汇总PPT\2024.12.03-整理双组学文章所需数据\1-细胞系样本\1-一些原始文件\SOB'  # 请将这里的路径替换为你的文件夹路径
#merged_file_path = r'D:\数据分析\2024\数据分析+结果+汇总PPT\2024.12.03-整理双组学文章所需数据\1-细胞系样本\1-一些原始文件\SOB.txt'  # 合并后文件的名称和路径
folder_path=sys.argv[1]
merged_file_path=sys.argv[2]
# 获取所有的txt文件
txt_files = [f for f in os.listdir(folder_path) if f.endswith('.txt')]

# 打开合并后的文件，准备写入

with open(merged_file_path, 'w') as outfile:
    # 遍历每个txt文件
    for file in txt_files:
        file_path = os.path.join(folder_path, file)

        # 打开文件进行读取
        with open(file_path, 'r') as infile:
            # 遍历文件中的每一行
            for line in infile:
                if line.strip():
                    type = line.strip().split('\t')[1] + '>' + line.split('\t')[2]
                    sample = os.path.splitext(file)[0].split('.')[0]  # 样本名
                    #qh = os.path.splitext(file)[0].split('.')[1]  # 样本名
                    # 如果行不是空的，去除行尾换行符并以\t分隔，然后在行首加入文件名
                    #outfile.write(f"{os.path.splitext(file)[0]}\t{line.strip()}\t{type}\n") #不输出sample
                    outfile.write(f"{os.path.splitext(file)[0]}\t{sample}\t{line.strip()}\t{type}\n") #输出sample
                    #outfile.write(f"{os.path.splitext(file)[0]}\t{sample}\t{line.strip()}\n")  # 不输出type
# 输出完成
print("Files have been merged successfully.")

