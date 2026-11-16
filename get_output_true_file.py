import os
import sys
import pandas as pd


def process_mutation_file(input_dir, cutoff, vaf, output_suffix="output_true_"):
    """
    处理线粒体突变文件，筛选低频突变并输出标准化结果

    参数：
    input_dir: str - 输入文件所在的根目录（对应原R脚本的path参数）
    cutoff: float - 频率筛选阈值（对应原R脚本的cutoff参数，需为整数或小数，如5表示5%）
    vaf: str - VAF值，用于输出文件名（对应原R脚本的vaf参数）
    output_suffix: str - 输出文件前缀（默认与原R脚本一致为"output_true_"）
    """
    # 验证输入目录是否存在
    if not os.path.exists(input_dir):
        print(f"错误：输入目录不存在 -> {input_dir}")
        sys.exit(1)

    # 转换cutoff为筛选阈值（与原R脚本逻辑一致：cutoff×0.01）
    filter_threshold = float(cutoff) * 0.01
    print(f"筛选阈值：突变频率 ≤ {filter_threshold:.6f}（原始cutoff={cutoff}）")
    # 遍历目录下所有符合格式的突变文件（<样本名>.conrmdup.v5.end10.txt）
    for filename in os.listdir(input_dir):
        if filename.endswith(".conrmdup.v5.end10.txt"):
            # 1. 提取样本名（从文件名中截取，如"HCS-2076P1k.conrmdup.v5.end10.txt" -> "HCS-2076P1k"）
            sample_name = filename.replace(".conrmdup.v5.end10.txt", "")
            file_path = os.path.join(input_dir, filename)
            print(f"\n正在处理样本：{sample_name} -> 文件路径：{file_path}")

            # 2. 读取突变文件（指定列名，确保与输入格式匹配）
            try:
                # 原始文件列：Variant, Position, ref, alt, Count, TotalDepth, Frequency(%)
                df = pd.read_csv(
                    file_path,
                    sep="\t",  # 制表符分隔
                    header=0,  # 第一行为列名
                    dtype={
                        "Variant": str,
                        "Position": int,
                        "ref": str,
                        "alt": str,
                        "Count": int,
                        "TotalDepth": int,
                        "Frequency(%)": float
                    }
                )
            except Exception as e:
                print(f"警告：读取文件{filename}失败，跳过该文件。错误信息：{str(e)}")
                continue

            # 3. 数据格式转换：Frequency(%)列除以100（去除百分比，转为小数）
            df["Frequency"] = df["Frequency(%)"] / 100  # 新增小数格式的频率列
            print(f"原始数据行数：{len(df)}，频率列转换完成（% -> 小数）")

            # 4. 筛选低频突变（频率 ≤ filter_threshold）
            filtered_df = df[df["Frequency"] <= filter_threshold].copy()
            print(f"筛选后低频突变行数：{len(filtered_df)}")

            # 5. 按原R脚本格式重组输出数据（6列）
            # 输出列顺序：chrM（固定）、Position、ref、alt、样本名、Frequency（小数格式）
            output_df = pd.DataFrame({
                "Col1": "chrM",  # 第一列固定为"chrM"（线粒体标记）
                "Col2": filtered_df["Position"],  # 第二列：突变位置（对应原文件Position列）
                "Col3": filtered_df["ref"],  # 第三列：参考碱基（对应原文件ref列）
                "Col4": filtered_df["alt"],  # 第四列：变异碱基（对应原文件alt列）
                "Col5": sample_name,  # 第五列：样本名
                "Col6": filtered_df["Frequency"]  # 第六列：转换后的频率（小数）
            })

            # 6. 生成输出文件（路径：输入目录下，文件名：output_true_<vaf>）
            output_filename = f"{output_suffix}{vaf}"
            output_path = os.path.join(input_dir, output_filename)
            # 写入文件：无表头、无索引、制表符分隔（与原R脚本一致）
            output_df.to_csv(
                output_path,
                sep="\t",
                header=False,
                index=False,
                quoting=3  # 对应R的quote=F，不引用字符串
            )
            print(f"输出文件已保存：{output_path}")

    print(f"\n所有文件处理完成！")


if __name__ == "__main__":
    # 命令行参数解析（与原R脚本参数顺序一致）
    # 用法：python get_output_true_file.py <input_dir> <cutoff> <vaf>
    if len(sys.argv) != 4:
        print("用法错误！正确命令：")
        print("python get_output_true_file.py <输入目录路径> <频率筛选阈值> <VAF值>")
        print("示例：python get_output_true_file.py ./mutations 5 0.01")
        print("说明：")
        print("  <输入目录路径>：存放突变文件（*.conrmdup.v5.end10.txt）的目录")
        print("  <频率筛选阈值>：低频突变的频率上限（如5表示筛选≤5%的突变，实际计算时会×0.01）")
        print("  <VAF值>：用于输出文件名（如0.01，输出文件为output_true_0.01）")
        sys.exit(1)

    # 获取命令行参数
    input_dir = sys.argv[1]
    cutoff = sys.argv[2]
    vaf = sys.argv[3]

    # 调用处理函数
    process_mutation_file(input_dir, cutoff, vaf)