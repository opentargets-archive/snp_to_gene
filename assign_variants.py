from collect_variant_data import CollectVariantData
from nearest_gene_five_prime import NearestGeneFivePrime
class AssignVariants:
    def __init__(self, rs_id_file):
        '''

        :param rs_id_file: str
        :return:
        '''
        collected_var_data = CollectVariantData(rs_id_file)
        self.variants_in_ensembl_map = collected_var_data.get_variants_in_ensembl_map()
        self.nearest_gene_map = collected_var_data.get_nearest_gene_map()
        self.rest_api_vep_list = collected_var_data.get_rest_api_vep_list()
    def __get_parsed_vep_output_map(self):
        '''

        :return: dict
        '''
        parsed_vep_output_map = {}
        for vep_entry in self.rest_api_vep_list:
            variant_id = vep_entry['id']
            most_severe_consequence = vep_entry['most_severe_consequence']
            transcript_consequences = vep_entry.get('transcript_consequences', [{'consequence_terms':[]}])
            associated_gene_ids = []
            for transcript_consequence in transcript_consequences:
                if most_severe_consequence in transcript_consequence['consequence_terms'] and \
                        transcript_consequence['biotype'] == 'protein_coding':
                    gene_id = transcript_consequence['gene_id']
                    if gene_id not in associated_gene_ids:
                        associated_gene_ids.append(gene_id)
            vep_details = {}
            vep_details['most_severe_consequence'] = most_severe_consequence
            vep_details['associated_gene_ids'] = associated_gene_ids
            parsed_vep_output_map[variant_id] = vep_details
        return parsed_vep_output_map

    def get_assigned_variant_list(self):
        '''
        return a list of dictionaries that contain the required information to assign variants to genes.
        :return: list
        '''
        parsed_vep_output_map = self.__get_parsed_vep_output_map()
        assigned_variant_list = []
        assigned_variant_map = {}
        for variant_id in self.variants_in_ensembl_map.keys():
            assigned_variant_map['variant_id'] = variant_id
            assigned_variant_map['is_in_ensembl?'] = self.variants_in_ensembl_map[variant_id]
            if variant_id in self.nearest_gene_map:
                nearest_gene_5p = NearestGeneFivePrime(self.nearest_gene_map[variant_id])
                nearest_gene_map = nearest_gene_5p.get_nearest_gene_map()
                assigned_variant_map['nearest_ensembl_5p_distance'] = nearest_gene_map.get('distance', 'NA')
                assigned_variant_map['nearest_5p_ensembl_gene_id'] = nearest_gene_map.get('ensembl_gene_id', 'NA')
            if variant_id in parsed_vep_output_map:
                assigned_variant_map['most_severe_consequence'] = parsed_vep_output_map[variant_id]['most_severe_consequence']
                assigned_variant_map['vep_associated_gene_ids'] = parsed_vep_output_map[variant_id]['associated_gene_ids']
            else:
                assigned_variant_map['most_severe_consequence'] = 'Not in VEP output'
                assigned_variant_map['vep_associated_gene_ids'] = ['Not in VEP output']
            assigned_variant_list .append(assigned_variant_map)
            assigned_variant_map = {}
        return assigned_variant_list
if __name__ == '__main__':
    rs_id_list_file = 'test_data/rs_id_list.txt'
    assigned_variants = AssignVariants(rs_id_list_file)
    assigned_variants.get_assigned_variant_list()
    for assigned_variant in assigned_variants.get_assigned_variant_list():
        print assigned_variant
