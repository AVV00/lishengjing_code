#!/usr/bin/env python3
import os
import sys
import glob
import pandas as pd
import re
from subprocess import check_call, CalledProcessError
import shutil

# 配置文件路径（统一管理，便于修改）
ANNOTATE_SCRIPT = "/mnt/hdd/softs/annovar/2020/annotate_variation.pl"
HUMANDB = "/mnt/hdd/softs/annovar/2020/humandb"
DBSNP_FILE = "/mnt/hdd/softs/dbsnp/chrM_dbsnp_b151.GRCh37p13.All_20180423.vcf"
MITOMAP_CONTROL = "/mnt/hdd/softs/mitomap/mtDNA_Variants_includes_mini_insertions_and_deletions/20200630/control_region/control_uniq.txt"
MITOMAP_CODING = "/mnt/hdd/softs/mitomap/mtDNA_Variants_includes_mini_insertions_and_deletions/20200630/coding_and_RNA/coding_uniq.txt"
DISEASE_FILE = "/mnt/hdd/softs/mitomap/mtDNA_Mutations_with_Reports_of_Disease-Associations/20200630/disease_related_variant.txt"
ASSESSOR_DATA = "/home/suliping/code/annotation/annotation_file/MA_scores_rel3_hg19_chrM_full.txt"
TRNA_DATA = "/home/suliping/code/annotation/annotation_file/tRNA_structure.txt"
CHRM_DATA = "/home/suliping/code/annotation/annotation_file/chrM.fa"
DLOOP_DATA = "/home/suliping/code/annotation/annotation_file/_GenomeLoci lt MITOMAP lt Foswiki.txt"
MIT20_PATH = "/mnt/hdd/usr/lishengjing/ref_seq/DB_data/mitimpact_2.0.txt"
MIT_PATH = "/mnt/hdd/usr/lishengjing/ref_seq/DB_data/mitimpact.txt"

def is_empty_file(file_path):
    """检测文件是否为空（包括仅含空白字符的情况）"""
    if not os.path.exists(file_path):
        return True
    # 检查文件大小是否为0
    if os.path.getsize(file_path) == 0:
        return True
    # 检查文件内容是否仅含空白字符
    try:
        with open(file_path, 'r') as f:
            for line in f:
                if line.strip():  # 存在非空白字符
                    return False
        return True
    except Exception:
        return True

def detect_delimiter(file_path):
    """自动检测文件分隔符（制表符/逗号/空格），兼容多种格式"""
    tab_char = '\t'
    comma_char = ','
    space_char = ' '
    
    delimiters = {tab_char: 0, comma_char: 0, space_char: 0}
    
    with open(file_path, 'r') as f:
        for i, line in enumerate(f):
            if i >= 10:  # 读取前10行足够判断
                break
            if line.startswith('#') or not line.strip():
                continue
            
            # 统计各分隔符出现次数
            delimiters[tab_char] += line.count(tab_char)
            delimiters[comma_char] += line.count(comma_char)
            delimiters[space_char] += len(re.split(r'\s+', line.strip())) - 1
    
    # 选择出现次数最多的分隔符，无则默认制表符
    max_count = max(delimiters.values())
    return [d for d, c in delimiters.items() if c == max_count][0] if max_count > 0 else tab_char

def load_dbsnp():
    """加载dbSNP数据（仅保留单碱基变异，Perl脚本_num函数逻辑）"""
    dbsnp = {}
    with open(DBSNP_FILE, 'r') as f:
        for line in f:
            if line.startswith('#'):
                continue
            parts = line.strip().split('\t')
            if len(parts) < 5:
                continue
            pos, ref, alts = parts[1], parts[3], parts[4]
            if len(ref) != 1:  # 仅处理单碱基变异
                continue
            for alt in alts.split(','):
                if len(alt) == 1:
                    dbsnp[f"{pos}\t{ref}\t{alt}"] = parts[2]  # rs编号
    return dbsnp

def load_mitomap():
    """加载MITOMAP变异数据（控制区+编码区）"""
    mitomap = {}
    for file in [MITOMAP_CONTROL, MITOMAP_CODING]:
        with open(file, 'r') as f:
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) >= 5 and parts[2]:
                    mitomap[f"{parts[2]}\t{parts[3]}\t{parts[4]}"] = 1  # 标记存在
    return mitomap

def load_disease():
    """加载疾病相关变异数据（MITOMAP疾病关联信息）"""
    disease = {}
    with open(DISEASE_FILE, 'r') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 4 and parts[1]:
                disease[f"{parts[1]}\t{parts[2]}\t{parts[3]}"] = parts[-1] if len(parts) > 4 else ""
    return disease

def load_assessor():
    """加载MutationAssessor数据（仅保留Func_Impact和FI_score，R脚本逻辑）"""
    assessor = {}
    df = pd.read_csv(ASSESSOR_DATA, sep='\t')
    for _, row in df.iterrows():
        if pd.isna(row[0]):
            continue
        parts = row[0].split(',')
        if len(parts) < 5:
            continue
        _, _, site, ref, alt = parts
        key = f"{site}\t{ref}\t{alt}"
        assessor[key] = {
            'Func_Impact': row.get('Func..Impact', ''),
            'FI_score': row.get('FI.score', '')
        }
    return assessor

def load_trna():
    """加载tRNA结构数据（缺失时填充空格，R脚本2022.05.27修改逻辑）"""
    trna = {}
    df = pd.read_csv(TRNA_DATA, sep='\t', header=0, keep_default_na=False)
    for _, row in df.iterrows():
        struct_name = row[0]
        for col in df.columns[1:]:
            pos = str(row[col]).strip()
            if pos and pos != 'nan':
                trna[pos] = struct_name
    return trna

def load_chrm():
    """加载线粒体参考基因组（修正3107位N为C，R脚本逻辑）"""
    chrm_seq = []
    with open(CHRM_DATA, 'r') as f:
        for line in f:
            if line.startswith('>'):
                continue
            chrm_seq.append(line.strip().upper())
    ref_base = list(''.join(chrm_seq))
    if len(ref_base) >= 3107:
        ref_base[3106] = 'C'  # 0-based索引
    return ref_base

def load_dloop():
    """加载D-loop区域数据（位置对应区域名称，R脚本逻辑）"""
    dloop = {}
    df = pd.read_csv(DLOOP_DATA, sep='\t', header=0)
    for _, row in df.iterrows():
        try:
            start = int(row['Starting'])
            end = int(row['Ending'])
            locus = row['Map.Locus']
            for pos in range(start, end + 1):
                if pos not in dloop:
                    dloop[pos] = []
                dloop[pos].append(locus)
        except (ValueError, KeyError):
            continue
    # 去重并转换为逗号分隔字符串
    for pos in dloop:
        dloop[pos] = ','.join(list(set(dloop[pos])))
    return dloop

def load_annotation_data():
    """加载mitimpact相关注释数据（PolyPhen2等）"""
    # 加载mitimpact_2.0.txt
    if not os.path.exists(MIT20_PATH):
        print(f"错误：mitimpact_2.0.txt 不存在！路径：{MIT20_PATH}")
        sys.exit(1)
    df_mit20 = pd.read_csv(
        MIT20_PATH, sep="\t", header=0, dtype={"Start": int, "Ref": str, "Alt": str}
    ).rename(columns={"Start": "pos", "Ref": "ref", "Alt": "alt"}, inplace=False)
    df_mit20_selected = df_mit20[
        ["pos", "ref", "alt", "PolyPhen2", "PolyPhen2_score", "MutationAssessor", "MutationAssessor_score"]
    ].drop_duplicates(subset=["pos", "ref", "alt"], keep="first")

    # 加载mitimpact.txt
    if not os.path.exists(MIT_PATH):
        print(f"错误：mitimpact.txt 不存在！路径：{MIT_PATH}")
        sys.exit(1)
    df_mit = pd.read_csv(
        MIT_PATH, sep="\t", header=None, names=["pos", "ref", "alt", "mit_impact"],
        dtype={"pos": int, "ref": str, "alt": str}
    ).drop_duplicates(subset=["pos", "ref", "alt"], keep="first")

    return df_mit20_selected, df_mit

def find_target_mutation_files(original_dir):
    """查找符合条件的突变文件（*1.txt 或 *end10*.txt），并按类型分组"""
    pattern1 = os.path.join(original_dir, "*1.txt")
    pattern2 = os.path.join(original_dir, "*end10*.txt")
    all_matched_files = list(set(glob.glob(pattern1) + glob.glob(pattern2)))

    # 过滤空文件
    valid_files = []
    for file in all_matched_files:
        if is_empty_file(file):
            print(f"⚠️ 跳过空文件：{os.path.basename(file)}")
            continue
        valid_files.append(file)

    if len(valid_files) == 0:
        print(f"❌ 未找到符合条件的非空文件！支持：*1.txt 或 *end10*.txt")
        sys.exit(1)
    
    # 按文件类型分组（1.txt 组 / end10.txt 组）
    file_groups = {
        "type1": [],  # *1.txt
        "type2": []   # *end10*.txt
    }
    for file in valid_files:
        basename = os.path.basename(file)
        if basename.endswith("1.txt") and "end10" not in basename:
            file_groups["type1"].append(file)
        elif "end10" in basename:
            file_groups["type2"].append(file)
    
    # 过滤空组
    file_groups = {k: v for k, v in file_groups.items() if v}
    return file_groups

def get_sample_info(filename):
    """根据文件名获取样本类型和阈值（Perl脚本kind和thresh逻辑）"""
    base = os.path.basename(filename)
    # 判断样本类型
    if 'shift' in base:
        sample_type = 'shift'
    elif 'germline' in base:
        sample_type = 'germline'
    elif 'somatic' in base:
        sample_type = 'somatic'
    elif 'hetro' in base:
        sample_type = 'hetro'
    else:
        sample_type = 'homo'
    # 判断阈值
    threshold = 0.5 if '0.5' in base else 2
    return sample_type, threshold

def parse_exon_file(exon_file):
    """解析ANNOVAR外显子变异文件（提取mRNA、蛋白变化，Perl脚本_exon逻辑）"""
    exon_var = {}
    if not os.path.exists(exon_file) or is_empty_file(exon_file):
        return exon_var
        
    with open(exon_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split('\t')
            if len(parts) < 8:
                continue
            pos, ref, alt, syn, gene_info = parts[5], parts[6], parts[7], parts[1], parts[2]
            syn = syn.split()[0] if syn else ""
            gene_parts = gene_info.split(':')
            if len(gene_parts) < 3:
                continue
            gene, mrna, pro = gene_parts[0], gene_parts[-2], gene_parts[-1]
            # 清理格式（去除c.和p.前缀）
            mrna = mrna.replace('c.', '', 1).upper() if mrna.startswith('c.') else mrna
            pro = pro.replace('p.', '', 1).upper() if pro.startswith('p.') else pro
            exon_var[f"{pos}\t{ref}\t{alt}"] = f"{gene}\t{syn}\t{mrna}\t{pro}"
    return exon_var

def process_annovar(input_file, temp_dir, pos_col_idx, ref_col_idx, alt_col_idx, delimiter):
    """运行ANNOVAR进行基因注释（Perl脚本核心逻辑）"""
    # 再次检查输入文件是否为空（双重保障）
    if is_empty_file(input_file):
        print(f"⚠️ 跳过ANNOVAR处理：{os.path.basename(input_file)} 是空文件")
        return None, None, 0
        
    base_name = os.path.basename(input_file)
    temp_input = os.path.join(temp_dir, f"temp_{base_name}")
    original_cols = 0

    # 生成ANNOVAR输入格式文件
    with open(input_file, 'r') as in_f, open(temp_input, 'w') as out_f:
        header_skipped = False
        for line in in_f:
            line = line.strip()
            if not line:
                continue
            # 跳过表头
            if not header_skipped:
                first_line = line.split(delimiter)
                is_header = any(str(x).lower() in ["pos", "position", "ref", "alt"] for x in first_line[:3])
                if is_header:
                    header_skipped = True
                    continue
                header_skipped = True
            # 提取核心信息并写入
            parts = line.split(delimiter)
            original_cols = max(original_cols, len(parts))
            pos = parts[pos_col_idx].strip()
            ref = parts[ref_col_idx].strip()
            alt = parts[alt_col_idx].strip()
            out_f.write(f"MT\t{pos}\t{pos}\t{ref}\t{alt}\t" + '\t'.join(parts) + f"\tORIGINAL_COLS={original_cols}\n")
    
    # 运行ANNOVAR
    try:
        check_call([
            "perl", ANNOTATE_SCRIPT, "-buildver", "GRCh37_MT", "-dbtype", "ensGene",
            temp_input, HUMANDB, "-outfile", os.path.join(temp_dir, f"annovar_temp_{base_name}")
        ])
    except CalledProcessError as e:
        print(f"❌ ANNOVAR运行失败：{e}")
        return None, None, 0

    variant_file = os.path.join(temp_dir, f"annovar_temp_{base_name}.variant_function")
    exon_file = os.path.join(temp_dir, f"annovar_temp_{base_name}.exonic_variant_function")
    return variant_file, exon_file, original_cols

def read_mutation_data(file_path, pos_col):
    """读取突变数据（自动识别分隔符+表头，支持指定pos列）"""
    # 检查文件是否为空
    if is_empty_file(file_path):
        print(f"⚠️ 跳过读取：{os.path.basename(file_path)} 是空文件")
        return None, None, None, None, None
        
    tab_char = '\t'
    comma_char = ','
    space_char = ' '
    delimiter = detect_delimiter(file_path)

    # 输出分隔符信息
    delimiter_desc = {tab_char: "制表符", comma_char: "逗号", space_char: "空格"}.get(delimiter, "未知分隔符")
    print(f"🔍 自动检测到{os.path.basename(file_path)}分隔符：{delimiter_desc}")

    # 计算列索引（1-based转0-based）
    pos_col_idx = pos_col - 1
    ref_col_idx = pos_col_idx + 1
    alt_col_idx = pos_col_idx + 2

    try:
        # 读取数据
        if delimiter == space_char:
            df_raw = pd.read_csv(file_path, sep=r'\s+', header=None, engine='python')
        else:
            df_raw = pd.read_csv(file_path, sep=delimiter, header=None)

        # 检查列数是否足够
        if len(df_raw.columns) < alt_col_idx + 1:
            print(f"❌ {os.path.basename(file_path)}列数不足！需要至少 {alt_col_idx + 1} 列（pos列：{pos_col}，ref列：{pos_col+1}，alt列：{pos_col+2}）")
            print(f"   当前文件实际列数：{len(df_raw.columns)}")
            return None, None, None, None, None

        # 判断并跳过表头
        first_line = df_raw.iloc[0].tolist()
        is_header = False
        for idx in [pos_col_idx, ref_col_idx, alt_col_idx]:
            val = str(first_line[idx]).lower()
            if val in ["pos", "position", "ref", "reference", "alt", "alternative", "variant"]:
                is_header = True
                break
        if not is_header:
            for idx in [pos_col_idx, ref_col_idx, alt_col_idx]:
                val = str(first_line[idx])
                if any(c.isalpha() for c in val) and not val.isdigit():
                    is_header = True
                    break
        if is_header:
            df_raw = df_raw.iloc[1:].reset_index(drop=True)
            print(f"✅ {os.path.basename(file_path)}检测到表头，已自动跳过")

        # 处理pos列格式
        df_raw[pos_col_idx] = pd.to_numeric(df_raw[pos_col_idx], errors='coerce')
        df_raw = df_raw.dropna(subset=[pos_col_idx])
        df_raw[pos_col_idx] = df_raw[pos_col_idx].astype(int)

        # 检查处理后是否还有有效数据
        if len(df_raw) == 0:
            print(f"⚠️ {os.path.basename(file_path)}无有效突变数据，跳过")
            return None, None, None, None, None

        # 重命名核心列
        col_names = list(df_raw.columns)
        col_names[pos_col_idx] = "pos"
        col_names[ref_col_idx] = "ref"
        col_names[alt_col_idx] = "alt"
        # 非核心列命名为colX
        new_col_names = []
        for idx, col in enumerate(col_names):
            if col in ["pos", "ref", "alt"]:
                new_col_names.append(col)
            else:
                new_col_names.append(f"col{idx+1}")
        df_raw.columns = new_col_names

        # 清理ref/alt列空格
        df_raw['ref'] = df_raw['ref'].astype(str).str.strip()
        df_raw['alt'] = df_raw['alt'].astype(str).str.strip()

        # 添加文件名标识列（用于溯源）
        df_raw['source_file'] = os.path.basename(file_path)

        print(f"✅ 读取成功：{os.path.basename(file_path)} - {len(df_raw)} 条有效突变数据")
        return df_raw, pos_col_idx, ref_col_idx, alt_col_idx, delimiter

    except Exception as e:
        print(f"❌ {os.path.basename(file_path)}数据读取失败：{str(e)}")
        return None, None, None, None, None

def process_single_file(file_path, pos_col, temp_dir, annotation_dbs):
    """处理单个文件的注释逻辑，返回注释后的DataFrame"""
    # 先检查文件是否为空
    if is_empty_file(file_path):
        print(f"⚠️ 跳过处理：{os.path.basename(file_path)} 是空文件")
        return None
        
    # 解包注释数据库
    dbsnp, mitomap, disease, assessor, trna, ref_base, dloop, df_mit20, df_mit = annotation_dbs
    
    # 读取原始数据
    read_result = read_mutation_data(file_path, pos_col)
    if read_result[0] is None:  # 读取失败或无有效数据
        return None
    original_df, pos_col_idx, ref_col_idx, alt_col_idx, delimiter = read_result
    
    sample_name = os.path.splitext(os.path.basename(file_path))[0]
    sample_type, threshold = get_sample_info(file_path)

    # 运行ANNOVAR注释
    print(f"📝 运行ANNOVAR注释：{os.path.basename(file_path)}")
    variant_file, exon_file, original_cols = process_annovar(
        file_path, temp_dir, pos_col_idx, ref_col_idx, alt_col_idx, delimiter
    )
    if not variant_file or not os.path.exists(variant_file) or is_empty_file(variant_file):
        print(f"❌ {os.path.basename(file_path)} ANNOVAR注释结果不存在或为空！")
        return None

    # 解析外显子变异信息
    exon_var = parse_exon_file(exon_file) if exon_file else {}

    # 整合所有注释信息
    print(f"📝 整合{os.path.basename(file_path)}注释数据...")
    results = []
    for _, row in original_df.iterrows():
        pos = int(row['pos'])
        ref = row['ref']
        alt = row['alt']
        pos_str = str(pos)
        key = f"{pos_str}\t{ref}\t{alt}"

        # 6.1 基因区域判断（Perl脚本逻辑）
        gene = ""
        if 1 <= pos <= 576:
            gene = "D_loop_1"
        elif 16024 <= pos <= 16569:
            gene = "D_loop_2"
        else:
            # 从ANNOVAR结果中补充基因信息
            with open(variant_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    parts = line.split('\t')
                    if len(parts) >= 5 and parts[4] == pos_str:
                        gene = parts[1].strip()
                        if 'upstream' in parts[0].lower() or 'downstream' in parts[0].lower():
                            gene = 'gap'
                        break

        # 6.2 基础注释（dbSNP+MITOMAP+疾病）
        rs_id = dbsnp.get(key, ".")
        mitomap_flag = 1 if key in mitomap else 0
        disease_info = disease.get(key, ".")

        # 6.3 外显子变异注释（mRNA+蛋白变化）
        syn, mrna_change, protein_change = ".", ".", "."
        if key in exon_var:
            _, syn, mrna_change, protein_change = exon_var[key].split('\t')

        # 6.4 MutationAssessor注释（R脚本逻辑）
        func_impact = assessor.get(key, {}).get('Func_Impact', ".")
        fi_score = assessor.get(key, {}).get('FI_score', ".")

        # 6.5 参考碱基修正+三碱基上下文（R脚本核心逻辑）
        ref_corrected = ref
        if 0 < pos <= len(ref_base):
            # 修正参考碱基（若不一致）
            if ref_base[pos-1] != ref:
                print(f"⚠️ 参考碱基修正：样本{sample_name} pos{pos} 原ref={ref} → 基因组ref={ref_base[pos-1]}")
                ref_corrected = ref_base[pos-1]
            # 三碱基上下文（前+当前+后）
            prev = ref_base[pos-2] if pos-2 >= 0 else ""
            curr = ref_base[pos-1]
            next_b = ref_base[pos] if pos < len(ref_base) else ""
            ref_tri = f"{prev}{curr}{next_b}"
            alt_tri = f"{prev}{alt}{next_b}"
        else:
            ref_tri = "."
            alt_tri = "."

        # 6.6 D-loop区域注释（R脚本逻辑）
        dloop_region = dloop.get(pos, " ")

        # 6.7 tRNA结构注释（R脚本空格填充逻辑）
        tRNA_info = trna.get(pos_str, " ")

        # 6.8 mitimpact注释（PolyPhen2等）
        polyphen2 = "."
        polyphen2_score = "."
        ma_mitimpact = "."
        ma_score_mitimpact = "."
        mit_impact = "."
        # 从mitimpact_2.0匹配
        match_mit20 = df_mit20[(df_mit20['pos'] == pos) & (df_mit20['ref'] == ref_corrected) & (df_mit20['alt'] == alt)]
        if not match_mit20.empty:
            polyphen2 = match_mit20.iloc[0]['PolyPhen2']
            polyphen2_score = match_mit20.iloc[0]['PolyPhen2_score']
            ma_mitimpact = match_mit20.iloc[0]['MutationAssessor']
            ma_score_mitimpact = match_mit20.iloc[0]['MutationAssessor_score']
        # 从mitimpact匹配
        match_mit = df_mit[(df_mit['pos'] == pos) & (df_mit['ref'] == ref_corrected) & (df_mit['alt'] == alt)]
        if not match_mit.empty:
            mit_impact = match_mit.iloc[0]['mit_impact']

        # 整合一行结果（原始列 + 所有注释列）
        original_data = row.drop(['pos', 'ref', 'alt']).tolist()
        result_row = [pos, ref_corrected, alt] + original_data + [
            gene, rs_id, str(mitomap_flag), disease_info,
            syn, mrna_change, protein_change,
            func_impact, fi_score,
            ref_tri, alt_tri,
            dloop_region, tRNA_info,
            polyphen2, polyphen2_score,
            ma_mitimpact, ma_score_mitimpact,
            mit_impact, sample_name, sample_type
        ]
        results.append(result_row)

    # 检查是否有结果数据
    if len(results) == 0:
        print(f"⚠️ {os.path.basename(file_path)}无注释结果，跳过")
        return None

    # 构建列名
    original_col_names = [col for col in original_df.columns if col not in ["pos", "ref", "alt"]]
    annotation_col_names = [
        "pos", "ref_corrected", "alt",  # 核心列（ref已修正）
        *original_col_names,            # 原始其他列
        "Gene_Region", "rs_ID", "MITOMAP_Flag", "Disease_Info",
        "Variant_Type", "mRNA_Change", "Protein_Change",
        "MA_Func_Impact", "MA_FI_Score",
        "Ref_Triple_Base", "Alt_Triple_Base",
        "Dloop_Region", "tRNA_Structure",
        "PolyPhen2", "PolyPhen2_Score",
        "MITIMPACT_MA", "MITIMPACT_MA_Score",
        "MIT_IMPACT", "Sample_Name", "Sample_Type"
    ]

    # 生成最终DataFrame
    final_df = pd.DataFrame(results, columns=annotation_col_names)
    final_df.fillna(".", inplace=True)  # 缺失值用.填充
    return final_df

def main():
    # 命令行参数检查
    if len(sys.argv) != 3:
        print("✅ 正确用法：python3 mt_annotation.py [突变文件文件夹] [pos列（1-based）]")
        print("📌 示例：python3 mt_annotation.py /mnt/data/demo 2")
        print("💡 支持：自动识别分隔符、多文件分组合并、完整注释功能、空文件自动跳过")
        sys.exit(1)

    original_dir = sys.argv[1]
    try:
        pos_col = int(sys.argv[2])
        if pos_col < 1:
            raise ValueError
    except ValueError:
        print("❌ pos列必须是正整数！")
        sys.exit(1)

    if not os.path.isdir(original_dir):
        print(f"❌ {original_dir} 不是有效目录！")
        sys.exit(1)

    # 创建临时目录和输出目录
    temp_dir = os.path.join(original_dir, "temp_annotation")
    output_dir = os.path.join(original_dir, "annotation")
    os.makedirs(temp_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    try:
        # 1. 加载所有注释数据库（仅加载一次，提高效率）
        print("🔄 加载注释数据库...")
        dbsnp = load_dbsnp()
        mitomap = load_mitomap()
        disease = load_disease()
        assessor = load_assessor()
        trna = load_trna()
        ref_base = load_chrm()
        dloop = load_dloop()
        df_mit20, df_mit = load_annotation_data()
        annotation_dbs = (dbsnp, mitomap, disease, assessor, trna, ref_base, dloop, df_mit20, df_mit)

        # 2. 查找目标文件并按类型分组（已过滤空文件）
        file_groups = find_target_mutation_files(original_dir)
        print(f"\n📁 检测到文件分组：{list(file_groups.keys())}")
        for group_type, files in file_groups.items():
            print(f"   {group_type}：{[os.path.basename(f) for f in files]}")

        # 3. 按分组处理文件并合并
        for group_type, files in file_groups.items():
            print(f"\n========== 处理{group_type}组文件 ==========")
            merged_df = None
            
            # 处理组内每个文件
            for file in files:
                file_df = process_single_file(file, pos_col, temp_dir, annotation_dbs)
                if file_df is None:
                    print(f"⚠️ 跳过{os.path.basename(file)}：注释失败或无有效数据")
                    continue
                
                # 合并DataFrame
                if merged_df is None:
                    merged_df = file_df
                else:
                    # 确保列名一致后合并
                    merged_df = pd.concat([merged_df, file_df], ignore_index=True)

            # 保存合并后的文件
            if merged_df is not None and len(merged_df) > 0:
                # 确定输出文件名
                if group_type == "type1":
                    output_filename = "merged_type1_1txt_annotation.txt"
                else:  # type2
                    output_filename = "merged_type2_end10txt_annotation.txt"
                output_path = os.path.join(output_dir, output_filename)
                
                # 保存文件
                merged_df.to_csv(output_path, sep='\t', index=False, header=True, encoding="utf-8")
                
                # 输出分组统计
                print(f"\n🎉 {group_type}组处理完成！")
                print(f"📊 分组统计：")
                print(f"   - 处理文件数：{len(files)} 个")
                print(f"   - 合并后总突变数：{len(merged_df)} 条")
                print(f"💾 合并文件路径：{output_path}")
            else:
                print(f"\n⚠️ {group_type}组无有效注释数据，跳过保存")

    finally:
        # 清理临时目录
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            print("\n🗑️ 临时文件已清理")

if __name__ == "__main__":
    main()
