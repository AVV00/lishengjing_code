import os
import shutil
import sys

def classify_and_rename_files(directory):
    # 遍历指定目录下的所有文件
    for filename in os.listdir(directory):
        if filename.endswith('.R1.fastq.gz') or filename.endswith('.R2.fastq.gz'):
            # 获取样本名（文件名前缀）
            sample_name = filename.split('.')[0]
            # 创建样本名目录（如果不存在）
            sample_dir = os.path.join(directory, sample_name)
            if not os.path.exists(sample_dir):
                os.makedirs(sample_dir)
            
            # 构建新的文件名
            if filename.endswith('.R1.fastq.gz'):
                new_filename = sample_name + '.R1.fq.gz'
            elif filename.endswith('.R2.fastq.gz'):
                new_filename = sample_name + '.R2.fq.gz'
            
            # 移动并重命名文件
            src_path = os.path.join(directory, filename)
            dst_path = os.path.join(sample_dir, new_filename)
            shutil.move(src_path, dst_path)
            print(f'Moved {src_path} to {dst_path}')

if __name__ == "__main__":
    # 获取用户输入的目录路径
    if len(sys.argv) != 2:
        print("Usage: python classify_and_rename_files.py <directory_path>")
        sys.exit(1)

    directory_path = sys.argv[1]

    # 检查目录是否存在
    if not os.path.exists(directory_path):
        print(f"Error: Directory '{directory_path}' does not exist.")
        sys.exit(1)

    # 进行文件分类和重命名
    classify_and_rename_files(directory_path)

