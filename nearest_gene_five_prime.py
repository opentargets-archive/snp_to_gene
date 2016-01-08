from subprocess import Popen, PIPE
import json
from execute_ensembl_perl import ExecuteEnsemblPerl
'''

'''

class NearestGeneFivePrime():
    def __init__(self, nearest_gene_list):
        '''
        Instantiate with a list of dictionaries where each dictionary entry contains the distance
        and the gene identifier details.
        :param nearest_gene_list:
        :return: None
        '''
        self._nearest_gene_list = nearest_gene_list
    def get_gene_map_for_rank(self, rank):
        '''
        Ascending sort of the list of dictionaries by the absollute distance
        and returns the dictionary with the given rank
        :param self:
        :param rank: int
        :return: dictionary
        '''
        # Sort a list of dictionaries numerically using the key "distance".
        genes = sorted(self._nearest_gene_list, key=lambda x: abs(int(x['distance'])))
        if len(genes) -1 < rank:
            return {}
        return genes[rank]
    def get_nearest_gene_map(self, rank=0):
        '''
        Return a dictionary with required gene ID and distance information.
        Default rank=0 chooses the nearest gene but can provide rank=1
        to get, for example, the next nearest gene.
        '''
        nearest_gene_map = self.get_gene_map_for_rank(rank)
        return nearest_gene_map
        
if __name__ == '__main__':
    test_file = './test_data/rs_id_list.txt'
    exec_ensembl_perl = ExecuteEnsemblPerl(test_file)
    nearest_gene_map = exec_ensembl_perl.get_nearest_gene_map()
    rs_id = 'rs1000113'
    nearest_gene5p = NearestGeneFivePrime(nearest_gene_map[rs_id])
    print rs_id + ': ',
    print nearest_gene5p.get_nearest_gene_map()

    
