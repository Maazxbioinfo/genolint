cat in.vcf | java -jar SnpSift.jar filter "ANN[*].EFFECT has 'synonymous'" > out.vcf
