bcftools index input.vcf.gz
bcftools view -R regions.bed -Oz -o out.vcf.gz input.vcf.gz
