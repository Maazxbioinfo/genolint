bcftools view -Ou in.vcf.gz | bcftools concat -Oz -o all.vcf.gz shard_1.vcf.gz shard_2.vcf.gz
