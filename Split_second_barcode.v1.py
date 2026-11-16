#!/usr/bin/python
import gzip, argparse, sys, os

# Input files
def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--samp',required=True, help='sample name')
    p.add_argument('--samp_barcode1',required=True, help='R1 barcode,exmple:ATGTCA')
    p.add_argument('--samp_barcode2',required=True, help='R2 barcode,exmple:ATGTCA')
    p.add_argument('--samp_type',required=True, help='sample type,exmple:HCS_Tissue_DOU_mtDNA-CAP')
    p.add_argument('--analysis_type',required=True, help='analysis type,exmple:Combine_Analysis_rCRS-hg19-DNA_V1')
    p.add_argument('--outdir', required=True, help='outdir,first dir,exmple:/mnt/data/Seq_data/20220726')    
    args = p.parse_args()
    #if not path.exists(args.infile):
    #    sys.exit(f'Error: `{args.infile}`: infile does not exist.')
    #if not path.exists(args.outdir):
    #    sys.exit(f'Error: `{args.outdir}`: outdir does not exist.')
        
    return args

def split_barcode(sample,sample_barcode1,sample_barcode2,sample_type,analysis_type,output_dir):
        print (sample_type + '\t'+ sample)
                
        R1filter = gzip.open(output_dir + '/' + sample_type + '/' + analysis_type + '/' + sample + '/' + sample + '_filtered_R1.fq.gz', 'wb') 
        R2filter = gzip.open(output_dir + '/' + sample_type + '/' + analysis_type + '/' + sample + '/' + sample + '_filtered_R2.fq.gz', 'wb')
        R1removed = gzip.open(output_dir + '/' + sample_type + '/' + analysis_type + '/' + sample  + '/' +sample + '_removed_R1.fq.gz', 'wb')
        R2removed = gzip.open(output_dir + '/' + sample_type + '/' + analysis_type + '/' + sample + '/' + sample + '_removed_R2.fq.gz', 'wb')
                
        R1_file=gzip.open(output_dir + '/' + sample_type + '/' + analysis_type + '/' + sample + '/' + sample + '_R1.fq.gz', 'rb')
#        R1=data_R1.readlines()       
        R2_file=gzip.open(output_dir + '/' + sample_type + '/' + analysis_type + '/' + sample + '/' + sample + '_R2.fq.gz', 'rb')
#        R2=data_R2.readlines()
                
#        for j in range(0,len(R1),4):
        read_name_R1 = "1"
        while read_name_R1:
                read_name_R1 = R1_file.readline().strip().decode()
                read_seq_R1 = R1_file.readline().strip().decode()
                plus_R1 = R1_file.readline().strip().decode()
                q_value_R1 = R1_file.readline().strip().decode()
                second_barcode_R1 = read_seq_R1[0:6]

                read_name_R2 = R2_file.readline().strip().decode()
                read_seq_R2 = R2_file.readline().strip().decode()
                plus_R2 = R2_file.readline().strip().decode()
                q_value_R2 = R2_file.readline().strip().decode()
                second_barcode_R2 = read_seq_R2[0:6]
                
                if second_barcode_R1 == sample_barcode1 and second_barcode_R2 == sample_barcode2:
                    R1filter.write(read_name_R1.encode()  + b'\n')
                    R1filter.write(read_seq_R1[7:].encode()  + b'\n')
                    R1filter.write(plus_R1.encode()  + b'\n')
                    R1filter.write(q_value_R1[7:].encode()  + b'\n')
                    R2filter.write(read_name_R2.encode()  + b'\n')
                    R2filter.write(read_seq_R2[7:].encode()  + b'\n')
                    R2filter.write(plus_R2.encode()  + b'\n')
                    R2filter.write(q_value_R2[7:].encode()  + b'\n')
                else:
                    R1removed.write(read_name_R1.encode() + b'\n')
                    R1removed.write(read_seq_R1[7:].encode() + b'\n')
                    R1removed.write(plus_R1.encode() + b'\n')
                    R1removed.write(q_value_R1[7:].encode() + b'\n')
                    R2removed.write(read_name_R2.encode() + b'\n')
                    R2removed.write(read_seq_R2[7:].encode() + b'\n')
                    R2removed.write(plus_R2.encode() + b'\n')
                    R2removed.write(q_value_R2[7:].encode() + b'\n')
        R1filter.close()
        R2filter.close()
        R1removed.close()
        R2removed.close()
        R1_file.close()
        R2_file.close()
# Main function
def main():
     # Parse Arguments
    args = parse_args()

    sample=args.samp
    sample_barcode1=args.samp_barcode1
    sample_barcode2=args.samp_barcode2
    sample_type=args.samp_type
    analysis_type=args.analysis_type
    output_dir=args.outdir

    split_barcode(sample,sample_barcode1,sample_barcode2,sample_type,analysis_type,output_dir)

# --------
# Run Code
# --------
if __name__ == '__main__':
    main()
