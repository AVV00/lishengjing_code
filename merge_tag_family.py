import os
import sys
import pandas as pd

def process_family_size_files(input_folder, output_file):
    # 存储所有样本的数据，键为样本名，值为字典（键：family size，值：数量）
    sample_data = {}
    # 存储所有文件中的最大family size
    max_family_size = 0

    # 遍历输入文件夹中的所有文件
    for filename in os.listdir(input_folder):
        # 仅处理.txt文件
        if filename.endswith('.txt'):
            # 提取样本名（假设文件名格式为“样本名.tag_family_size.txt”，取第一个“.”前的部分作为样本名）
            sample_name = filename.split('.')[0]
            file_path = os.path.join(input_folder, filename)
            
            try:
                # 读取txt文件，分隔符为制表符或空格（适应不同分隔符情况）
                df = pd.read_csv(file_path, sep='\s+', header=None, names=['family_size', 'count'])
                # 将数据转换为字典，便于后续查找
                family_count_dict = dict(zip(df['family_size'], df['count']))
                sample_data[sample_name] = family_count_dict
                
                # 更新最大family size
                current_max = df['family_size'].max()
                if current_max > max_family_size:
                    max_family_size = current_max
            except Exception as e:
                print(f"处理文件 {filename} 时出错：{str(e)}")
                continue

    # 如果没有有效数据，提示并退出
    if not sample_data or max_family_size == 0:
        print("未找到有效数据或所有文件数据为空")
        return

    # 生成从1到最大family size的连续序列
    all_family_sizes = list(range(1, max_family_size + 1))
    # 创建合并后的数据框，第一列为family size
    merged_df = pd.DataFrame({'family_size': all_family_sizes})

    # 为每个样本添加对应的数量列，若该样本无此family size的数据，数量设为0
    for sample_name, family_count_dict in sample_data.items():
        # 按照all_family_sizes的顺序获取每个family size对应的数量
        counts = [family_count_dict.get(fs, 0) for fs in all_family_sizes]
        merged_df[sample_name] = counts

    # 调整列顺序，确保family_size在第一列
    columns_order = ['family_size'] + list(sample_data.keys())
    merged_df = merged_df[columns_order]

    # 保存合并后的数据到输出文件
    merged_df.to_csv(output_file, index=False, sep='\t')
    print(f"数据合并完成，已保存到 {output_file}")

if __name__ == "__main__":
    # 检查命令行参数是否正确
    if len(sys.argv) != 3:
        print("使用方法：python merge_family_size.py <输入文件夹路径> <输出文件路径>")
        print("示例：python merge_family_size.py ./family_size_files ./merged_family_size.txt")
        sys.exit(1)

    # 获取命令行传入的输入文件夹和输出文件路径
    input_folder = sys.argv[1]
    output_file = sys.argv[2]

    # 检查输入文件夹是否存在
    if not os.path.exists(input_folder):
        print(f"错误：输入文件夹 {input_folder} 不存在")
        sys.exit(1)

    # 执行数据合并操作
    process_family_size_files(input_folder, output_file)
