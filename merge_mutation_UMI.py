import sys
import os
import pandas as pd

def main(folder_path):
    # Initialize lists to hold data for sscs and dcs
    sscs_data = []
    dcs_data = []
    
    # Headers will be set from the first file encountered
    headers = None
    new_headers = ['Source File', 'Sample Name', 'Mutation Type']
    
    # Traverse all subfolders
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.snp_indel.anno.xls'):
                full_path = os.path.join(root, file)
                filename = file  # Just the filename
                
                # Determine type
                parts = filename.split('.')
                if len(parts) < 3:
                    continue  # Invalid filename format
                sample_name = parts[0]
                mutation_type = parts[1]
                
                if mutation_type not in ['sscs', 'dcs']:
                    continue  # Skip if not sscs or dcs
                
                # Read the file as TSV, since .xls is likely tab-delimited text
                df = pd.read_csv(full_path, sep='\t')
                
                # If headers not set, set them
                if headers is None:
                    headers = df.columns.tolist()
                    full_headers = new_headers + headers
                
                # Get data rows (all rows after header, but since read_csv uses first as header, df has data)
                data_rows = df.values.tolist() if not df.empty else []
                
                # Add new columns to data rows
                augmented_rows = []
                for row in data_rows:
                    augmented_rows.append([filename, sample_name, mutation_type] + row)
                
                # Append to appropriate list
                if mutation_type == 'sscs':
                    sscs_data.extend(augmented_rows)
                elif mutation_type == 'dcs':
                    dcs_data.extend(augmented_rows)
    
    # If no data, exit
    if not headers:
        print("No valid files found.")
        return
    
    # Create DataFrames
    sscs_df = pd.DataFrame([full_headers] + sscs_data) if sscs_data else pd.DataFrame(columns=full_headers)
    dcs_df = pd.DataFrame([full_headers] + dcs_data) if dcs_data else pd.DataFrame(columns=full_headers)
    
    # Write to Excel
    output_file = 'UMI_merged_mutations.xlsx'
    with pd.ExcelWriter(output_file) as writer:
        sscs_df.to_excel(writer, sheet_name='sscs', index=False, header=False)  # Header already included
        dcs_df.to_excel(writer, sheet_name='dcs', index=False, header=False)
    
    print(f"Output written to {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 script.py <folder_path>")
        sys.exit(1)
    main(sys.argv[1])
