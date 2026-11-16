#!/bin/bash

#
destination_folder="/mnt/data2/lishengjing/12_numt_20240828/"

mkdir -p "$destination_folder/reads/nuclear_proper"
mkdir -p "$destination_folder/reads/nuclear_second"
mkdir -p "$destination_folder/reads/proper_NO2_chrM"
mkdir -p "$destination_folder/reads/second_chrM"

cp ./*/*nuclear.proper.reads.txt "$destination_folder/reads/nuclear_proper"
cp ./*/*nuclear.second.reads.txt "$destination_folder/reads/nuclear_second"
cp ./*/*proper.NO2.chrM.reads.txt "$destination_folder/reads/proper_NO2_chrM"
cp ./*/*second.chrM.reads.txt "$destination_folder/reads/second_chrM"

python3 /mnt/hdd/usr/lishengjing/Code/merge_numt_reads.py "$destination_folder/reads/nuclear_proper" "$destination_folder/reads/nuclear_proper.txt"
python3 /mnt/hdd/usr/lishengjing/Code/merge_numt_reads.py "$destination_folder/reads/nuclear_second" "$destination_folder/reads/nuclear_second.txt"
python3 /mnt/hdd/usr/lishengjing/Code/merge_numt_reads.py "$destination_folder/reads/proper_NO2_chrM" "$destination_folder/reads/proper_NO2_chrM.txt"
python3 /mnt/hdd/usr/lishengjing/Code/merge_numt_reads.py "$destination_folder/reads/second_chrM" "$destination_folder/reads/second_chrM.txt"
python3 /mnt/hdd/usr/lishengjing/Code/merge_numt_result.py "$destination_folder/reads/nuclear_proper.txt" "$destination_folder/reads/nuclear_second.txt" "$destination_folder/reads/proper_NO2_chrM.txt" "$destination_folder/reads/second_chrM.txt" "$destination_folder/reads/merge_numt_result.txt"
