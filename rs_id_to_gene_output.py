from assign_rs_ids_to_genes import AssignRsIDsToGenes

'''
Processes and checks the output from "assign_rs_ids_to_genes.py".
Checks all the Ensembl genes against Ensembl gene information.
Retrieves the HGNC gene symbols and ensures that all ensembl gene IDs are for the
reference assembly.
'''

class RsIdToGeneOutput():
    '''
    
    '''
    def __init__(self, rs_ids, assembly_name, pg_conn=None):
        '''
        '''
        assign_genes = AssignRsIDsToGenes(rs_ids, assembly_name)
        self.gene_assignments = assign_genes.get_gene_assignments()
        self.pg_conn = pg_conn
        self.ensembl_gene_info = self._set_ensembl_gene_info()
        self.ensembl_gene_info_map = self._set_ensembl_gene_info_map()
        self.gene_name_ref_ensembl_id_map = self._set_gene_name_ref_ensembl_id_map()
        self.genes_not_in_ensembl_info = self._set_genes_not_in_ensembl_info()
        self.gene_assignment_output = self._set_gene_assignment_output()
    def _set_ensembl_gene_info(self):
        '''
        
        '''
        sql = """
          SELECT
            ensembl_gene_id,
            external_name,
            is_reference
          FROM
            lookups.ensembl_gene_info
          WHERE
            biotype = 'protein_coding'
        """
        if self.pg_conn:
            cur = self.pg_conn.cursor()
            cur.execute(sql)
            ensembl_gene_info = cur.fetchall()
            return ensembl_gene_info
        else:
            return None
    def _set_ensembl_gene_info_map(self):
        '''
        
        '''
        ensembl_gene_info_map = {}
        for row in self.ensembl_gene_info:
            (ensembl_gene_id, external_name, is_reference) = (row[0], row[1], row[2])
            gene_detail = {'external_name': external_name, 'is_reference':is_reference}
            ensembl_gene_info_map[ensembl_gene_id] = gene_detail
        return ensembl_gene_info_map
    def get_ensembl_gene_info_map(self):
        '''
        
        '''
        return self.ensembl_gene_info_map
    def _set_gene_name_ref_ensembl_id_map(self):
        '''
        
        '''
        sql = """
            SELECT
              external_name,
              ensembl_gene_id
            FROM
              lookups.ensembl_gene_info
            WHERE
              external_name IN
              (SELECT
                 external_name
               FROM
                 lookups.ensembl_gene_info
               GROUP BY
                 external_name
               HAVING
                 COUNT(ensembl_gene_id) > 1)
              AND
                is_reference = TRUE
              AND
                biotype = 'protein_coding'        
        """
        gene_name_ref_ensembl_id_map = {}
        cur = self.pg_conn.cursor()
        cur.execute(sql)
        for row in cur:
            gene_name_ref_ensembl_id_map[row[0]] = row[1]
        return gene_name_ref_ensembl_id_map
    def get_gene_name_ref_ensembl_id_map(self):
        '''
        
        '''
        return self.gene_name_ref_ensembl_id_map
    def _set_genes_not_in_ensembl_info(self):
        '''
        
        '''
        assigned_ensembl_gene_ids = []
        for row in self.gene_assignments:
            for ensembl_gene_id in row[2].split(','):
                assigned_ensembl_gene_ids.append(ensembl_gene_id)
        gene_info_ensembl_ids = [row[0] for row in self.ensembl_gene_info]
        genes_not_in_ensembl_info = list(set(assigned_ensembl_gene_ids) - set(gene_info_ensembl_ids))
        return genes_not_in_ensembl_info
    def get_genes_not_in_ensembl_info(self):
        '''
        
        '''
        return self.genes_not_in_ensembl_info
    def _set_gene_assignment_output(self):
        '''
        
        '''
        gene_assignment_output = []
        for row in self.gene_assignments:
            (rs_id, so_term, genes, distance) = (row[0], row[1], row[2], row[3])
            ensembl_gene_ids = []
            gene_names = []
            for ensembl_gene_id in genes.split(','):
                if ensembl_gene_id in self.genes_not_in_ensembl_info: continue
                gene_name = self.ensembl_gene_info_map[ensembl_gene_id]['external_name']
                gene_names.append(gene_name)
                if not self.ensembl_gene_info_map[ensembl_gene_id]['is_reference']:
                    ensembl_gene_id_ref = self.self.gene_name_ref_ensembl_id_map[gene_name]
                    ensembl_gene_ids.append(ensembl_gene_id_ref)
                    
                else:
                    ensembl_gene_ids.append(ensembl_gene_id)
            gene_assignment_output.append([rs_id, so_term, ','.join(ensembl_gene_ids), ','.join(gene_names), distance])
        return gene_assignment_output
    def get_gene_assignment_output(self):
        '''
        '''
        return self.gene_assignment_output
    def write_gene_assignment_output_to_file(self, filename):
        '''
        
        '''
        with open(filename, 'wt') as fho:
            for line in self.get_gene_assignment_output():
                fho.write('\t'.join([str(element) for element in line]) + '\n')

if __name__ == '__main__':
    from ini_params import IniParams
    from create_pg_conn_for_db import CreatePgConnForDb
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
    rs_id_file = 'test_data/rs_id_list.txt'
    rs_ids = open(rs_id_file, 'rt').read().split('\n')
    assembly_name = 'GRCh38'
    rsid_gene_output = RsIdToGeneOutput(rs_ids, assembly_name, pg_conn)
    #print rsid_gene_output.get_gene_assignment_output()
    #print rsid_gene_output.get_genes_not_in_ensembl_info()
    rsid_gene_output.write_gene_assignment_output_to_file('test_data/rs_id_to_gene_output.txt')
