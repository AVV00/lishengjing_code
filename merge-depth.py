import os
import pandas as pd
import sys


def process_depth_files(input_folder, output_folder):

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"make dir {output_folder}")

    depth_files = [f for f in os.listdir(input_folder) if f.endswith('.depth') or f.endswith('.depth.stat')]
    if not depth_files:
        print(f"There is no depth file in '{input_folder}'")
        return

    print(f"find {len(depth_files)} depth file, start precessing...")

    all_positions = pd.DataFrame({'Position': range(1, 17120)})
    merged_df_17119 = all_positions.copy()

    for filename in depth_files:
        filepath = os.path.join(input_folder, filename)

        try:
            df = pd.read_csv(filepath, sep='\t', header=None, names=['Chromosome', 'Position', 'Depth'])
            #chrm_df = df[df['Chromosome'] == 'chrM'][['Position', 'Depth']]
            chrm_df = df[df['Chromosome'].isin(['chrM', 'MT'])][['Position', 'Depth']]
            sample_name = os.path.splitext(filename)[0]
            chrm_df = chrm_df.rename(columns={'Depth': sample_name})

            merged_df_17119 = pd.merge(merged_df_17119, chrm_df, on='Position', how='left')

        except Exception as e:
            print(f"precess  {filename} error: {e}")
            continue

    merged_df_17119 = merged_df_17119.fillna(0)

    for col in merged_df_17119.columns:
        if col != 'Position':
            merged_df_17119[col] = merged_df_17119[col].astype(int)

    output_path_17119 = os.path.join(output_folder, 'combine_depth_17119.txt')
    merged_df_17119.to_csv(output_path_17119, sep='\t', index=False)

    df_17119_indexed = merged_df_17119.set_index('Position')

    head_depth = df_17119_indexed.loc[1:550]
    tail_depth = df_17119_indexed.loc[16570:17119]

    tail_depth.index = range(1, 551)

    adjusted_head_depth = head_depth + tail_depth

    merged_df_16569 = df_17119_indexed.loc[1:16569].copy()
    merged_df_16569.loc[1:550] = adjusted_head_depth

    output_path_16569 = os.path.join(output_folder, 'combine_depth_16569.txt')
    merged_df_16569.reset_index().to_csv(output_path_16569, sep='\t', index=False)

    average_depths = merged_df_16569.mean().reset_index()
    average_depths.columns = ['Sample', 'Average_Depth']

    output_path_avg = os.path.join(output_folder, 'average_depth.txt')
    average_depths.to_csv(output_path_avg, sep='\t', index=False)
    print(f"Seccess output: {output_path_avg}")

    print("\nFinished")


if __name__ == '__main__':
    input_directory = sys.argv[1]

    output_directory = sys.argv[2]

    # ------------------------------------

    if not os.path.isdir(input_directory):
        print(f"erroe: input dir path '{input_directory}' is none or is not a dir")
    else:
        process_depth_files(input_directory, output_directory)
