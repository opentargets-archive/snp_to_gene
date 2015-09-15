from rs_id_vep import RsIdVep, NoJsonException
from process_vep import ProcessVep
from nearest_gene_five_prime import NearestGeneFivePrime
import os

class AssignRsIDsToGenes():
    def __init__(self, rs_ids, assembly_name):
        self.rs_ids = rs_ids
        self.assembly_name = assembly_name
        self.vep_gene_assignments = self._set_vep_gene_assignments()
        self.nearest_gene_five_prime = self._set_nearest_five_prime()
    def _set_vep_gene_assignments(self):
        '''
        Loop over all the rs IDs and for each one, create an RsIdVep instance.
        Use its methods to extract required data.
        Return a list of dictionaries where each dictionary contains the extracted data.
        For any dictionary list elements where the "most_severe_consequence_genes" is an empty list,
        their rs IDs will be evaluated for the nearest five prime gene using the Perl API.
        '''
        vep_gene_assignments = []
        for rs_id in self.rs_ids:
            rs_id_vep_obj = RsIdVep(rs_id, self.assembly_name)
            consequence_genes_map = {}
            try:
                vep_rest_output = rs_id_vep_obj.get_json_for_rs_id()
                vep_processor = ProcessVep(vep_rest_output)
                most_severe_consequence = vep_processor.get_most_severe_consequence()
                most_severe_consequence_genes = vep_processor.get_ensembl_gene_list_for_most_severe_consequence()
                consequence_genes_map['rs_id'] = rs_id
                consequence_genes_map['most_severe_consequence'] = most_severe_consequence
                consequence_genes_map['most_severe_consequence_genes'] = most_severe_consequence_genes
                vep_gene_assignments.append(consequence_genes_map)
            except NoJsonException as ex:
                consequence_genes_map['rs_id'] = rs_id
                consequence_genes_map['most_severe_consequence'] = None
                consequence_genes_map['most_severe_consequence_genes'] = []
                vep_gene_assignments.append(consequence_genes_map)
        return vep_gene_assignments
    def get_vep_gene_assignments(self):
        '''
        Return list of dictionaries instance variable where list element
        dictionaries contain VEP gene assignment values (rs ID, SO term and list of assigned genes)
        '''
        return self.vep_gene_assignments
    def get_rs_ids_with_no_vep_genes(self):
        '''
        
        '''
        vep_rs_ids = [vep_gene_assignment['rs_id'] for vep_gene_assignment in self.vep_gene_assignments]
        rs_ids_with_no_vep_genes = list(set(self.rs_ids) - set(vep_rs_ids))
        for vep_gene_assignment in self.vep_gene_assignments:
            rs_id = vep_gene_assignment['rs_id']
            if vep_gene_assignment['most_severe_consequence'] == 'intergenic_variant':
                rs_ids_with_no_vep_genes.append(rs_id)
        return rs_ids_with_no_vep_genes

    def _set_nearest_five_prime(self):
        '''
        
        '''
        rs_ids_with_no_vep_genes = self.get_rs_ids_with_no_vep_genes()
        temp_file = 'rs_ids.txt'
        fho = open(temp_file, 'wt')
        fho.write('\n'.join(rs_ids_with_no_vep_genes))
        fho.close()
        nearest_gene_5p = NearestGeneFivePrime(temp_file)
        nearest_gene_map = nearest_gene_5p.get_rs_id_nearest_gene_map()
        os.remove(temp_file)
        self.nearest_five_prime = nearest_gene_map
    def get_nearest_five_prime(self):
        '''
        
        '''
        return self.nearest_five_prime
    def get_gene_assignments(self):
        '''
        Produce the final gene assignments as a list of lists.
        '''
        gene_assignments = []
        for vep_gene_assignment in self.vep_gene_assignments:
            rs_id = vep_gene_assignment['rs_id']
            if vep_gene_assignment['most_severe_consequence'] == 'intergenic_variant': continue
            so_term = vep_gene_assignment['most_severe_consequence']
            genes = ','.join(vep_gene_assignment['most_severe_consequence_genes'])
            distance = 0
            gene_assignments.append([rs_id, so_term, genes, distance])
        for rs_id, gene_info in self.nearest_five_prime.items():
            so_term = 'nearest_gene_five_prime'
            if not gene_info.has_key('ensembl_gene_id'): continue
            gene = gene_info['ensembl_gene_id']
            distance = gene_info['distance']
            gene_assignments.append([rs_id, so_term, gene, distance])
        return gene_assignments
if __name__ == '__main__':
    rs_id_file = 'test_data/rs_id_list.txt'
    rs_ids = open(rs_id_file, 'rt').read().split('\n')
    assign_genes = AssignRsIDsToGenes(rs_ids, 'GRCh38')
    vep_gene_assignments = assign_genes.get_vep_gene_assignments()
    #print vep_gene_assignments
    #print assign_genes.get_rs_ids_with_no_vep_genes()
    #print assign_genes.get_nearest_five_prime()
    print assign_genes.get_gene_assignments()
    