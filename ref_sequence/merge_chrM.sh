grep -v "^>" /mnt/hdd/ref_data/genomes/human/hg38/chrM.fa | tr -d '\n' > chrM_sequence.txt
original_length=$(wc -c < chrM_sequence.txt)
echo "Original length: $original_length"  # 应输出 Original length: 16569
cat chrM_sequence.txt chrM_sequence.txt > chrM_duplicated_sequence.txt
duplicated_length=$(wc -c < chrM_duplicated_sequence.txt)
echo "Duplicated length: $duplicated_length"  # 应输出 Duplicated length: 33138
echo ">chrM_circular_v2" > /mnt/hdd/ref_data/genomes/human/hg38/chrM_circular_v2.fa
fold -w 80 chrM_duplicated_sequence.txt >> /mnt/hdd/ref_data/genomes/human/hg38/chrM_circular_v2.fa

# 确保文件末尾有换行符（避免工具解析错误）
echo "" >> /mnt/hdd/ref_data/genomes/human/hg38/chrM_circular_v2.fa
# 检查标题行唯一性
grep "^>" /mnt/hdd/ref_data/genomes/human/hg38/chrM_circular_v2.fa  # 应仅有一行 >chrM_circular_v2

# 检查所有序列行长度（除最后一行外应为80字符）
awk '!/^>/ {if (length($0)!=80 && NR>1) print "Line " NR " has length " length($0)}' /mnt/hdd/ref_data/genomes/human/hg38/chrM_circular_v2.fa
# 若无输出，表示所有行长度一致

# 验证总长度（33138）
tail -n +2 /mnt/hdd/ref_data/genomes/human/hg38/chrM_circular_v2.fa | tr -d '\n' | wc -c  # 应输出33138
samtools faidx /mnt/hdd/ref_data/genomes/human/hg38/chrM_circular_v2.fa  # 应无报错

# 检查索引文件
cat /mnt/hdd/ref_data/genomes/human/hg38/chrM_circular_v2.fa.fai
# 正确输出示例：
# chrM_circular_v2  33138  18  80  81
