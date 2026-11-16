import sys
from collections import defaultdict

def merge_pileup(input_file, output_file, original_length=16569):
    # 初始化字典存储合并后的数据
    merged = defaultdict(lambda: {'chr': None, 'pos': 0, 'ref': '', 'depth': 0, 'bases': '', 'quals': ''})

    with open(input_file, 'r') as f:
        for line in f:
            fields = line.strip().split('\t')
            chrom, pos, ref, depth, bases, quals = fields[0], int(fields[1]), fields[2], int(fields[3]), fields[4], fields[5]

            # 计算原始位置
            original_pos = pos if pos <= original_length else pos - original_length

            # 合并数据
            if merged[original_pos]['pos'] == 0:
                merged[original_pos] = {
                    'chr': chrom,
                    'pos': original_pos,
                    'ref': ref,
                    'depth': depth,
                    'bases': bases,
                    'quals': quals
                }
            else:
                merged[original_pos]['depth'] += depth
                merged[original_pos]['bases'] += bases
                merged[original_pos]['quals'] += quals

    # 写入合并后的文件
    with open(output_file, 'w') as f_out:
        for pos in sorted(merged.keys()):
            data = merged[pos]
            f_out.write(f"{data['chr']}\t{data['pos']}\t{data['ref']}\t{data['depth']}\t{data['bases']}\t{data['quals']}\n")

if __name__ == "__main__":
    input_pileup = sys.argv[1]
    output_pileup = sys.argv[2]
    merge_pileup(input_pileup, output_pileup)
