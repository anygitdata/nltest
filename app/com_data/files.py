"""
Модуль обработки доступа к файлам,
Различные манипуляции с файлами
Обработка файлов JSON
"""

import os
from nltest import settings
import json
from .any_mixin import Res_proc


__all__ = ['writeDict_into_JSON','conv_strPath',
           'loadJSON_file_modf','loadJSON_withTempl','verify_exists_file_photo']


def writeDict_into_JSON(arg_dict, arg_path):
    res = Res_proc(res=False)
    try:
        with open(arg_path, "w") as write_file:
            json.dump(arg_dict, write_file, ensure_ascii=False)

        res.res = True
        return res

    except Exception as ex:
        res.res = False
        res.error = str(ex)
        return res


# Конвертирование _path из входящего формата cat/cat1/... 
# в формат необходимый для записи в файл или поиска в каталогах
def conv_strPath(_path, sep='/'):
    BASE_DIR = settings.BASE_DIR

    sfile = ''
    if sep:
        for s in _path.split(sep):
            sfile = os.path.join(BASE_DIR, sfile, s )
    else: sfile = jsfile

    return sfile


# Модифицированная Загрузка данных из json файла
# путь к файлу прописывается в параметре
# например advuser/file.json
# расширение json не добавляется
def loadJSON_file_modf(jsfile, sep='/'):

    sfile = conv_strPath(jsfile)
    sfile += '.json'

    if not os.path.isfile(sfile): return None

    try:
        with open(sfile, 'r', encoding='utf-8' ) as f:
            data = json.load(f)
    except Exception as ex:
        return None

    return data


"""
 Загрузка объекта json по формату строки
     Единая точка для загрузки JSON файла

     path_file = Type_value.init_formatTempl(path_file ) -> создание правильного формата
     init_formatTempl(path_file, arg_templ) 
        если arg_templ is None создается шаблон {%jsn%} стандартная загрузка
        arg_templ='jdv' используется для явного указания в вызывающем коде, 
                    что jsonObject будет загружаться в развернутом виде

    ---------------- настройки для загрузки файла ---------------    
    from .files import loadJSON_withTempl
    from app.com_data.type_value import Type_value

    path = Type_value.init_formatTempl(path,'jsn')
    dict_pswcl = loadJSON_withTempl(path)

"""
def loadJSON_withTempl(arg_str):
    from .type_value import Type_value as typeVal

    if not isinstance(arg_str, str):
        raise TypeError('AnyMixin.files.loadJSON_withTempl arg_str: не соответствие типа')

    _type = typeVal.type_value(arg_str)
    if not _type.optionStr.PR_input_dict:
        raise ValueError('AnyMixin.files.loadJSON_withTempl arg_str: не соответствие идентификатора строки')

    data = loadJSON_file_modf(arg_str[7:])    

    return data


# Процедура проверки наличия файла в заданном каталоге
def verify_exists_file_photo(arg_file):
    """
        arg_templ шаблон где искать файл
        dir/dir2 и т.д. 
    """
    from app.models import spr_param_proj

    PLACEMENT_PROJECT = settings.PLACEMENT_PROJECT
    
    rec_param_spr = spr_param_proj.get_param_spr('base_catalog_photo_user') if settings.PLACEMENT_PROJECT == 'local' else spr_param_proj.get_param_spr('base_catalog_photo_user_server')


    BASE_DIR = settings.BASE_DIR

    file = BASE_DIR
    list_dir = rec_param_spr.val_param.split('/')

    for s in list_dir:
        file = os.path.join(file, s)
    
    file = os.path.join(file, arg_file)

    if not os.path.isfile(file): 
        file = rec_param_spr.path_proj  + '/empty.png'
    else:  # создать path, который будет использоваться при запуске в браузере
        file = rec_param_spr.path_proj + '/' + arg_file

    return file
