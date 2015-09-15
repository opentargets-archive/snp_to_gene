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
    def __init__(self, rs_id, assembly):
        '''
        Initialise with an rs ID and assembly name.
        '''
        self.rs_id = rs_id.lower()
        self.assembly = assembly.lower()
        if self.assembly == 'grch38':
            self.url = 'http://rest.ensembl.org/vep/human/id/%s?' % (rs_id,)
        elif self.assembly == 'grch37':
            self.url = 'http://%s.rest.ensembl.org/vep/human/id/%s?' % ('grch37', rs_id)
        else:
            raise Exception('Unknown assembly: %r' % assembly)
    def get_json_for_rs_id(self):
        '''
        Return the VEP output JSON as string.
        Raise a custom NoJsonException exception if no JSON is returned by the API.
        '''
        req = requests.get(self.url, headers={ "Content-Type" : "application/json"})
        if not req.ok:
            raise NoJsonException('No JSON returned from REST API!')
        return json.dumps(req.json())
    
if __name__ == '__main__':
    rs_ids = ['rs429358', 'rs7412']
    for rs_id in rs_ids:
        vep_37 = RsIdVep(rs_id, 'GRCh37')
        print vep_37.get_json_for_rs_id()
        vep_38 = RsIdVep(rs_id, 'GRCh38')
        print vep_38.get_json_for_rs_id()
