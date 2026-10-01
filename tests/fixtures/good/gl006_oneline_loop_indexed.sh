bcftools index in.vcf.gz
for i in 1 2; do bcftools view -r ${i} in.vcf.gz > out_${i}.vcf; done
