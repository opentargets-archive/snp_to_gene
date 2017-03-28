from write_gene_assignments import WriteGeneAssignments
import sys
'''
Given an input file with a single column of rs IDs for SNPs, write an output TSV file with gene assignments.
'''
rs_id_list_file = sys.argv[1]
output_file = sys.argv[2]
gene_assignments_writer = WriteGeneAssignments(rs_id_list_file)
gene_assignments_writer.write_output_to_file(output_file)
print "Done!"