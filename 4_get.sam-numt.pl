#!/usr/bin/perl -w
use warnings;
use strict;
my $outdir="/mnt/data2/lishengjing/2_o_10_HCC/DNA/";
my @list =glob("/mnt/data2/lishengjing/2_o_10_HCC/DNA/*/*.numt.bam");
foreach my $f (@list){
       my $sam=(split/\//,$f)[-2];
       print "$sam\n";
       open IN, "samtools view -hF 4 $f|" or die $!;
       open (O,">$outdir/$sam/$sam.0.numt.sam");
       open (R,">$outdir/$sam/$sam.0.numt.rm.sam");
       while(<IN>){
            chomp;
            if (/^@/){print O "$_\n";print R "$_\n";}else{
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
               if ($mismatch < 1){print O "$_\n";}else{print R "$_\n";}
            }
      }close(IN);
      close(O);
      close(R);
      `samtools view -bS -h $outdir/$sam/$sam.0.numt.rm.sam >$outdir/$sam/$sam.0.numt.rm.bam`;
      `samtools index $outdir/$sam/$sam.0.numt.rm.bam`;
      `samtools flagstat $outdir/$sam/$sam.0.numt.rm.bam >$outdir/$sam/$sam.0.numt.rm.bam.stat`;
      `samtools view -bS -h $outdir/$sam/$sam.0.numt.sam >$outdir/$sam/$sam.0.numt.bam`;
      `samtools index $outdir/$sam/$sam.0.numt.bam`;
      `samtools flagstat $outdir/$sam/$sam.0.numt.bam >$outdir/$sam/$sam.0.numt.bam.stat`;

}             
