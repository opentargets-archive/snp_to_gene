import requests
import json
import re

class RsIdVepPost():
    '''
    
    '''
    def __init__(self, rs_ids, assembly_name='GRCh38'):
        '''
        
        '''
        self.rs_ids = [rs_id.lower() for rs_id in rs_ids
                            if re.search(r'^rs\d+$', rs_id.strip(), re.IGNORECASE)]
        self.assembly_name = assembly_name.lower()
        self.rs_id_sublists = self._make_rs_id_sublists(self.rs_ids)
        self.post_request_errors = []
        self.vep_post_output_jsons = self._set_vep_post_output_jsons()
    def _make_rs_id_sublists(self, rs_ids, sublist_size=500):
        if sublist_size >= len(rs_ids):
            return [rs_ids]
        return [rs_ids[i:i + sublist_size] for i in range(0, len(rs_ids), sublist_size)]
    def get_rs_id_sublists(self):
        '''
        '''
        return self.rs_id_sublists
    def _get_rs_id_string_formatted_for_post(self, rs_id_sublist):
        '''
        
        '''
        string_formatted_for_post = '[' + ', '.join(['"' + rs_id + '"' for rs_id in rs_id_sublist]) + ']'
        return string_formatted_for_post
    def _set_vep_post_output_jsons(self):
        '''
        
        '''
        server = "http://rest.ensembl.org"
        ext = "/vep/human/id"
        headers={ "Content-Type" : "application/json", "Accept" : "application/json"}
        vep_post_output_jsons = []
        for rs_id_sublist in self.rs_id_sublists:
            ids_list = '{ "ids" : %s }' % self._get_rs_id_string_formatted_for_post(rs_id_sublist)
            try:
                req = requests.post(server+ext, headers=headers, data=ids_list)
                vep_post_outputs = req.json()
                for vep_post_output in vep_post_outputs:
                    vep_post_output_json = json.loads(json.dumps(vep_post_output))
                    if isinstance(vep_post_output_json, dict):
                        vep_post_output_jsons.append(json.loads(json.dumps(vep_post_output)))
            except ValueError as ex:
                self.post_request_errors.append(rs_id_sublist)
        return vep_post_output_jsons
    def get_vep_post_output_jsons(self):
        '''
        
        '''
        return self.vep_post_output_jsons
    
    def get_post_request_errors(self):
        '''
        
        '''
        return self.post_request_errors
    def get_rs_ids_not_in_vep_output(self):
        '''
        
        '''
        rs_ids_in_vep_output = [vep_output['id'] for vep_output in self.vep_post_output_jsons]
        rs_ids_not_in_vep_output = list(set(self.rs_ids) -  set(rs_ids_in_vep_output))
        return rs_ids_not_in_vep_output
    def write_vep_jsons_to_file(self, filename):
        with open(filename, 'wt') as fho:
            for vep_output_json in self.vep_post_output_jsons:
                fho.write(json.dumps(vep_output_json) + '\n')
        
    
if __name__ == '__main__':
    from pprint import pprint
    rs_id_list_file = './test_data/rs_id_list.txt'
    rs_ids = open(rs_id_list_file, 'rt').read().split('\n')
    vep_post = RsIdVepPost(rs_ids)
    rs_id_sublists = vep_post.get_rs_id_sublists()
    #print '\n'.join(json.dumps(vep_post.get_vep_post_output_jsons()))
    #print len(vep_post.get_post_request_errors())
    print '\n'.join(vep_post.get_rs_ids_not_in_vep_output()) + '\n'
    vep_post.write_vep_jsons_to_file('./test_data/test_vep_output.json')