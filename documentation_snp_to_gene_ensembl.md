Take just one SNP rs ID rs1050450 and follow it through the MySQL tables

~~~~~~~

-- Example rs ID = rs1050450
USE homo_sapiens_variation_81_38

-- Does variant exist in Ensembl?
SELECT
  v.`name`,
  v.variation_id
FROM
  variation v
WHERE
  `name` = 'rs1050450';

-- Get consequence types and other variation features
-- Much faster to query on variation_id (column is indexed),
-- variation_name is not.
-- variation_id for "rs1050450" is 779938
SELECT
  vf.variation_feature_id,
  vf.variation_name,
  vf.variation_id,
  vf.seq_region_id,
  vf.seq_region_start,
  vf.seq_region_end,
  vf.allele_string,
  vf.consequence_types
FROM
  variation_feature vf
WHERE
  variation_id = 779938;
  
-- Get transcripts for variation_feature_id 628168.
-- variation_id 779938 maps to variation_feature_id 628168
SELECT
 tv.transcript_variation_id,
 tv.variation_feature_id,
 tv.feature_stable_id,
 tv.consequence_types
FROM
  transcript_variation tv
WHERE
  variation_feature_id = 628168;
~~~~~~~


Go the homo_sapiens_core_81_38 database to get the gene details.

~~~~~~~
USE homo_sapiens_core_81_38;

-- Get the gene IDs for the transcript  and add the biotype.
SELECT 
  t.gene_id,
  biotype
FROM
  transcript t
WHERE
  stable_id IN('ENST00000419783','ENST00000419349','ENST00000496791','ENST00000620890','ENST00000418115','ENST00000454011','ENST00000422781');
  
-- Get gene details for a list of gene IDs (gene ID and ensembl_gene_id
SELECT
 gene_id,
 stable_id
FROM
  gene
WHERE gene_id IN(
  SELECT 
  t.gene_id
FROM
  transcript t
WHERE
  stable_id IN('ENST00000419783','ENST00000419349','ENST00000496791','ENST00000620890','ENST00000418115','ENST00000454011','ENST00000422781'));
  
-- Get the gene name using the xref table.
SELECT
  display_label
FROM
  xref
WHERE
  xref_id IN(
  SELECT
    display_xref_id
  FROM
    gene
  WHERE gene_id IN(
    SELECT 
      t.gene_id
    FROM
      transcript t
    WHERE
      stable_id IN('ENST00000419783','ENST00000419349','ENST00000496791','ENST00000620890','ENST00000418115','ENST00000454011','ENST00000422781')));
~~~~~~~

The final query gave the output "GPX1" and "RHOA".
