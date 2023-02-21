from os.path import abspath, dirname


res_folder_path = abspath(dirname(__file__)) + '/'
conf_json_path = res_folder_path + 'conf.json'
latest_txt_path = res_folder_path + 'latest.txt'
notebook_path = res_folder_path + 'notebook.txt'
online_cache_path = res_folder_path + 'online_cache.json'
usr_word_path = res_folder_path + 'usr_word.json'
dict_en_ind_path = res_folder_path + '/dict/en.ind'
dict_en_z_path = res_folder_path + '/dict/en.z'
dict_zh_ind_path = res_folder_path + '/dict/zh.ind'
dict_zh_z_path = res_folder_path + '/dict/zh.z'
start_bat_path = res_folder_path + '/start.bat'
pid_file_path = res_folder_path + 'pid'


def get_start_bat_path():
    print(start_bat_path)


__all__ = ['conf_json_path', 'latest_txt_path', 'notebook_path', 'online_cache_path', 'usr_word_path', 'res_folder_path', 'dict_zh_z_path', 'dict_en_z_path',
           'dict_zh_ind_path', 'dict_en_ind_path', 'get_start_bat_path', 'pid_file_path']
