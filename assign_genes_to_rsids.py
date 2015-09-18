from ini_params import IniParams
from create_pg_conn_for_db import CreatePgConnForDb
from rs_id_to_gene_output import RsIdToGeneOutput

ini_file_path= '/Users/mmaguire/cttv_gitlab/pgloader/db_config.ini'
database_ini_key = 'POSTGRESQL_TEST_DOCKER_DEV04'
inip = IniParams(ini_file_path)
(host, database_name, port, user) = (inip.get_ini_option_value(database_ini_key,'host'),
                                     inip.get_ini_option_value(database_ini_key, 'database_name'),
                                     inip.get_ini_option_value(database_ini_key, 'port'),
                                     inip.get_ini_option_value(database_ini_key, 'username'))
# Create a database handle for the target database
conn_creator = CreatePgConnForDb(database_ini_key, ini_file_path)
pg_conn = conn_creator.get_pg_conn_for_db()
rs_id_file = '/Users/mmaguire/CTTV/cttv018_ibd_gmas/rs_ids.txt'
rs_ids = open(rs_id_file, 'rt').read().split('\n')
assembly_name = 'GRCh38'
rsid_gene_output = RsIdToGeneOutput(rs_ids, assembly_name, pg_conn)
#print rsid_gene_output.get_gene_assignment_output()
#print rsid_gene_output.get_genes_not_in_ensembl_info()
rsid_gene_output.write_gene_assignment_output_to_file('/Users/mmaguire/CTTV/cttv018_ibd_gmas/cttv_gene_assignments.txt')