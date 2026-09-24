rule subset:
    input: "a.vcf.gz"
    output: "out.vcf.gz"
    shell:
        "bcftools view -r chr20 a.vcf.gz -Oz -o out.vcf.gz"

rule merge:
    shell:
        """
        bcftools concat -Oz -o all.vcf.gz shard_1.vcf.gz shard_2.vcf.gz
        """
