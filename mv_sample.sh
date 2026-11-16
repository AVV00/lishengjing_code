#!/bin/bash

# 
destination_folder=$(cd "$(dirname "$0")" && pwd)

# 
while IFS=$'\t' read -r sample_name sample_path; do
  echo "$destination_folder/$sample_name"
  # 
  mkdir -p "$destination_folder/$sample_name"
  
  # 
  subfolder_path="$sample_path/$sample_name"
  
  find "$subfolder_path" -type f -name "*realn.bam" -exec cp {} "$destination_folder/$sample_name/" \;
  #find "$subfolder_path" -type f -name "*good.fq.gz" -exec cp {} "$destination_folder/$sample_name/" \;
done < samples.txt

