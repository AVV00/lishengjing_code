#!/usr/bin/perl -w 
use strict;

my $file = shift;
unless ($file and $file =~ /bam$/) {
    print "please input bam file\n";
    exit;
}

# 去掉 -f 0x2 过滤条件，直接提取比对到 chrM 的 reads
open IN, "samtools view -h $file chrM |" || die $!;

while (<IN>) {
    chomp;
    if (/^\@/) {
        # 保留头部信息，跳过非 chrM 的参考序列
        next if /\@SQ\tSN:chr[\d+|X|Y|Un]/;
        print "$_\n";
    } else {
        my @aa = split /\t/, $_;
        my $pos = $aa[3];  # 比对位置
        my $mapq = $aa[4]; # 比对质量分数

        # 过滤低质量的 reads（比对质量分数 >= 20）
        if ($mapq >= 20) {
            print "$_\n";
        }
    }
}

close IN;
