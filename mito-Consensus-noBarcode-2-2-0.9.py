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
mito_ref_file = r"/mnt/hdd/usr/lishengjing/Code/chrM_refAllele.txt"
out_genotype_2_2_file=out_dir + "/"+sample+ "/"+sample+".RawGenotypes.2.2.txt"

#===========读取参考基因组=============
mito_ref=pd.read_table(mito_ref_file,names=["pos","base"])

max_bp=mito_ref.shape[0]

#===============凑配对reads===================
bam_input = pysam.AlignmentFile(bam_file, "rb")
MoleculeDict=defaultdict(list)
ReadPairDict=defaultdict(list)
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

#===============打开输出文件===================
## Open the 4 files for write
#out_genotypeTotal=open(out_genotypeTotal_file,"w")
#out_genotypeVerySensitive=open(out_genotypeVerySensitive_file,"w")
#out_genotypeSensitive=open(out_genotypeSensitive_file,"w")
#out_genotypeSpecific=open(out_genotypeSpecific_file,"w")
out_genotype_2_2=open(out_genotype_2_2_file,"w")

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

    #=====================构建一致性序列=========================
    for read_pair in MoleculeDict[m]:
        seq_0=ReadPairDict[read_pair][0].seq
        seq_1=ReadPairDict[read_pair][1].seq
        quality_0=ReadPairDict[read_pair][0].query_qualities
        quality_1=ReadPairDict[read_pair][1].query_qualities
        pos_array_0=np.asarray(ReadPairDict[read_pair][0].get_aligned_pairs(matches_only=True))
        pos_array_1=np.asarray(ReadPairDict[read_pair][1].get_aligned_pairs(matches_only=True))
        pos_array_overlap=np.intersect1d(pos_array_0[:,1],pos_array_1[:,1])
        pos_array_specific_0=pos_array_0[~np.isin(pos_array_0[:,1],pos_array_overlap)]
        pos_array_specific_1=pos_array_1[~np.isin(pos_array_1[:,1],pos_array_overlap)]
        pos_array_overlap_0=pos_array_0[np.isin(pos_array_0[:,1],pos_array_overlap)]
        pos_array_overlap_1=pos_array_1[np.isin(pos_array_1[:,1],pos_array_overlap)]
        ## Collect genotype for the specific_0, or the non-overlapped left part
        if len(pos_array_specific_0)>0: #如果不完全重叠
            for base_0 in pos_array_specific_0:
                if quality_0[base_0[0]]>BaseQ_thld_hi:
                    SG_Genotypes[base_0[1],dna_letters.index(seq_0[base_0[0]])]+=1
                    Strand_mtx[base_0[1],int(ReadPairDict[read_pair][0].is_reverse)]+=1
                else:
                    SG_Genotypes[base_0[1],4]+=1
        ## Collect genotype for the overlap part
        if len(pos_array_overlap)>0: #如果有重叠
            for base_0,base_1 in zip(pos_array_overlap_0,pos_array_overlap_1):
                if (seq_0[base_0[0]]==seq_1[base_1[0]]):
                    if(quality_0[base_0[0]]>BaseQ_thld_hi or quality_1[base_1[0]]>BaseQ_thld_hi):
                        DB_Genotypes[base_0[1],dna_letters.index(seq_0[base_0[0]])]+=1
                        Strand_mtx[base_0[1],0]+=1
                        Strand_mtx[base_0[1],1]+=1
                    else:
                        DB_Genotypes[base_0[1],4]+=1
                # else:  # I figured this step is too confusing and not making sense the DB with conflict is worse then even the SG, not woth it to be included into the DB_Genotypes, maybe we can include those into SG_Genotypes, but here wanted to keep simple
                #     ConflictBases=(seq_0[base_0[0]],seq_1[base_1[0]])
                #     ConflictQ=(quality_0[base_0[0]],quality_1[base_1[0]])
                #     if max(ConflictQ)> BaseQ_thld_hi and min(ConflictQ)< BaseQ_thld_mid:
                #         DB_Genotypes[base_0[1],dna_letters.index(ConflictBases[ConflictQ.index(max(ConflictQ))])]+=1
                #         Strand_mtx[base_0[1],0]+=1
                #         Strand_mtx[base_0[1],1]+=1
                else:
                    DB_Genotypes[base_0[1],4]+=1
        ## Collect genotype for the specific_1, or the non-overlapped right part
        if len(pos_array_specific_1)>0:
            for base_1 in pos_array_specific_1:
                if quality_1[base_1[0]]>BaseQ_thld_hi:
                    SG_Genotypes[base_1[1],dna_letters.index(seq_1[base_1[0]])]+=1
                    Strand_mtx[base_1[1],int(ReadPairDict[read_pair][1].is_reverse)]+=1
                else:
                    SG_Genotypes[base_1[1],4]+=1

    #===================进行突变识别====================
    for i in np.where(np.sum((SG_Genotypes+DB_Genotypes),axis=1)>0)[0]: #遍历fragment覆盖到的位点
        Cur_Genotype_array=(SG_Genotypes+DB_Genotypes)[i][0:4] #（0，0，1，0）
        FamSize=sum(Cur_Genotype_array) #fragement的数量
        if FamSize>0:
            CallIndex=Cur_Genotype_array.tolist().index(max(Cur_Genotype_array)) #占比最高的一个碱基（序列）
            Call=dna_letters[CallIndex] #碱基（字母）
            Ref=mito_ref["base"][i].upper() #参考碱基
            Variant=str(i+1)+"_"+Ref+"_"+Call #位点_参考碱基_该位点碱基
            GT_Cts=Cur_Genotype_array[CallIndex] #（0，0，0，0）中的碱基序列对应的序号
            SG_Cts=SG_Genotypes[i][CallIndex] #（0，1，0，0，0） 中的碱基序列对应的序号
            DB_Cts=DB_Genotypes[i][CallIndex] #（0，0，0，0，1） 中的碱基序列对应的序号
            CSS=GT_Cts/FamSize #占比最多的碱基，占fragemnt数量的占比
            Strand=((Strand_mtx>0).astype(int))[i]
            TotalMoleculeCtsMatrix[i][0]+=1
            OUT=m+"\t"+m.split("_")[0]+"\t"+str(i+1)+"\t"+Variant+"\t"+Call+"\t"+Ref+"\t"+str(FamSize)+"\t"+str(GT_Cts)+"\t"+str(CSS)+"\t"+str(DB_Cts)+"\t"+str(SG_Cts)+"\t"+str(Strand[0])+"\t"+str(Strand[1])+"\n" ## Note those matrix are 0-16568, therefore position ot i need to add 1 to match the 1-based corrdinates
            #if not Call==Ref:
                #out_genotypeTotal.write(OUT)
            if CSS>0.9 and FamSize>=2:  ##VerySensitive
                TotalMoleculeCtsMatrix[i][1]+=1
                if not Call==Ref:
                    out_genotype_2_2.write(OUT)
        bar.next()

'''
            if DB_Cts==0: #如果这个碱基不是R1和R2的重复区域
                if CSS>0.75 and FamSize>=2:  ##VerySensitive
                    TotalMoleculeCtsMatrix[i][1]+=1
                    if not Call==Ref:
                        out_genotypeVerySensitive.write(OUT)
                if CSS>0.75 and FamSize>=3:  ##Sensitive
                    TotalMoleculeCtsMatrix[i][2]+=1
                    if not Call==Ref:
                        out_genotypeSensitive.write(OUT)
                if CSS>0.9 and FamSize>=4:   ##Specific
                    TotalMoleculeCtsMatrix[i][3]+=1
                    if not Call==Ref:
                        out_genotypeSpecific.write(OUT)
            else: #如果在R1和R2的重复区域
                if CSS>0.75 and FamSize>=1:  ##VerySensitive
                    TotalMoleculeCtsMatrix[i][1]+=1
                    if not Call==Ref:
                        out_genotypeVerySensitive.write(OUT)
                if CSS>0.75 and FamSize>=2:  ##Sensitive
                    TotalMoleculeCtsMatrix[i][2]+=1
                    if not Call==Ref:
                        out_genotypeSensitive.write(OUT)
                if CSS>0.9 and FamSize>=3:   ##Specific
                    TotalMoleculeCtsMatrix[i][3]+=1
                    if not Call==Ref:
                        out_genotypeSpecific.write(OUT)

            if CSS>0.9 and FamSize>=2:  ##VerySensitive
                TotalMoleculeCtsMatrix[i][1]+=1
                if not Call==Ref:
                    out_genotype_2_2.write(OUT)

'''
            #bar.next()

bar.finish()

#out_genotypeTotal.close()
#out_genotypeVerySensitive.close()
#out_genotypeSensitive.close()
#out_genotypeSpecific.close()

######### Print out the qualified total counts, aka qualified depth
print("Start to print Qualified Total Molecule Counts")
with open(out_totalCts_file,"w") as out_totalCts:
    for pos in range(0,len(TotalMoleculeCtsMatrix)):
        out_totalCts.write(str(pos+1)+"\t"+str(TotalMoleculeCtsMatrix[pos][0])+"\t"+str(TotalMoleculeCtsMatrix[pos][1])+"\t"+str(TotalMoleculeCtsMatrix[pos][2])+"\t"+str(TotalMoleculeCtsMatrix[pos][3])+"\n")
