from assign_variants import AssignVariants
from execute_ensembl_perl import ExecuteEnsemblPerl
class WriteGeneAssignments:
    def __init__(self, rs_id_file):
        '''

        :param rs_id_file: str
        :param output_tsv_file: str
        :return: None
        '''
        self.assigned_variants = AssignVariants(rs_id_file)
        self.tsv_file_header = ['rs_id',
                                'in_ensembl',
                                'ensembl_gene_ids',
                                'gene_symbols',
                                'so_term',
                                'distance']
        self.output_rows = self.__process_assigned_variants()
        self.reference_gene_map = self.__get_reference_gene_map()
    def __process_assigned_variants(self):
        '''

        :return: list
        '''

        assigned_variant_list = self.assigned_variants.get_assigned_variant_list()
        output_rows = []
        for row_map in assigned_variant_list:
            rs_id = row_map['variant_id']
            in_ensembl = row_map['is_in_ensembl?']
            if row_map['vep_associated_gene_ids']:
                so_term = row_map['most_severe_consequence']
                distance = 0
                ensembl_gene_ids = row_map['vep_associated_gene_ids']
            elif row_map['most_severe_consequence'] == 'regulatory_region_variant':
                so_term = 'nearest_gene_five_prime_end_reg'
                distance = row_map['nearest_ensembl_5p_distance']
                ensembl_gene_ids = [row_map['nearest_5p_ensembl_gene_id']]
            else:
                so_term = 'nearest_gene_five_prime_end'
                distance = row_map['nearest_ensembl_5p_distance']
                ensembl_gene_ids = [row_map['nearest_5p_ensembl_gene_id']]
            output_rows.append([rs_id, in_ensembl, ensembl_gene_ids,so_term, distance ])
        return output_rows
    def __get_reference_gene_map(self):
        '''

        :return: dict
        '''
        ensembl_gene_ids = []
        for output_row in self.output_rows:
            ensembl_gene_ids.extend(output_row[2])
        ensembl_id_uniq = list(set(ensembl_gene_ids))
        exec_ensembl_perl = ExecuteEnsemblPerl()
        reference_gene_map = exec_ensembl_perl.get_ensembl_gene_id_ref_map(ensembl_id_uniq)
        return reference_gene_map
    def write_output_to_file(self, path_to_output_file):
        '''

        :param path_to_file: string
        :return: None
        '''
        new_output_rows = []
        for output_row in self.output_rows:
            (rs_id, in_ensembl, ensembl_gene_ids, so_term, distance) = output_row
            #    (output_row[0], output_row[1], output_row[2], output_row[3])
            gene_symbols = []
            ensembl_gene_id_references = []
            for ensembl_gene_id in ensembl_gene_ids:
                try:
                    ref_gene_map = self.reference_gene_map[ensembl_gene_id]
                except KeyError:
                    continue
                gene_symbol = ref_gene_map['external_name']
                ensembl_gene_id_reference = ref_gene_map.get('ensembl_gene_id_for_reference', None)
                gene_symbols.append(gene_symbol)
                ensembl_gene_id_references.append(ensembl_gene_id_reference)
            new_output_row = [rs_id, in_ensembl, ','.join(ensembl_gene_id_references), ','.join(gene_symbols), so_term, distance]
            new_output_rows.append(new_output_row)
        with open(path_to_output_file, 'w') as fho:
            for data_row in new_output_rows:
                fho.write('\t'.join([str(element) for element in data_row]) + '\n')

if __name__ == '__main__':
    rs_id_list_file = '/Users/mmaguire/CTTV/cttv009_gwas_catalog/big_rs_id_list.txt'
    gene_assignments_writer = WriteGeneAssignments(rs_id_list_file)
    output_file = '/Users/mmaguire/CTTV/cttv009_gwas_catalog/big_rs_id_list_output.tsv'
    gene_assignments_writer.write_output_to_file(output_file)
