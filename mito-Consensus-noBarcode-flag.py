import pysam
import click
import os
import sys
import pickle
import numpy as np
import pandas as pd
from progress.bar import Bar
from collections import defaultdict


usage='''
mitoConsensus.py
This script perfrom consensus variant calling, 
Syntax: mitoConsensus <sample> <out_dir> <barcode_tag> <BaseQ_thld_hi>

Inputs
---
sample: The prefix, should be barcodes.# check the prefix of /temp/barcoded_bams/ for example. REQUIRED
out_dir: The folder of the whole analysis. It is usually called CW_mgatk, under which you could find temp, final, etc REQUIRED.
barcode_tag: The tag name in bam file, which is BC by 10X system
BaseQ_thld_hi: The base quality score threadhold, which is usually set as 30

output:
-------
Generate 4 *.RawGenotypes outputs + 1 *.QualifiedTotalCts with 4 columns output

Acknowledgment:
---------------
Inherited some of the codes from https://github.com/caleblareau/mgatk by Caleb Lareau et al. 
'''
if len(sys.argv)<4:
    print("Argument missing")
    print(usage)
    quit()
########## Section 1, define argument and constant and read files
##########

dna_letters = ['A','C','G','T','N']
##Take argument from command line
sample=sys.argv[1] #The prefix, should be barcodes.# check the prefix of /temp/barcoded_bams/ for example. REQUIRED
bam_file=sys.argv[2]
out_dir=sys.argv[3] #The folder of the whole analysis. It is usually called CW_mgatk, under which you could find temp, final, etc REQUIRED.
BaseQ_thld_hi=int(sys.argv[4]) ## It is usually set as 30


out_genotypeTotal_file=out_dir + "/"+sample+ "/"+sample+".RawGenotypes.Total"
out_genotypeVerySensitive_file=out_dir + "/"+sample+ "/"+sample+".RawGenotypes.VerySensitive"
out_genotypeSensitive_file=out_dir + "/"+sample+ "/"+sample+".RawGenotypes.Sensitive"
out_genotypeSpecific_file=out_dir + "/"+sample+ "/"+sample+".RawGenotypes.Specific"
out_totalCts_file=out_dir + "/"+sample+ "/"+sample+".QualifiedTotalCts"
#bam_file =out_dir + "/"+sample+ "/"+sample+".bam"  ## For example "temp/barcoded_bams/barcodes.1.bam"
mito_ref_file =r"/mnt/hdd/usr/lishengjing/Code/chrM_refAllele.txt"
flag_file=out_dir + "/"+sample+ "/"+sample+".flag"

#===========读取参考基因组=============
mito_ref=pd.read_table(mito_ref_file,names=["pos","base"])

max_bp=mito_ref.shape[0]

#===============凑配对reads===================
bam_input = pysam.AlignmentFile(bam_file, "rb")
MoleculeDict=defaultdict(list)
ReadPairDict=defaultdict(list)
FlagDict=defaultdict(list)
for read in bam_input:
    ReadPairDict[read.query_name].append(read)

#==================构建fragment family====================
# Make dictionary from Molecule(Cell_Start_End)-->Rname
for read_name in ReadPairDict:
    # disregard singlets and multiplets
    if len(ReadPairDict[read_name]) != 2:
        continue
    # identify fwd and rev in a pair
    read0, read1 = ReadPairDict[read_name]
    if read0.is_reverse and not read1.is_reverse:
            fwd_read, rev_read = read1, read0
    elif not read0.is_reverse and read1.is_reverse:
            fwd_read, rev_read = read0, read1
    else:
            # disregard a pair if both are the same strand
        continue

    if(fwd_read.tlen>0):
        Molecule=str(fwd_read.pos)+'_'+str(fwd_read.pos+fwd_read.tlen)
    else:
        Molecule=str(fwd_read.pos-fwd_read.tlen)+"_"+str(fwd_read.pos)
    MoleculeDict[Molecule].append(read_name)


#==========构建结果矩阵================
TotalMoleculeCtsMatrix=np.zeros((max_bp,4))  # Matrix to collect 1,Total;Very_sensitive;Sensitive;Specific



#====================构建进度条===================
MolecularN=len(MoleculeDict)
bar = Bar('Genotyping', max=MolecularN)
#==============
for m in MoleculeDict:
    # print(m)
    #CellBC=m.split('_')[0]
    ## Create predefined arrary to collect single and double stranded genotype, both of which are an array, each coloum is a base, A, C, G, T, N; each row is a position
    SG_Genotypes=np.zeros((max_bp,5))
    DB_Genotypes=np.zeros((max_bp,5))
    Strand_mtx=np.zeros((max_bp,2)) ## 0 will be + or forward,  1 will be - or reverse
    flag_mtx = np.zeros((max_bp, 2))

    #=====================构建一致性序列=========================
    for read_pair in MoleculeDict[m]:
        flag_0 = ReadPairDict[read_pair][0].flag
        flag_1 = ReadPairDict[read_pair][1].flag
        FlagDict[m].append(flag_0)
        FlagDict[m].append(flag_1)


    bar.next()

bar.finish()

######### Print out the qualified total counts, aka qualified depth
print("Start to print Qualified Total Molecule Counts")
with open(flag_file,"w") as out_totalCts:
    out_totalCts.write('fragment family\t83\t163\t99\t147\n')
    for m,value in FlagDict.items():
        out_totalCts.write(f'{m}\t')
        a=str(value.count(83))
        b = str(value.count(163))
        c = str(value.count(99))
        d = str(value.count(147))
        out_totalCts.write(f'{a}\t')
        out_totalCts.write(f'{b}\t')
        out_totalCts.write(f'{c}\t')
        out_totalCts.write(f'{d}\t')
        out_totalCts.write('\n')
