import sys
file1=sys.argv[1]
file2=sys.argv[2]
file3=sys.argv[3]
file4=sys.argv[4]
file_output=sys.argv[5]

data={}
f=open(file1,'r').readlines()
for i in f:
    sample=i.split('.')[0]
    data[sample] =[]
    data[sample].append(i.split('\t')[1])
    data[sample].append(i.strip('\n').split('\t')[2])

f=open(file2,'r').readlines()
for i in f:
    sample=i.split('.')[0]
    data[sample].append(i.split('\t')[1])
    data[sample].append(i.strip('\n').split('\t')[2])

f=open(file3,'r').readlines()
for i in f:
    sample=i.split('.')[0]
    data[sample].append(i.split('\t')[1])
    data[sample].append(i.strip('\n').split('\t')[2])

f=open(file4,'r').readlines()
for i in f:
    sample=i.split('.')[0]
    data[sample].append(i.split('\t')[1])
    data[sample].append(i.strip('\n').split('\t')[2])

f1=open(file_output,'w')
f1.write('sample\thg19-1+mtDNA-1\thg19-2\thg19-mtDNA-1+hg19-1\thg19-mtDNA-2\tmtDNA-1+hg19-1\tmtDNA-2\tmtDNA-hg19-1+mtDNA-1\tmtDNA-hg19-2\n')
for key,value in data.items():
    f1.write(key+'\t')
    f1.write('\t'.join(value)+'\n')

f1.close()
