import os
import shutil
import sys
# 源文件夹路径
source_folder = sys.argv[1]
# 目标文件夹路径
target_folder = sys.argv[2]


# 遍历源文件夹中的所有文件
for filename in os.listdir(source_folder):
    # 检查文件是否是普通文件
    if os.path.isfile(os.path.join(source_folder, filename)):
        # 分割文件名，获取样本名,保留倒数第二个_之前的内容
        sample = filename.split('.')[0]
        last_index = sample.rfind("_")
        second_last_index = sample.rfind("_", 0, last_index)
        if second_last_index != -1:
            sample_name = sample[:second_last_index]
        else:
            sample_name=sample
        # 创建目标文件夹路径
        target_path = os.path.join(target_folder, sample_name)
        # 检查目标文件夹是否存在，如果不存在则创建
        if not os.path.exists(target_path):
            os.makedirs(target_path)
        #print(filename.split('.')[1])
        #print(filename.split('.')[1]=='R1')
        if filename.split('.')[1]=='R1':
            new_filename=sample_name + '_R1.fq.gz'
        elif filename.split('.')[1]=='R2':
            new_filename=sample_name + '_R2.fq.gz'
        print(new_filename)
        # 移动文件到目标文件夹
        shutil.move(os.path.join(source_folder, filename), os.path.join(target_path, new_filename))

print("文件移动完成。")

