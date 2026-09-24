bcftools index input.vcf.gz
bcftools view -r chr20 input.vcf.gz -Oz -o out.vcf.gz
