#!/usr/bin/python

import os

ID_2thbarcode = open('/mnt/data2/suliping-capture-contaminnation/barcode.txt')
ID_barcode_seq = {}
for i in ID_2thbarcode:
    i = i.strip().split('\t')
    ID_barcode_seq[i[0]] = i[1]
ID_2thbarcode.close()

Sample_ID = open('/mnt/data2/suliping-capture-contaminnation/name.info')
patient_ID = {}
for i in Sample_ID:
    i = i.strip().split(' ')
    patient_ID[i[0]] = i[1]
Sample_ID.close()

sample_seq = {}
for k,v in patient_ID.items():
    sample_seq[k] = ID_barcode_seq[v]

f = open('/mnt/data2/suliping-capture-contaminnation/sample_name.txt')
for i in f:
    i = i.strip()
    R1 = open('/mnt/data2/suliping-capture-contaminnation/' + i + '/' + i + '_R1.fq').readlines()
    R2 = open('/mnt/data2/suliping-capture-contaminnation/' + i + '/' + i + '_R2.fq').readlines()
    R1filter = open('/mnt/data2/suliping-capture-contaminnation/' + i + '/' + i + '_filtered_R1.fq','a')
    R2filter = open('/mnt/data2/suliping-capture-contaminnation/' + i + '/' + i + '_filtered_R2.fq','a')
    R1removed = open('/mnt/data2/suliping-capture-contaminnation/' + i + '/' + i + '_removed_R1.fq','a')
    R2removed = open('/mnt/data2/suliping-capture-contaminnation/' + i + '/' + i + '_removed_R2.fq','a')

    for j in range(0,len(R1),4):
        read_info_R1 = R1[j:j+4]
        read_name_R1 = read_info_R1[0]
        read_seq_R1 = read_info_R1[1]
        plus_R1 = read_info_R1[2]
        q_value_R1 = read_info_R1[3]
        second_barcode_R1 = read_seq_R1[0:6]
        read_info_R2 = R2[j:j+4]
        read_name_R2 = read_info_R2[0]
        read_seq_R2 = read_info_R2[1]
        plus_R2 = read_info_R2[2]
        q_value_R2 = read_info_R2[3]
        second_barcode_R2 = read_seq_R2[0:6]

        if second_barcode_R1 == second_barcode_R1:
            R1filter.write(read_name_R1)
            R1filter.write(read_seq_R1[7:])
            R1filter.write(plus_R1)
            R1filter.write(q_value_R1[7:])
            R2filter.write(read_name_R2)
            R2filter.write(read_seq_R2[7:])
            R2filter.write(plus_R2)
            R2filter.write(q_value_R2[7:])
        else:
            R1removed.write(read_name_R1)
            R1removed.write(read_seq_R1[7:])
            R1removed.write(plus_R1)
            R1removed.write(q_value_R1[7:])
            R2removed.write(read_name_R2)
            R2removed.write(read_seq_R2[7:])
            R2removed.write(plus_R2)
            R2removed.write(q_value_R2[7:])

    R1filter.close()
    R1removed.close()
    R2filter.close()
    R2removed.close()

f.close()

