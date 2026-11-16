import pandas as pd
import os

def main():
    # 1. 定义文件绝对路径
    mitimpact_2_0_path = "/mnt/hdd/usr/lishengjing/ref_seq/DB_data/mitimpact_2.0.txt"
    mitimpact_path = "/mnt/hdd/usr/lishengjing/ref_seq/DB_data/mitimpact.txt"
    # 假设原有输出文件路径（可根据实际需求修改）
    output_path = "/mnt/hdd/usr/lishengjing/ref_seq/DB_data/annotated_mutations.txt"

    # 2. 读取 mitimpact_2.0.txt（新增1列：MutationAssessor_score）
    # 列名：pos, ref, alt, PolyPhen2, PolyPhen2_score, MutationAssessor, MutationAssessor_score
    df_2_0 = pd.read_csv(
        mitimpact_2_0_path,
        sep="\t",
        header=0,
        dtype={"pos": int, "ref": str, "alt": str}
    )
    # 只保留需要新增的列（去重，避免重复关联）
    df_2_0_selected = df_2_0[["pos", "ref", "alt", "MutationAssessor_score"]].drop_duplicates(
        subset=["pos", "ref", "alt"], keep="first"
    )
    # 重命名列，避免冲突
    df_2_0_selected.rename(columns={"MutationAssessor_score": "MA_score"}, inplace=True)

    # 3. 读取 mitimpact.txt（新增4列：假设为 impact_type1-4，实际根据文件结构补充，这里以实际数据为准）
    # 列名：pos, ref, alt, impact1, impact2, impact3, impact4（实际文件无表头，需手动指定）
    df_mit = pd.read_csv(
        mitimpact_path,
        sep="\t",
        header=None,
        names=["pos", "ref", "alt", "impact1", "impact2", "impact3", "impact4"],
        dtype={"pos": int, "ref": str, "alt": str}
    )
    # 去重
    df_mit_selected = df_mit.drop_duplicates(subset=["pos", "ref", "alt"], keep="first")

    # 4. 读取原有突变数据（假设原有数据文件路径，需替换为你的实际文件路径）
    # 假设原有数据包含 pos, ref, alt 三列作为关联键
    original_data_path = "/mnt/hdd/usr/lishengjing/ref_seq/DB_data/original_mutations.txt"  # 替换为实际路径
    df_original = pd.read_csv(
        original_data_path,
        sep="\t",  # 根据实际分隔符调整
        header=0,
        dtype={"pos": int, "ref": str, "alt": str}
    )

    # 5. 关联新增注释信息（左连接，保留原有所有数据）
    # 第一步：关联 mitimpact_2.0 的 MA_score
    df_annotated = pd.merge(
        df_original,
        df_2_0_selected,
        on=["pos", "ref", "alt"],
        how="left"
    )

    # 第二步：关联 mitimpact 的 4列注释
    df_annotated = pd.merge(
        df_annotated,
        df_mit_selected,
        on=["pos", "ref", "alt"],
        how="left"
    )

    # 6. 填充缺失值（可选，根据需求调整）
    df_annotated.fillna(".", inplace=True)

    # 7. 保存结果
    df_annotated.to_csv(
        output_path,
        sep="\t",
        index=False,
        header=True
    )

    print(f"注释完成！新增5列注释（MA_score + impact1-4），结果保存至：{output_path}")

if __name__ == "__main__":
    main()
