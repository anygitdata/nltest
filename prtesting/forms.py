
from django import forms
import json

from app import  loadJSON_withTempl
from app import get_valFromDict, Res_proc

#import advuser, app, AnyMixin
#from advuser import modl_user
from .any_mixin import ResTesting
from app import Type_value as typeVal

#import prtesting.jsonTest as jsonTest
from prtesting import tests


class TestingForm(forms.Form):
    script = forms.CharField(label='Каталог тестирования', max_length=50, 
                             disabled=True,
                                widget=forms.TextInput(attrs={"class":"form-control"}) )
    
    @classmethod
    def SelectFilesTesting(cls, arg_par_testing):

        list_res_test = []

        path_file_arg = arg_par_testing.PR_path_file_arg

        for file in arg_par_testing.PR_files:        
            arg_proc = dict(file=path_file_arg + file, base_path=path_file_arg )

            res_arr_dict = cls.Testing(arg_proc)

            if get_valFromDict(res_arr_dict,'res') == -300:
                return Res_proc(res=-300, 
                                error= get_valFromDict(res_arr_dict,'error'), 
                                res_list=list_res_test )

            if get_valFromDict(res_arr_dict,'list_res_test'):
                for item in get_valFromDict(res_arr_dict,'list_res_test'):
                    list_res_test.append(item)
            else:
                # Поставить заглушку и вывести сообщение отсутствия данных в файле тестирования
                list_res_test.append(dict(empty_data='В файле %s нет данных для тестирования '% file))

            #list_res_test.append(get_valFromDict(res_arr_dict,'list_res_test'))            
                    
        return Res_proc(res=200, mes='Ok', res_list=list_res_test )

    @classmethod
    def conv_str_json_test(cls, arg_lst):

        res = Res_proc(res=False)

        obj_appl = jsonTest
        obj_modl = None
        for item in arg_lst[1].split('#'):
            _error = None
            if obj_modl :
                if hasattr(arg_obj_appl,item):
                    obj_modl = getattr(obj_modl, item)
                else:
                    _error = True
            else: 
                if hasattr(obj_appl, item):
                    obj_modl = getattr(obj_appl, item) 
                else:
                    _error = True

            if _error:
                res.error = 'Атрибут %s не найден' % item
                return res

        res.res = True
        res.res_obj = obj_modl

        return res


    @classmethod
    def Testing(cls, kwagrs):

        # base_path каталог в котором находятся файлы в которых находятся данные для процедуры
        #clData = self.cleaned_data
        
        list_res_test = []        

        path_file = get_valFromDict(kwagrs,'file')

        if path_file is None:
            return dict(res=-222, error='ValueError##prtesting.form.Testing Нет данных для файла теста')

        try:
            # каталог, где может быть расположен файл с параметрами для тестируемой процедуры
            base_path = get_valFromDict(kwagrs,'base_path')


            path_file = typeVal.init_formatTempl(path_file )
            scrData = loadJSON_withTempl(path_file)

            if not scrData: 
                res_test = ResTesting()
                res_test.res=-300
                res_test.error='ValueError##prtesting.form.Testing Файл не найден'
                list_res_test.append(res_test)
                return dict(res=-300, error='Файл не найден')

            for js in scrData:
                if js['stop']: continue

                dict_param_test = js['test']  # Зависимости между модулями 

                list_name_params = dict_param_test.split('.')

                res_test = ResTesting()
                res_test.name_proc = dict_param_test

                #if len(list_name_params) != 4:
                #    res_test.res = -220
                #    res_test.error = 'Ошибка формата: ' + str_param_test
                #    list_res_test.append(res_test)
                #    continue

                obj_appl    = None
                obj_modl    = None
                obj_class   = None
                obj_proc    = None
                str_proc    = ''
                list_args   = js['param']['arg']

                """ типАргумента, 
                    если type_arg=file_json -> загрузка данных для тестируемой процедуры из файла 
                    файлы-параметры для тестов в каталоге prtesting/jsonTest 
                    """
                type_arg    = get_valFromDict(js, 'type_arg')                 
                res_test.init_args(list_args)

                # инициализация приложения
                s_appl = list_name_params[0]                

                if s_appl == 'tests':
                    obj_appl = tests
                elif s_appl == 'advuser':
                    obj_appl = advuser
                elif s_appl == 'app':
                    obj_appl = app
                elif s_appl == 'AnyMixin':
                    obj_appl = AnyMixin
                else:
                    res_test.res = -220
                    res_test.error = 'Нет приложения ' + list_name_params[0]
                    list_res_test.append(res_test)
                    continue

                if hasattr(obj_appl, list_name_params[1]):
                        obj_modl = getattr(obj_appl, list_name_params[1])
                else:
                    res_test.res = -220
                    res_test.error = 'Нет модуля ' + list_name_params[1]
                    list_res_test.append(res_test)
                    continue

                # инициализация атрибута class
                str_class = list_name_params[2]
                str_proc = list_name_params[3]
                if str_class == 'empty':                    
                    if hasattr(obj_modl, str_proc):
                        obj_proc = getattr(obj_modl, str_proc)
                    else:
                        res_test.res = -220
                        res_test.error = 'В модуле нет процедуры ' + str_proc
                        list_res_test.append(res_test)
                        continue

                # инициализация объекта процедуры
                else: 
                    if hasattr(obj_modl, str_class):
                        obj_class = getattr(obj_modl, str_class)

                        # инициализация метода в объекте
                        if hasattr(obj_class, str_proc ):
                            obj_proc = getattr(obj_class, str_proc)
                        else:
                            res_test.res = -220
                            res_test.error = 'Нет процедуры ' + str_proc
                            list_res_test.append(res_test)
                            continue
                    else:
                        res_test.res = -220
                        res_test.error = 'Не найден объект %s ' % str_class
                        list_res_test.append(res_test)
                        continue

                
                # старт теста 
                res_from_test = None

                try:

                    len_arr_arg = len(list_args)

                    if not len_arr_arg:
                            res_from_test = obj_proc()
                    elif  len_arr_arg == 1: 
                        # Только с одним параметром допустимо использование загрузка данных из *.json файла
                        if type_arg == 'file_json':
                            # файлы для теста в каталоге jsonTest
                            # '/' используется как разделитель в строке path в процедуре loadJSON_withTempl
                            # расширение файла json не указывать !!!
                            if base_path :   # если не указан каталог из которого делается выборка файла
                                strPath_json = base_path + list_args[0]
                            else:
                                res_test.error = '%s : Не найден каталог для загрузки файла с параметрами' % str_proc
                                list_res_test.append(res_test)
                                continue

                            strPath_json = typeVal.init_formatTempl(strPath_json, 'jsn')
                            arg_from_json = loadJSON_withTempl(strPath_json)
                            if arg_from_json :
                                res_from_test = obj_proc(arg_from_json)
                            else:
                                res_test.res = -220
                                res_test.error = 'Данные из файла %s не загружены ' % strPath_json
                        else: 

                            # Обычный вызов процедуры с параметрами 
                            res_from_test = obj_proc(list_args[0])

                    elif len_arr_arg == 2:
                            res_from_test = obj_proc(list_args[0], list_args[1])
                    elif len_arr_arg == 3:
                             res_from_test = obj_proc(list_args[0], list_args[1], list_args[2] )

                    else:
                        res_test.res = -220
                        res_test.error = 'Кол-во параметров превышает допустимое значение = 3'

                    if res_from_test:
                        res_test.res_proc = res_from_test
                    
                    list_res_test.append(res_test)

                except Exception as e:
                    if not list_res_test:
                        return dict(res=-222, error=str(e))
                    else:
                        return dict(res=-222, error=str(e), list_res_test=list_res_test)

        except Exception as e: 
            if not list_res_test:
                return dict(res=-222, error=str(e))
            else:
                return dict(res=-222, error=str(e), list_res_test=list_res_test)

        return dict(res=200, mes='Ok', list_res_test=list_res_test)


    

