import requests
import time
import re

class RsIdVepPost():
    '''
    Using the Ensembl REST API, retrieve the VEP information for a list of human rs IDs
    as JSON string.
    '''
    def __init__(self, rs_ids, assembly_name='GRCh38'):
        '''
        Provide a list of human rs IDs and an optional and a humand genome assembly (defaults to GRCh38).
        Any identifiers that do not match the regex ^rs\d+$ are removed.
        '''
        self.rs_ids = [rs_id.lower() for rs_id in rs_ids
                            if re.search(r'^rs\d+$', rs_id.strip(), re.IGNORECASE)]
        self.assembly_name = assembly_name.lower()
        self.post_request_errors = []
    def __query_rest_api(self):
        '''
        Create the parameters for the POST call and execute it.
        Return the request JSON.
        '''
        time.sleep(1) # Ensure a pause when used in a loop.
        server = "http://rest.ensembl.org"
        ext = "/vep/human/id"
        headers={ "Content-Type" : "application/json", "Accept" : "application/json"}
        rs_id_string_formatted_for_post = '[' + ', '.join(['"' + rs_id + '"' for rs_id in self.rs_ids]) + ']'
        ids_list = '{ "ids" : %s }' % rs_id_string_formatted_for_post
        req = requests.post(server+ext, headers=headers, data=ids_list)
        return req.json()
    def get_vep_post_output(self, max_retry_count = 10):
        '''
        Calls "__query_rest_api()" in a loop to allow for
        failures. If the call does not generate an exception, the VEP info JSON is returned.
        Will re-try up to the number set in "max_retry_count" and raises an
        exception when this limit is reached.
        '''
        success = False
        vep_post_output = []
        retry_count = 0
        while success == False:
            try:
                vep_post_output = self.__query_rest_api()
                success = True
            except ValueError as ex:
                if ex.message == 'No JSON object could be decoded':
                    time.sleep(1)
                    retry_count += 1
                    if retry_count == max_retry_count:
                        raise Exception("Maximum retry count reached!")
                else:
                    raise ex
        return vep_post_output
    
if __name__ == '__main__':
    rs_id_list_file = './test_data/rs_id_list.txt'
    rs_ids = open(rs_id_list_file, 'rt').read().split('\n')
    vep_post = RsIdVepPost(rs_ids)
    vep_post_output = vep_post.get_vep_post_output()
    for entry in vep_post_output:
        print entry['id'], entry['most_severe_consequence']

