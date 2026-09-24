bcftools index in.vcf.gz
zcat x.txt | bcftools view -r chr20 in.vcf.gz -Oz -o o.vcf.gz
