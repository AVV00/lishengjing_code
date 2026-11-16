#! /usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os, glob, string, subprocess,time, math, re
from array import *
from collections import deque 

###a script from CRISP, downloaded from http://polymorphism.scripps.edu/~vbansal/software/CRISP/
### Line 95, modified by Mingkun Li, if cigarstring == '*' or mq < 0, thus keep the reads with quality score ==0;
######################################################################

pileuptable = {}; # list of positions to print, others to omit 
subsetflag =0;

def read_fasta(seqfile):
    sequences = {}; reflist = []; lines=0; strlist = []; 
    File = open(seqfile,'r');
    if not File: print >>sys.stderr, 'reference sequence file',seqfile,'not found'; sys.exit();

    for line in File:
        if line[0] == '>': 
            if lines > 0:
                l =0;
                for k in xrange(len(strlist)): l += len(strlist[k]);
                sequences[refname][0] += ''.join(strlist); sequences[refname][1] = l; 
                for i in range(len(strlist)): strlist.pop();
                print >>sys.stderr, 'added seq',refname,(sequences[refname][1]);
            refname = line.strip().strip('\r').lstrip('>').split()[0];    reflist.append(refname);
            sequences[refname] = ['',0];    # refsequence and basecalls 
        else: strlist.append(line.strip().strip('\r').upper()); lines +=1; 
    l =0;
    for k in xrange(len(strlist)): l += len(strlist[k]);
    sequences[refname][0] += ''.join(strlist); sequences[refname][1] = l; 
    for i in range(len(strlist)): strlist.pop();
    print >>sys.stderr, 'added seq',refname,(sequences[refname][1]);
    File.close();
    return [sequences,reflist];


def ibases(bases): 
    if bases[0] == 'D' or bases[0] == 'I': return bases[6:]
    else: return '';

def printpile(locus,refsequence,last,start,RQ,lenRQ):
        
    for k in xrange(last,start):
        if subsetflag ==1:
            if locus + ':' + str(k+1) not in pileuptable: 
                if lenRQ > 0: RQ.popleft(); lenRQ -=1; 
                continue;
        if lenRQ > 0:
            coverage = len(RQ[0]);
            bases = ''.join([RQ[0][f][0] for f in xrange(coverage)]);
            qvalues = ''.join([RQ[0][f][1] for f in xrange(coverage)]);
            mvalues = ''.join([RQ[0][f][2] for f in xrange(coverage)]);
            positions = ','.join([ str(ord(RQ[0][f][3])*100+ord(RQ[0][f][4])) for f in xrange(coverage)]);
            mismatches = ''.join([RQ[0][f][5]  for f in xrange(coverage)]);
            indelbases = ''.join([RQ[0][f][6:]  for f in xrange(coverage)]);
            Ic = 0;
            for f in xrange(coverage):
                if bases[f] == 'I': Ic +=1;
            print locus,k+1,refsequence[0][k],coverage-Ic,'@'+bases,'@'+qvalues,'@'+mvalues,positions,mismatches,indelbases;
            RQ.popleft(); lenRQ -=1;
        else: 
            print locus,k+1,refsequence[0][k],0;
    return lenRQ;

def samtopileup(readfile,seqfile,targetfile):
    global subsetflag
    if targetfile != '':
        print >>sys.stderr, 'reading target positions',targetfile;
        File = open(targetfile,'r');
        for line in File:        
            pos = line.split(); 
            for a in xrange(int(pos[1]),int(pos[2])+1):   pileuptable[pos[0]+':'+`a`] = 1;
        File.close();
    [sequences,reflist] = read_fasta(seqfile); 
    current =0 ; index = sequences[reflist[current]]; last =0;

    File=open(readfile,'r');  reads =0;
    if not File: print >>sys.stderr, 'samfile',readfile,'not found'; sys.exit();

    RQ = deque(); lenRQ =0; offset =0;

    # 新增过滤判断函数
    def is_filtered(readlen, physical_pos):
        if readlen == 143:
            return physical_pos < 3 or physical_pos >= readlen - 10
        elif readlen == 150:
            return physical_pos < 10 or physical_pos >= readlen - 10
        elif 144 <= readlen <= 149:
            n = 150 - readlen
            three_filter = 10 - n
            return physical_pos < 10 or physical_pos >= readlen - three_filter
        elif 133 <= readlen <= 142:
            n = 143 - readlen
            three_filter = 10 - n
            return physical_pos < 3 or physical_pos >= readlen - three_filter
        elif readlen < 133:
            return physical_pos < 3
        return False

    for s in File:
        if s[0] == '@': continue;
        line = s.strip().split();
        reads +=1; 
        if reads%200000 ==0: print >>sys.stderr, 'processed',reads,'reads';
        ll = len(line);
        if ll < 11: continue;
        try: 
            readid = line[0]; flag = int(line[1]); locus = line[2]; start = int(line[3]); mq = min(int(line[4]),90);
        except ValueError: continue;
        cigarstring = line[5]; 
        if cigarstring == '*' or mq < 0: continue;
        read = line[9]; quality = line[10]; 
        try: refsequence = sequences[locus];
        except KeyError: print >>sys.stderr, 'could not find sequence name',locus,'in fasta file'; sys.exit(); 

        readlength = len(read); delta =0
        if flag & 4 ==4: continue;
        strand = '+';
        if flag & 16 == 16: strand = '-';
        if flag & 1 == 1 and flag & 128 == 128: read12 = 2; delta = readlength;

        cigarlist = []; prev = 0; 
        cflag =0;  mlength =0; l1 =0; l2 =0; mismatches =0;
        for i in xrange(len(cigarstring)):
            b = ord(cigarstring[i]);
            if b < 48 or b > 57: 
                ml = int(cigarstring[prev:i]); cigarlist.append(cigarstring[i]);  cigarlist.append(ml);    prev = i+1;
                if cigarstring[i] == 'M': 
                    if start+l2+ml-1 < refsequence[1] and start+l2-1 >=0:
                        # 新增mismatch计算（考虑过滤区域）
                        for t in xrange(ml):
                            current_l1 = l1 + t
                            ref_pos = start + l2 + t -1
                            # 计算物理位置
                            if strand == '+':
                                physical_pos = current_l1
                            else:
                                physical_pos = readlength - 1 - current_l1
                            # 过滤区域不统计mismatch
                            #if not is_filtered(readlength, physical_pos):
                            if read[current_l1] != refsequence[0][ref_pos]:
                                mismatches +=1
                    l1 +=ml; l2 += ml; mlength += ml;
                elif cigarstring[i] == 'D': mlength += ml; mismatches +=1; l2 += ml;
                elif cigarstring[i] == 'I': mismatches +=1; l1 += ml;
                elif cigarstring[i] == 'S': l1 += ml;
                elif cigarstring[i] == 'H' or cigarstring[i] == 'P' or cigarstring[i] == 'N': cflag =1; break; 
        
        if cflag ==1 or start + mlength >= refsequence[1] or mismatches >= 60: continue;

        while locus != reflist[current]:
            lenRQ = printpile(reflist[current],index,last,index[1],RQ,lenRQ); 
            last = 0;
            current +=1;
            if current < len(reflist): index = sequences[reflist[current]];
            else: break;
            if current >= len(reflist): break;

        lenRQ = printpile(locus,refsequence,last,start-1,RQ,lenRQ); 
        last = start-1;
        
        l1 = 0; l2 =0; e = 0; mqb = chr(mq+33); mmb = chr(mismatches+48);  delta =0;
        # 处理CIGAR添加碱基（新增过滤逻辑）
        for k in xrange(0,len(cigarlist),2):
            op = cigarlist[k]
            oplen = cigarlist[k+1]
            if op == 'M':
                l2_initial = l2
                for t in xrange(oplen):
                    current_l1 = l1 + t
                    ref_pos = start + l2_initial + t -1
                    # 计算物理位置
                    if strand == '+':
                        physical_pos = current_l1
                        psb = current_l1 + 1 + delta
                    else:
                        physical_pos = readlength - 1 - current_l1
                        psb = readlength - current_l1 + delta
                    
                    # 生成base字符
                    if read[current_l1] == refsequence[0][ref_pos]:
                        base = ',' if strand == '+' else '.'
                    else:
                        base = read[current_l1].upper() if strand == '+' else read[current_l1].lower()
                    
                    # 过滤判断
                    if base not in (',', '.') and is_filtered(readlength, physical_pos):
                        continue  # 跳过错配碱基
                    
                    # 添加到队列
                    current_rq_pos = l2_initial + t
                    while current_rq_pos >= len(RQ):
                        RQ.append([])
                        lenRQ += 1
                    qual_char = quality[current_l1] if current_l1 < len(quality) else '!'
                    entry = "%s%s%s%s%s%s" % (base, qual_char, mqb, chr(psb//100), chr(psb%100), mmb)
                    RQ[current_rq_pos].append(entry)
                
                l1 += oplen
                l2 += oplen
            elif op == 'I':
                # 处理插入（保持原逻辑）
                if strand == '+': 
                    psb = l1 +1 + delta
                    b = read[l1:l1+oplen]
                else: 
                    psb = readlength - l1 + delta
                    b = read[l1:l1+oplen].lower()
                bases = "I%s%s%s%s%s+%s" % (quality[l1],mqb,chr(psb//100),chr(psb%100),mmb,b)
                while l2 >= lenRQ: RQ.append([]); lenRQ +=1;
                RQ[l2].append(bases);
                l1 += oplen
            elif op == 'D':
                # 处理删除（保持原逻辑）
                if strand == '+': 
                    psb = l1 +1 + delta
                    b = refsequence[0][start+l2_initial-1:start+l2_initial-1+oplen]
                else: 
                    psb = readlength - l1 + delta
                    b = refsequence[0][start+l2_initial-1:start+l2_initial-1+oplen].lower()
                bases = "D%s%s%s%s%s-%s" % (quality[l1],mqb,chr(psb//100),chr(psb%100),mmb,b)
                while l2 >= lenRQ: RQ.append([]); lenRQ +=1; 
                RQ[l2].append(bases);
                l2 += oplen

    File.close();
    
    index = sequences[reflist[current]];
    lenRQ = printpile(reflist[current],index,last,index[1],RQ,lenRQ);
    last =0; current +=1;
    while current < len(reflist):
        index = sequences[reflist[current]];
        lenRQ = printpile(reflist[current],index,last,index[1],RQ,lenRQ);
        current +=1;

##########################################################################################################################

if len(sys.argv)< 3: print 'python sam_to_pileup.py SAMfile.sorted ref.fasta targets.BED(optional)'; sys.exit();
elif len(sys.argv) ==3: samtopileup(sys.argv[1],sys.argv[2],'');
elif len(sys.argv) ==4: subsetflag =1; samtopileup(sys.argv[1],sys.argv[2],sys.argv[3]);
