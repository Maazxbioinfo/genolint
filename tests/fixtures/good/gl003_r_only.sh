bcftools index input.vcf.gz
bcftools view -r chr20:1-1000 -Oz -o out.vcf.gz input.vcf.gz
