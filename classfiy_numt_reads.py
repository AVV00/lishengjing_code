import pysam
import sys

bam_filepath=sys.argv[1]
result_txt=sys.argv[2]
# 打开 BAM 文件
bam_file = pysam.AlignmentFile(bam_filepath, "rb")

# 创建字典用于存储 R1 和 R2 reads 名
r1_reads_categories = {
    "1. MT primary, nuclear secondary": [],
    "2. MT primary, no nuclear secondary": [],
    "3. Nuclear primary, MT secondary": [],
    "4. Nuclear primary, no MT secondary": [],
    "5. Unmapped": []
}

r2_reads_categories = {
    "1. MT primary, nuclear secondary": [],
    "2. MT primary, no nuclear secondary": [],
    "3. Nuclear primary, MT secondary": [],
    "4. Nuclear primary, no MT secondary": [],
    "5. Unmapped": []
}
#=================================计算bam文件总数=================================
# 初始化计数器
read_count = 0

# 遍历 BAM 文件中的每个 read
for read in bam_file.fetch():
    read_count += 1

# 打印 reads 总数
print(f"Total number of reads: {read_count}")

#==================================对reads进行5分类===========================================
def classify_read(read, mt_chromosome):
    if read.is_unmapped:
        return "5. Unmapped"
    elif mt_chromosome in read.reference_name:
        if read.has_tag("XA:Z") and mt_chromosome not in read.get_tag("XA"):
            return "1. MT primary, nuclear secondary"
        else:
            return "2. MT primary, no nuclear secondary"
    else:
        if read.has_tag("XA:Z") and mt_chromosome in read.get_tag("XA"):
            return "3. Nuclear primary, MT secondary"
        else:
            return "4. Nuclear primary, no MT secondary"
NOT_1_2=[]
# 读取 BAM 文件
for read in bam_file.fetch():
    if read.is_read1:
        category = classify_read(read, "chrM")
        r1_reads_categories[category].append(read.query_name)
    elif read.is_read2:
        category = classify_read(read, "chrM")
        r2_reads_categories[category].append(read.query_name)
    else:
        NOT_1_2.append(read.query_name)

print(f'R1和R2都不是的reads数：{len(NOT_1_2)}')

# 关闭 BAM 文件
bam_file.close()

#=================将结果输出到矩阵===============================
# 初始化一个5x5的矩阵来存储键对的组合
matrix = [[0 for _ in range(5)] for _ in range(5)]

# 键的名称
keys1 = list(r1_reads_categories.keys())
keys2 = list(r2_reads_categories.keys())

'''
# 遍历第一个字典
for key1, values1 in r1_reads_categories.items():
    # 遍历第二个字典
    for key2, values2 in r2_reads_categories.items():
        # 统计两个字典中相同值的出现次数
        common_values = set(values1) & set(values2)
        for value in common_values:
            for val1 in values1:
                if val1 == value:
                    for val2 in values2:
                        if val2 == value:
                            # 更新矩阵
                            i, j = keys1.index(key1), keys2.index(key2)
                            matrix[i][j] += 1
'''
#paired=[]
#=[]
# 遍历第一个字典
for key1, values1 in r1_reads_categories.items():
    #all_reads_r1=all_reads_r1+values1
    #all_reads_r2=[]
    # 遍历第二个字典
    for key2, values2 in r2_reads_categories.items():
        #all_reads_r2=all_reads_r2+values2
        # 统计两个字典中相同值的出现次数
        common_values = set(values1) & set(values2)

        # 更新矩阵
        i, j = keys1.index(key1), keys2.index(key2)
        matrix[i][j] += len(common_values)
        #paired.extend(common_values)

#ummap_r1=[item for item in all_reads_r1 if item not in paired]
#ummap_r2=[item for item in all_reads_r2 if item not in paired]
'''
ummap_r1=set(all_reads_r1)- set(paired)
ummap_r2=set(all_reads_r2)- set(paired)
paired_Reads=set(all_reads_r1) & set(all_reads_r2)
print(f'R1和R2中能直接配对的reads有：{len(paired_Reads)}')
print(f'R1中未配对的reads有{len(ummap_r1)}条')
print(f'R2中未配对的reads有{len(ummap_r2)}条')
print(f'R1的reads数：{len(all_reads_r1)}')
print(f'R2的reads数：{len(all_reads_r2)}')
print(f'R1中有无重复校正：{len(set(all_reads_r1))}')
print(f'R2中有无重复校正：{len(set(all_reads_r2))}')

with open('unpaired.txt','w') as file1:
    for i in ummap_r1:
        file1.write(i+'\n')
    for i in ummap_r2:
        file1.write(i+'\n')


# 打印结果矩阵
for row in matrix:
    print(row)
'''
#total = sum(sum(row) for row in matrix)
#print(f'矩阵总数是：{total}')

with open(result_txt, 'w') as f:
    f.write(f'R1\tR2\t{bam_filepath.split(".")[0]}\n')
    # 遍历矩阵的每一行
    for i, row in enumerate(matrix):
        # 遍历矩阵的每一列
        for j, value in enumerate(row):
            # 写入横坐标、纵坐标和矩阵值
            f.write(f"{keys1[i]}\t{keys2[j]}\t{value}\n")
