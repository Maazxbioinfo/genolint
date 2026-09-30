gatk --java-options "-Xmx4G" HaplotypeCaller -R ref.fa -L chr20 --native-pair-hmm-threads 4 -I in.bam -O out.vcf.gz
