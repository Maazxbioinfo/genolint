bcftools index in.vcf.gz
bcftools view -r chr1 --output-type z --output-file out.vcf.gz in.vcf.gz
