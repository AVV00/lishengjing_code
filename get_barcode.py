#!/usr/bin/python
#coding:gbk

import os
import gzip
dir_path='/mnt/data2/Seq_data/20240509/'
f = open(dir_path + 'Combine_Analysis_rCRS-hg19-DNA_V1/sample_name.txt')
barcodes = open(dir_path + 'Combine_Analysis_rCRS-hg19-DNA_V1/'  + 'get_barcode.txt','a')

barcodes.write('sample'+'\t'+'R1 barcode'+'\t'+'R2 barcode'+'\t'+'R1 barcode freq'+'\t'+'R2 barcode freq'+'\t'+'R1 file size(M)'+'\n')    #get_barcode.txt header
fetch_read_number = 1000

for i in f:
    i = i.strip()
    R1=[];
    R2=[];
    num=0
    
    R1filename= dir_path + 'Rawdata/'  + i + '/' + i + '_R1.fq.gz'
    R2filename= dir_path + 'Rawdata/'  + i + '/' + i + '_R2.fq.gz'
    
    
    with gzip.open(R1filename,'rb') as f:
            for line in f:
                line=line.decode()
                num=num+1
                R1.append(''.join(line.strip('\n').split('\n'))) 
                if(num==fetch_read_number*4):
                    break
    num=0
    with gzip.open(R2filename,'rb') as f:
            for line in f:
                num=num+1
                line=line.decode()
                R2.append(''.join(list(line.strip('\n').split('\n')))) 
                if(num==fetch_read_number*4):
                    break
    R1_barcode_array=[]
    R2_barcode_array=[]
    k=0
    for j in range(0,len(R1),4):
        k=k+1
        read_info_R1 = R1[j:j+4]                   #R1 reads的四行信息
        read_seq_R1 = read_info_R1[1]              #ATCG序列信息
        second_barcode_R1 = read_seq_R1[0:6]       #序列的前6个碱基
        read_info_R2 = R2[j:j+4]                   #R2 reads的四行信息
        read_seq_R2 = read_info_R2[1]              
        second_barcode_R2 = read_seq_R2[0:6]      
        R1_barcode_array.append(second_barcode_R1) #R1barcode添加到数组中，数组中包含n个reads序列的barcode
        R2_barcode_array.append(second_barcode_R2)
        if(k==fetch_read_number):                  #设置只查看前fetch_read_number条的reads中的barcode序列，选出现最多的barcode作为样本的barcode
            break
    R1barcode=max(R1_barcode_array, key=R1_barcode_array.count)  #R1中数量最多的barcode
    R2barcode=max(R2_barcode_array, key=R2_barcode_array.count)
    
    #计算barcode在fetch_read_number中出现的频率
    R1barcode_freq_array = {}
    R2barcode_freq_array = {}
    for x in R1_barcode_array :
        R1barcode_freq_array[x] = R1barcode_freq_array.get(x, 0) + 1
    for x in R2_barcode_array :
        R2barcode_freq_array[x] = R2barcode_freq_array.get(x, 0) + 1
    R1barcode_freq=str(float(R1barcode_freq_array[R1barcode])/fetch_read_number)
    R2barcode_freq=str(float(R2barcode_freq_array[R2barcode])/fetch_read_number)   
    
    #计算fq文件大小,M为单位
    size1=str(round(os.path.getsize(R1filename)/float(1024*1024),2))
    #size2=str(round(os.path.getsize(R2filename)/float(1024*1024),2))
    
    barcodes.write(i+'\t'+R1barcode+'\t'+R2barcode+'\t'+R1barcode_freq+'\t'+R2barcode_freq+'\t'+size1+'\n')         #保存文件
barcodes.close()
f.close()
