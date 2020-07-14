
"""
Модуль вспомогательных процедур

Поля данных теста из RegUserForm
"""

import json

from app import loadJSON_file_modf
from app import get_valFromDict


class Params_testing:
    # Каталог по которому проводятся тесты    
    base_directory = 'prtesting/tests/'

    def __init__(self):

        base_path = Params_testing.base_directory


        dict_from_file = loadJSON_file_modf(Params_testing.base_directory + 'test_path')
        if dict_from_file is None:
            raise ValueError('Файл не найден')

        path_redirect_test = get_valFromDict(dict_from_file,'path')

        self._base_directory = get_valFromDict(path_redirect_test,'directory')
        if self._base_directory is None:
            self._base_directory = 'jsonTest'

        self._path_file_arg = '%s%s/' % (base_path, self.PR_base_directory if self.PR_base_directory != 'jsonTest' else '' )

        path_for_test = loadJSON_file_modf(self.PR_path_file_arg+'test_path')
        path_for_test = path_for_test['path']
        self._files = get_valFromDict(path_for_test,'files')


    @property
    def PR_path_file_arg(self):
        return self._path_file_arg

    @property
    def PR_files(self):
        return self._files

    @property
    def PR_base_directory(self):
        return self._base_directory


class ResTesting:
    def __init__(self, res=None, name_proc=None, res_proc=None, args=None, error=None ):
        self.res = res
        self.name_proc = name_proc
        self.res_proc = res_proc
        self.args = args
        self.error = error

    def init_args(self, list_args):
        s_arg_test = ''
        for s in list_args:
            s_arg_test += ' ' + s if isinstance(s, str) else str(s)

        self.args = s_arg_test
    
