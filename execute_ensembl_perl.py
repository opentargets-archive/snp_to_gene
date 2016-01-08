from subprocess import Popen, PIPE
import json

'''
All calls to Perl scripts that use the Ensembl API are wrapped here.
Each Perl script call is wrapped in its own method.
These Perl methods all print data structures serialized as JSON to stdout and the methods here
return these JSONs as Python data structures.
'''

class ExecuteEnsemblPerl:
    def __init__(self, rs_id_list_file):
        self._rs_id_list_file = rs_id_list_file
    def __get_json_output_for_perl_cmd(self, perl_cmd):
        '''
        Execute any Perl script and capture its JSON output and return it as a Python object.
        :param perl_cmd:
        :return: object
        '''
        p = Popen(perl_cmd, stdout=PIPE, stderr=PIPE, shell=True)
        stdout, stderr = p.communicate()
        if len(stderr) >0:
            raise Exception('Perl call has thrown error: %s' % stderr)
        return json.loads(stdout)
    def get_variant_in_ensembl_maps(self):
        '''
        Return a list of dictionaries where the dictionary maps the rs ID to a boolean
        to indicate if the rs ID is present in the current Ensembl.
        :return: list
        '''
        perl_cmd = 'perl variants_in_ensembl.pl %s' % self._rs_id_list_file
        return self.__get_json_output_for_perl_cmd(perl_cmd)
    def get_nearest_gene_map(self):
        '''
        Return a dictionary where each entry stores a list of dictionaries with
        distance information and names for the nearest genes.
        :return: dictionary
        '''
        perl_cmd = 'perl run_NearestGeneToSnp.pl %s' % self._rs_id_list_file
        return self.__get_json_output_for_perl_cmd(perl_cmd)

if __name__ == '__main__':
    test_file = './test_data/rs_id_list.txt'
    exec_ensembl_perl = ExecuteEnsemblPerl(test_file)
    print exec_ensembl_perl.get_variant_in_ensembl_maps()
    print exec_ensembl_perl.get_nearest_gene_map()
