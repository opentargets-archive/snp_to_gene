from execute_ensembl_perl import ExecuteEnsemblPerl
from rs_id_vep_post import RsIdVepPost

'''
Given a single column file with rs IDs, get required information from the Perl Ensembl and
VEP POST REST APIs.
Implements three public methods to:
1: Get a dictionary indicating if the input variants are in the current Ensembl.
2: Get the nearest gene as a dictionary.
3: Get a list of VEP JSONs.
'''
class CollectVariantData:
    def __init__(self, rs_id_file):
        '''
        :param rs_id_file:
        :return: None
        '''
        self.rs_id_file = rs_id_file
        self.ensembl_perl = ExecuteEnsemblPerl(rs_id_file)
    def get_variants_in_ensembl_map(self):
        '''
        Uses the Perl Ensembl REST API to determine if input variants are in Ensembl.
        :return: dict
        '''
        return self.ensembl_perl.get_variant_in_ensembl_maps()
    def get_nearest_gene_map(self):
        '''
        Uses the PERL Ensembl API to get the nearest gene at the 5' end for each variant.
        :return: dict
        '''
        return self.ensembl_perl.get_nearest_gene_map()
    def __chunk_list(self, input_list, chunk_size=500):
        '''
        Breaks the input list into chunks. Used to limit the number of variants
        sent to the Ensembl REST VEP POST API call.
        :param chunk_size: int
        :return: generator
        '''
        sublist = []
        for element in input_list:
            sublist.append(element)
            if len(sublist) == chunk_size:
                yield sublist
                sublist = []
        if sublist:
            yield sublist
    def get_rest_api_vep_list(self):
        '''
        Uses the Ensembl REST VEP POST API to return a list of VEP JSONs.
        :return: list
        '''
        vep_outputs = []
        rs_ids = [rs_id.strip() for rs_id in open(self.rs_id_file, 'rt').read().split('\n')]
        for sublist in self.__chunk_list(rs_ids):
            rs_id_vep_post = RsIdVepPost(sublist)
            vep_output = rs_id_vep_post.get_vep_post_output()
            for entry in vep_output:
                vep_outputs.append(entry)
        return vep_outputs

if __name__ == '__main__':
    rs_id_list_file = 'test_data/big_rs_id_list.txt'
    collected_var_data = CollectVariantData(rs_id_list_file)
    variants_in_ensembl_map = collected_var_data.get_variants_in_ensembl_map()
    nearest_gene_map = collected_var_data.get_nearest_gene_map()
    rest_api_vep_list = collected_var_data.get_rest_api_vep_list()