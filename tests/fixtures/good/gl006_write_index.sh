bcftools view -f PASS --write-index -Oz -o out.vcf.gz input.vcf.gz
bcftools view -r chr20 out.vcf.gz -Oz -o sub.vcf.gz
