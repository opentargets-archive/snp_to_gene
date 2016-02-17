import re

class CleanupRsIdList(object):
    delimiters = ':|'
    def __init__(self, rs_id_list):
        '''

        :param rs_id_list: list
        :return: None
        '''
        self._rs_id_list = [rs_id.strip().lower() for rs_id in rs_id_list]
        self.extended_list = self.__make_extended_list()
    def __make_extended_list(self):
        '''

        :return: list
        '''
        extended_list = []
        re_split_pat = '[' + CleanupRsIdList.delimiters + ']'
        for rs_id in self._rs_id_list:
            if re.search(r'^rs\d+$', rs_id):
                extended_list.append(rs_id)
            elif re.search('^rs\d+' + re_split_pat + 'rs\d+', rs_id):
                extended_list.extend(re.split(re_split_pat, rs_id))
        return extended_list
    def get_cleaned_rs_id_list(self):
        '''

        :return: list
        '''
        return self.extended_list

if __name__ == '__main__':
    rs_id_list = open('/Users/mmaguire/CTTV/cttv009_gwas_catalog/rs_id_list_20160217.txt', 'rt').read().split('\n')
    cleaned_rs_id_list = CleanupRsIdList(rs_id_list).get_cleaned_rs_id_list()
    print '\n'.join(cleaned_rs_id_list)
