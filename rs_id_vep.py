import requests
import json


class NoJsonException(Exception):
    '''
    A custom exception to be raised when no JSON
    is returned from the REST API.
    '''
    pass


class RsIdVep():
    '''
    Returns Ensembl VEP REST API output for a given rs ID and assemblly name.
    Only recognises GRCh37 and GRCh38.
    '''
    def __init__(self, rs_id, assembly_name):
        '''
        Initialise with an rs ID and assembly name.
        '''
        self.rs_id = rs_id.lower()
        self.assembly_name = assembly_name.lower()
        if self.assembly_name == 'grch38':
            self.url = 'http://rest.ensembl.org/vep/human/id/%s?' % (rs_id,)
        elif self.assembly_name == 'grch37':
            self.url = 'http://%s.rest.ensembl.org/vep/human/id/%s?' % ('grch37', rs_id)
        else:
            raise Exception('Unknown assembly: %r' % assembly_name)
    def get_json_for_rs_id(self):
        '''
        Return the VEP output JSON as string. This method returns the JSON as an array
        with a single element. The array element is returned and not the array.
        Raise a custom NoJsonException exception if no JSON is returned by the API.
        '''
        req = requests.get(self.url, headers={ "Content-Type" : "application/json"})
        if not req.ok:
            raise NoJsonException('No JSON returned from REST API!')
        req_json = req.json()
        return json.dumps(req_json[0])
    
if __name__ == '__main__':
    # rs ID rs10005603 is intronic in a linc RNA
    rs_id_file = '/Users/mmaguire/cttv_gitlab/snp_to_gene/not_in_vep.txt'
    rs_ids = open(rs_id_file, 'rt').read().split('\n')
    for rs_id in rs_ids:
        try:
            vep_38 = RsIdVep(rs_id, 'GRCh38')
            print rs_id, '\t', vep_38.get_json_for_rs_id()
        except NoJsonException:
            print rs_id, '\t', 'No JSON'
        
