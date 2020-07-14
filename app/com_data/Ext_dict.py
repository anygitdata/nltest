
"""
AnyMixin

Ext_dict
"""

import json
from .type_value import Type_value


# Используется в Ext_dict
# Регистрация и реагирование, если ранее был создан объект этого типа 
class RegisterError:
    def __init__(self, arg_type, arg_source, arg_mes):
        self.type_err = arg_type
        self.source_err = arg_source
        self.mes_err = arg_mes


"""
is_simpl_dict
is_multi_dict

Модуль для Ext_dict
"""
class base_ext_dict:
    def __init__(self, arg_dict=None):

        self.error = None
        self.dict = {}

        try:

            if arg_dict:
                arg_type = Type_value.type_value(arg_dict)

                if arg_type.is_dict or arg_type.is_list:
                    self.init_from_dict(arg_dict, arg_type)  
                    return

                if arg_type.is_str:
                    _dict = self._get_dict_FromStr(arg_dict)                
                    self.init_from_dict(_dict)

        except Exception as ex:
            if self.PR_error:
                raise SystemError ('Операции заблокированы см. подробности через PR_error')
            else:
                self.error = RegisterError(ex.__name__, 'init_dict', str(ex) )

    empty = 'empty'

    @property
    def PR_error(self):
        if self.error: return self.error
        else: return False


    def init_error(self, type_err, source_err, mes_err):
        if self.PR_error:
            raise SystemError('SystemError повторная инициализация исключения')
        self.error = RegisterError(type_err, source_err, mes_err)


    def get_arg_simplDict(self, arg_dict):
        if not isinstance(arg_dict, dict):
            return None
        key = list(arg_dict.keys())[0]
        return key


    def _del_element(self, arg_dict):

        if self.PR_error: return

        try:
            _type = Type_value.type_value(arg_dict)
        
            if _type.is_dict:
                if _type.optionDict.oneSimple:
                    key = self.get_arg_simplDict(arg_dict)
                    if key and self.dict.get(key): del self.dict[key]

                elif _type.optionDict.oneMulti:
                    key = self.get_arg_simplDict(arg_dict)
                    if key:
                        if self.dict.get(key) : # удаление элемента целиком, если есть в self.dict
                            del self.dict[key]

                        else:  # поиск и удаление по каждому из keys
                            _multiDict = arg_dict[key]   # Изменение формата и -> _del_element как multiKeys
                            self._del_element(_multiDict)
                    
                elif _type.optionDict.multiKeys:
                    for key in arg_dict.keys():
                        if self.dict.get(key) : del self.dict[key]

            elif _type.is_list:
                for item in arg_dict:
                    if isinstance(item,str):
                        del self.dict[item]
                    else:                    
                        self._del_element(item)

            elif _type.is_str:
                if _type.optionStr.lke:  # если это массив строк key разделенных пробелом
                    _list_key = arg_dict[7:].split(' ')
                    for item in _list_key:
                        if self.dict.get(item): del self.dict[item]           
        
                else:
                    # иначе загружается dict из строки -> _del_element(_dict)
                    _dict = self._get_dict_FromStr(arg_dict)
                    if _dict:
                        self._del_element(_dict)

        except Exception as ex:
            self.init_error( type(ex).__name__ ,'_del_element', str(ex))


    def init_from_dict(self, arg_dict, arg_type=None):               

        if self.PR_error: return

        try:
            if not arg_type: 
                arg_type = Type_value.type_value(arg_dict)

            if arg_type.is_str:
                arg_dict = self._get_dict_FromStr(arg_dict)
                arg_type = Type_value.type_value(arg_dict)

            if not arg_type.is_dict and not arg_type.is_list:
                self.init_error('TypeError','init_from_dict', 'base_ext_dict.init_from_dict arg_dict: не соответствие типа')
                return                

            if arg_type.is_dict and arg_type.optionDict.PR_notUpdate_dict:
                return 
        
            if arg_type.is_list:
                for item in arg_dict:
                    self.init_from_dict(item)
                return

            if arg_type.is_dict:

                # Вход для обновления self.dict 
                # в конечном итоге все манипуляции к преобразованию -> dict
                if arg_type.optionDict.oneSimple :
                     self.dict.update(arg_dict)
                     return

                if arg_type.optionDict.oneMulti or arg_type.optionDict.multiKeys:
                    if arg_type.optionDict.oneMulti_as_one:  # означает не разворачивать dict.keys(). 
                        self.dict.update(arg_dict)
                    else:  # Инициализация по каждому элементу dict 
                        self._init_from_multiDict(arg_dict)
                    return

                if arg_type.optionDict.oneList:
                    for k,v in arg_dict.items():
                        if isinstance(v, list):
                            for item in v:
                                self.init_from_dict(item)
                            return
                        if isinstance(v, dict):
                            self.init_from_dict(item)

        except Exception as ex:
            self.init_error(type(ex).__name__,'init_from_dict',str(ex))


    def _init_from_multiDict(self, arg_dict):
        if self.PR_error: return

        try:
            if not isinstance(arg_dict, dict):
                self.init_error('ValueError','_init_from_multiDict','base_ext_dict._init_from_multiDict arg_dict: не соответствие типа')
                return 

            for k,v in arg_dict.items():
                _dict = {k:v}

                # key == 'oneMulti' используется как маркер 
                # развертывания входящего dict по каждому элементу
                if k == Type_value.Option_oneMulti.get_str_oneMulti():  
                    continue

                _type = Type_value.type_value(v)
                if _type.is_dict or _type.is_list:
                    self.init_from_dict(v, _type)
                else:
                    self.init_from_dict(_dict)
        except Exception as ex:
            self.init_error(type(ex).__name__,_init_from_multiDict, str(ex) )
       

    @property
    def pr_sizeof(self): return len(self.dict.keys())

    """
    Метод на уровне класса проверяет значение arg_key
        если это строка и после удаления пробелов not None 
            возвращается значение
            иначе -> arg_default
        для других типов проверка проходит при входе isinstance(...
    """
    @classmethod
    def modify_value(cls, arg_key, arg_default=empty):
        if arg_key is None:
            return arg_default
        s_type = type(arg_key).__name__

        if s_type in ('bool','str') :
            if s_type == 'str':
                val = arg_key.strip()
                if val: 
                    return val
                else: return arg_default
            else:
                if arg_key:
                    val = 'true'
                else:
                    val = 'false'
                return val
        else:            
            return arg_key

     
    def get_val(self, arg_key, arg_Default=None):

        if self.dict.get(arg_key):
            return self.modify_value(self.dict[arg_key], arg_Default)
        else:
            return arg_Default

    # В отличие от get_val возвращает None if val=='empty'
    def get_valMod(self, arg_key):
        res = self.get_val(arg_key)
        if res == cls.empty:
            res = None

        return res 


    # Преобразование значения empty -> None
    @classmethod
    def CL_modify_empty(cls, arg_dict):
        for key, val in arg_dict.items():
            if val == cls.empty:
                arg_dict[key] = None


    # сканирует dict и замещает значения 'empty' -> None
    def modify_dict(self):
        self.CL_modify_empty(self.dict)
            #for key, val in self.dict.items():
            #    if val == cls.empty:
            #        self.dict[key] = None

    """
    По входящему шаблону tmpl_dict создать выходной dict по данным self.dict
    """
    @classmethod
    def modifyTmplDict_byExt_dict(cls, tmpl_dict, ext_dict):
        if not isinstance(tmpl_dict,dict) or not isinstance(ext_dict, dict):
            raise ValueError('Ext_dict.modifyTmplDict_byExt_dict : не соответствие типа у аргументов')

        # создание set из tmpl_dict
        set_tmpl = set()
        for key in tmpl_dict.keys():
            set_tmpl.add(key)

        # создание set из self.dict
        set_self = set()
        for key in ext_dict.keys():
            set_self.add(key)

        # Объединение set
        set_tmpl &=set_self;  # значения keys, которые есть в tmpl_dict и в self.dict            
        for key in set_tmpl:
            tmpl_dict[key] = cls.modify_value(ext_dict[key])


    """
    По входящему шаблону tmpl_dict создать выходной dict по данным self.dict
    """
    def modifyExtDict_bySelf_dict(self, tmpl_dict):

        # создание set из tmpl_dict
        set_tmpl = set()
        for key in tmpl_dict.keys():
            set_tmpl.add(key)

        # создание set из self.dict
        set_self = set()
        for key in self.dict.keys():
            set_self.add(key)

        # Объединение set
        set_tmpl &=set_self;  # значения keys, которые есть в tmpl_dict и в self.dict            
        for key in set_tmpl:
            tmpl_dict[key] = self.get_val(key, 'empty')


    # Обновить dict  из arg_dict через массив key    
    def init_from_dictExt(self, arg_dict, arg_keys):

        if self.PR_error: return

        try:
            if arg_keys:
                for key in arg_keys:
                    if arg_dict.get(key):
                        _dict = arg_dict[key]
                        _type = Type_value.type_value(_dict)
                        self.init_from_dict(_dict, _type)
            else:
                self.init_from_dict(arg_dict)
        except Exception as ex:
            self.init_error(type(ex).__name__, 'init_from_dictExt', str(ex) )


    def get_clone(self):
        if not self.dict: return {}

        if self.error: return

        res_dict = {}
        for k,v in self.dict.items():
            res_dict.update({k:v})

        return res_dict


    def verifyExists(self, arg_key):  return self.dict.get(arg_key)


    # используется для отладки, а также для вывода на консоль или браузер
    def get_str_for_print(self, arg_div='; ')->str:

        res = ''

        if not self.dict :
            return 'Нет данных в self.dict'

        for k,v in self.dict.items():
            _type = Type_value.type_value(v)
            if _type.is_model_advuser:
                prt = 'model_AdvUser'
            elif _type.is_empty:
                prt = 'empty'
            elif _type.is_model_user:
                prt = 'model_User'
            else:
                prt = v

            res += '{0:>15}: {1}{2}'.format(k, prt, arg_div)

        return res

    @classmethod
    def _get_dict_FromStr(cls, arg_str):        

        if Type_value._optionStr.verify_arg_jsn(arg_str):
            _dict = json.loads(arg_str[7:])
        # else raise TypeError из verify_arg_jsn

        return _dict


"""
Расширенное взаимодействие со словарем:
    добавление словаря
        из объекта
        из массива объектов
        из строкового идентификатора
    удаление элемента словаря 
        по dict(key=... , val=...)  удаление по key, не зависимо от значения val
        по строка   строка выступает в роли значения key
        по list(dict(...)) 
    Добавлены ВЕСЬ имеющийся функционал по обработке, выборке данных из словаря

"""    
class Ext_dict(base_ext_dict):
    
    def __init__(self, arg_dict=None):
        super().__init__(arg_dict)        


    # --------------- внутренний процедурный интерфейс ----------------        
    # Соотношение равенства объектов
    # возвращает результат сравнения двух dict
    def ver_equal(self, other, arg_file=None):        
        if not (isinstance(other, dict) or isinstance(other, Ext_dict)):
            return None

        # Проверка на соответствие key
        if isinstance(other, Ext_dict):
            _other_dict = other.dict
        else:
            _other_dict = other

        _self_dict = self.dict

        _lst_keys_other = list(_other_dict.keys())
        _lst_keys_self  = list(_self_dict.keys())

        _res_ver_dict = dict( 
                    equal_val=[], 
                    diff_val=[], 
                    self_not_keys=[], 
                    other_not_keys=[])
        _list_buf = []
        for key in _lst_keys_self:
            if key not in _lst_keys_other:
                _list_buf.append(dict(key=key, val=_self_dict[key]))
                
        _res_ver_dict['self_not_keys']= _list_buf

        _list_buf = []
        for key in _lst_keys_other:
            if key not in _lst_keys_self:
                _list_buf.append(key)
        _res_ver_dict['other_not_keys'] = _list_buf
        # конец блока проверки соотношений по ключам

        for key in _lst_keys_self:
            if key in _lst_keys_other:
                # проверка типов
                if _self_dict[key] and (type(_self_dict[key]) != type(_other_dict[key])):
                    _res_ver_dict['diff_val'].append(
                        dict(key=key, 
                             val_self=_self_dict[key],  
                             val_other= 'Не совпТипа: %s' % str(_other_dict[key])   ))
                else:
                    if _self_dict[key] != _other_dict[key]:
                        _res_ver_dict['diff_val'].append(
                            dict(key=key, 
                                 val_self=_self_dict[key],  
                                 val_other= _other_dict[key] ))
                    else:
                        _res_ver_dict['equal_val'].append(
                            dict(key=key, val=_self_dict[key] ))
        if arg_file:
            try:
                with open(arg_file, "w") as write_file:
                    json.dump(_res_ver_dict, write_file, ensure_ascii=False) 
            except Exception as ex:
                _res_ver_dict.update(dict(error=str(ex)))

        return _res_ver_dict


    """ 
    self.dict + other
    К встроенному dict добавление other 
    Параметры могут быть :
        dict  - обычный одноуровневый
        list  - список, содержащий dict
        str   - dict преобразованный в строку
    """
    def __add__(self, other):

        _type = Type_value.type_value(other)
        
        if _type.is_Ext_dict:  #if isinstance(other, Ext_dict):
            self.__add__(other.dict)
            return

        if _type.is_dict or _type.is_list or _type.is_str:
            self.init_from_dict(other, _type)

        return self


    """
       Из встроенного dict  вычитание  other - dict
       other может быть:
        dict
        str
        list(dict)
    """
    def __sub__(self, other):

        if isinstance(other, Ext_dict):
            self.__sub__(other.dict)
            return self

        self._del_element(other)

        return self


    # self += other
    def __pos__(self, other):
        self.__add__(other)

    #self -=other
    def __neg__(self, other):
        self.__sub__(other)


