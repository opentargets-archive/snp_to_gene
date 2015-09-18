import json

'''
Parse Ensembl VEP REST API output for a single rs ID.
'''
class ProcessVep():
    '''
    Extracts required values from JSON returned by Ensembl VEP REST API.
    
    '''
    def __init__(self, json_vep_str):
        '''
        Instantiate with a JSON string as returned from Ensembl VEP REST API.
        '''
        self.json_vep_obj = json.loads(json_vep_str)
        self.rs_id = self.json_vep_obj['id']
    
    def get_rs_id(self):
        '''
        Return instance attribute.
        '''
        return self.rs_id
    
    def get_most_severe_consequence(self):
        '''
        Return the most severe consequence term if that term is represented in a trascript consequence
        that has biotype "protein_coding". The code here is complicated by the need to check that the given rs
        ID has returned a JSON with at least one transcript consequence where at least one of these has the
        biotype "protein_coding". If either of these tests fail, then it returns "intergenic_variant". All
        rs IDs with this consequence term will be assigned to the nearest five prime gene in the module
        "assign_rs_ids_to_genes.py".
        '''
        try:
            transcript_consequences = self.json_vep_obj['transcript_consequences']
        except KeyError:
            return 'intergenic_variant'
        biotypes = [trans_con['biotype'] for trans_con in transcript_consequences]
        if not 'protein_coding' in biotypes:
            return 'intergenic_variant'
        return self.json_vep_obj['most_severe_consequence']
    def get_ensembl_gene_list_for_most_severe_consequence(self):
        '''
        Return a list of Ensembl gene IDs where these genes have a transcript where
        the RS ID most severe consequence term is present in the transcript consequence
        terms.
        '''
        try:
            most_severe_consequence = self.get_most_severe_consequence()
            transcript_consequences = self.json_vep_obj['transcript_consequences']
        except KeyError as ex:
            return []
        if most_severe_consequence == 'intergenic_variant': return []
        ensembl_gene_list_for_most_severe_consequence = []
        for transcript_consequence in transcript_consequences:
            consequence_terms = transcript_consequence['consequence_terms']
            if most_severe_consequence in consequence_terms:
                ensembl_gene_id = transcript_consequence['gene_id']
                if ensembl_gene_id not in ensembl_gene_list_for_most_severe_consequence:
                    ensembl_gene_list_for_most_severe_consequence.append(ensembl_gene_id)
        return ensembl_gene_list_for_most_severe_consequence
    
if __name__ == '__main__':
    vep_json_file = '/Users/mmaguire/CTTV/gwas_catalog/test_vep_post_rs_ids_output.txt'
    for vep_json_line in open(vep_json_file, 'rt'):
        process_vep = ProcessVep(vep_json_line)
        print process_vep.get_rs_id(), process_vep.get_most_severe_consequence(), ','.join(process_vep.get_ensembl_gene_list_for_most_severe_consequence())

