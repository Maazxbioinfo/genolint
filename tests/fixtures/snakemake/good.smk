rule subset:
    input: "a.vcf.gz"
    output: "out.vcf.gz"
    shell:
        """
        bcftools index a.vcf.gz
        bcftools view -r chr20 a.vcf.gz -Oz -o out.vcf.gz
        """
