#!/usr/bin/perl -w
use warnings;
use strict;
my $outdir="/mnt/data2/lishengjing/2_o_10_HCC/DNA/";

my @list =glob("/mnt/data2/lishengjing/2_o_10_HCC/DNA/*/*rmdup.bam");
foreach my $f (@list){
       my $sam=(split/\//,$f)[-2];
       print "$sam\n";
       open IN, "samtools view -hF 4 $f|" or die $!;
       open (O,">$outdir/$sam/$sam.10.sam");
       open (R,">$outdir/$sam/$sam.10.rm.sam");
       open (O1,">$outdir/$sam/$sam.0.sam");
       open (R1,">$outdir/$sam/$sam.0.rm.sam");
       open (O2,">$outdir/$sam/$sam.1.sam");
       open (R2,">$outdir/$sam/$sam.1.rm.sam");
       while(<IN>){
            chomp;
            if (/^@/){print O "$_\n";print R "$_\n";print O1 "$_\n";print R1 "$_\n";print O2 "$_\n";print R2 "$_\n";}else{
               my @lines=split/\t/,$_;
               ## cigar
               my @str = split /\d+/,$lines[5];
               shift @str;
               my ($base_I,$base_D,$num_I,$num_D,$NM)=(0) x 5;
               my @num = split /[A-Z]/,$lines[5];
               my $i=0;
               foreach my $tmp_str(@str){
                      if ($tmp_str eq "I"){$num_I++;$base_I+=$num[$i];}
                      if ($tmp_str eq "D"){$num_D++;$base_D+=$num[$i];}
                      $i++;
               }                     
               foreach my $t(@lines){
                   if ($t =~ /NM:i/){
                       $NM=(split/:/,$t)[-1];
                   }
               }
               my $mismatch=$NM-$base_I-$base_D+$num_I+$num_D;
               if ($mismatch < 2){print O "$_\n";}else{print R "$_\n";}
               if ($mismatch < 1){print O1 "$_\n";}else{print R1 "$_\n";}
               if ($mismatch == 1){print O2 "$_\n";}else{print R2 "$_\n";}
            }
      }close(IN);
      close(O);
      close(R);
      `samtools view -bS -h $outdir/$sam/$sam.10.rm.sam >$outdir/$sam/$sam.10.rm.bam`;
      `samtools index $outdir/$sam/$sam.10.rm.bam`;
      `samtools flagstat $outdir/$sam/$sam.10.rm.bam >$outdir/$sam/$sam.10.rm.bam.stat`;
      `samtools view -bS -h $outdir/$sam/$sam.10.sam >$outdir/$sam/$sam.10.bam`;
      `samtools index $outdir/$sam/$sam.10.bam`;
      `samtools flagstat $outdir/$sam/$sam.10.bam >$outdir/$sam/$sam.10.bam.stat`;
      `samtools view -bS -h $outdir/$sam/$sam.0.rm.sam >$outdir/$sam/$sam.0.rm.bam`;
      `samtools index $outdir/$sam/$sam.0.rm.bam`;
      `samtools flagstat $outdir/$sam/$sam.0.rm.bam >$outdir/$sam/$sam.0.rm.bam.stat`;
      `samtools view -bS -h $outdir/$sam/$sam.0.sam >$outdir/$sam/$sam.0.bam`;
      `samtools index $outdir/$sam/$sam.0.bam`;
      `samtools flagstat $outdir/$sam/$sam.0.bam >$outdir/$sam/$sam.0.bam.stat`;
      `samtools view -bS -h $outdir/$sam/$sam.1.rm.sam >$outdir/$sam/$sam.1.rm.bam`;
      `samtools index $outdir/$sam/$sam.1.rm.bam`;
      `samtools flagstat $outdir/$sam/$sam.1.rm.bam >$outdir/$sam/$sam.1.rm.bam.stat`;
      `samtools view -bS -h $outdir/$sam/$sam.1.sam >$outdir/$sam/$sam.1.bam`;
      `samtools index $outdir/$sam/$sam.1.bam`;
      `samtools flagstat $outdir/$sam/$sam.1.bam >$outdir/$sam/$sam.1.bam.stat`;

}             
