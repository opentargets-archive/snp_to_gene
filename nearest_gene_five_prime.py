from subprocess import Popen, PIPE
import json

'''
Takes a list of SNPs (rs IDs) and uses the Perl Ensembl API
to return a JSON string with the nearest gene details.
Requires that the Perl Ensembl API is installed and available.
The Perl script that is invoked takes the rs ID list file as an argument
and writes its output as a JSON string to stdout.
Provides methods for extracting required data from the JSON returned by Perl.

In order to use the Ensembl Perl API, the current Ensembl variation and core packages
be downloaded and available to the Perl script called here. To ensure this, make
sure the PERL5LIB environment variable is set appropriately
'''

class NearestGeneFivePrime():
    def __init__(self, rs_id_list_file):
        '''
        Requires a path to a file with a list of SNPs as rs IDs.
        '''
        self.perl_cmd = 'perl run_NearestGeneToSnp.pl %s' % rs_id_list_file
        self.perl_json_output = ''
        self.perl_output_as_json()
        self.rs_ids = self.perl_json_output.keys()
    def perl_output_as_json(self):
        '''
        Execute the Perl script that takes the file with the list of rs IDs and
        capture the stdout into an instance variable. Raise an exception
        if the Perl script generates stderr output.
        '''
        p = Popen(self.perl_cmd, stdout=PIPE, stderr=PIPE, shell=True)
        stdout, stderr = p.communicate()
        if len(stderr) >0:
            raise Exception('Perl call has thrown error: %s' % stderr)
        self.perl_json_output = json.loads(stdout)
    def get_perl_output_as_json(self):
        '''
        Return the instance variable contsining the Perl script
        JSON output.
        '''
        return self.perl_json_output
    def get_gene_map_for_rank(self, rs_id, rank):
        '''
        For a given rs ID, return a dictionary from the sorted list of
        objects returned by as JSON by the Perl Ensembl API script. The returned
        dictionary is determined by the "rank" argument. The sorting is done on
        the absolute value of the "distance" integer. Passing a 0 for the rank will
        return the nearest gene.
        If the rank exceeds the last index of the list, an empty dictionary is returned.
        '''
        # Sort a list of dictionaries numerically using the key "distance".
        genes_for_rs_id = sorted(self.perl_json_output[rs_id], key=lambda x: abs(int(x['distance'])))
        if len(genes_for_rs_id) -1 < rank:
            return {}
        return genes_for_rs_id[rank]
    def get_rs_id_nearest_gene_map(self, rank=0):
        '''
        Return a dictionary mapping rs ID to dictionary with required
        gene ID and distance information.
        Default rank=0 chooses the nearest gene but can provide rank=1
        to get, for example, the next nearest gene.
        '''
        nearest_gene_map = {}
        for rs_id in self.rs_ids:
            nearest_gene_map[rs_id] = self.get_gene_map_for_rank(rs_id, rank)
        return nearest_gene_map
        
if __name__ == '__main__':
    rs_id_file = './test_data/rs_id_list.txt'
    nearest_gene_5p = NearestGeneFivePrime(rs_id_file)
    perl_json = nearest_gene_5p.get_perl_output_as_json()
    print perl_json
    print json.dumps(perl_json['rs1000113'])
    print json.dumps(nearest_gene_5p.get_gene_map_for_rank('rs1000113', 0))
    print json.dumps(nearest_gene_5p.get_gene_map_for_rank('rs1000113', 1))
    print json.dumps(nearest_gene_5p.get_rs_id_nearest_gene_map())
    
