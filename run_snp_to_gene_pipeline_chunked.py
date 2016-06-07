import sys
import os
from subprocess import Popen, PIPE
'''
To be run for SNP lists >20K.
Creates sub-files that are then fed to "run_snp_to_gene_pipeline.py"
'''

def chunk_list(input_list, chunk_size=5000):
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

big_rs_id_file = sys.argv[1]
rs_id_list = [rs_id.strip() for rs_id in open(big_rs_id_file, 'rt').read().split('\n')]
target_dir = os.path.dirname(big_rs_id_file)
file_name = os.path.basename(big_rs_id_file)
(name, ext) = os.path.splitext(file_name)
chunk = 0
run_cmd_template = 'python run_snp_to_gene_pipeline.py %s %s'
for sub_list in chunk_list(rs_id_list, 500):
    chunk += 1
    subfile = os.path.join(target_dir, (name + '_chunk_' + str(chunk) + ext))
    subfile_out = os.path.join(target_dir, (name + '_chunk_' + str(chunk) + '_output' + ext))
    fho = open(subfile, 'wt')
    fho.write('\n'.join(sub_list))
    run_cmd = run_cmd_template % (subfile, subfile_out)
    print run_cmd
    p = Popen(run_cmd, stdout=PIPE, stderr=PIPE, shell=True)
    stdout, stderr = p.communicate()
    if len(stderr) >0:
        raise Exception('Error thrown: %s' % stderr)
    fho.close()

