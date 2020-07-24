"""
modify_models.py

class insert/update моделей
"""

from django.contrib.auth.models import User
import json

from app import Ext_dict, getUser, getLogin_cl, getPassword_cl
from app import Res_proc, ErrorRun_impl, TypeError_system 
from app.com_data.any_mixin import CreateUser_ext

from .models import AdvUser, SprStatus
from app.models import spr_fields_models

#********************************
# Используется из Modify_advuser and Modify_user
class Init_model:    

    def __init__(self, argObj, argDict):

        self.username = None
        self.obj_model = argObj       # задумано для инициализации модели 
        self.ext_dict = Ext_dict(argDict)          
        self.list_fieldsModel = argDict.get('list_fieldsModel')
        if not self.list_fieldsModel:
            raise ErrorRun_impl('ValueError##Init_model.__init__: argDict[list_fieldsModel] нет данных')

        s_type = type(argObj).__name__
        if s_type == 'User': self.username = argObj.username
        if s_type == 'AdvUser': self.username = argObj.user.username

        self._init_field_from_dict()
        if isinstance(self.obj_model, AdvUser):
            self._init_advdata()

    #----------- Конец блока инициализации -------------    


    def _init_field_from_dict(self):        
        from .serv_sprstatus import Com_proc_sprstatus

        _getVal = self.ext_dict.get_val


        for key in self.list_fieldsModel:

            if key == 'username': continue

            if not hasattr(self.obj_model, key): continue
                                
            if key == 'status_id':
                _id = _getVal(key)
                if not _id: continue

                _spr = Com_proc_sprstatus.getStatus_or_None (_id)
                if _spr:
                    """
                        Это заполнение используется при обновлении,
                        но при новой записи этот идентификатор None
                        поэтому заполнение поля status делается в условии
                    """
                    setattr(self.obj_model, 'status', _spr )
                    continue    
                else:
                    raise ErrorRun_impl('ValueError##Init_model._init_field_from_dict: status={0} не определен'.format(_id))

            if key == 'sendMes':
                _val  = True if _getVal('sendMes') == 'true' else False
                setattr(self.obj_model, key, _val )
                continue

            val = _getVal(key) 
            if val:
                _val = None if val == 'empty' else val
                setattr(self.obj_model, key, _val )


    # используется для инициализации поля advuser.advData  
    def _init_advdata(self):
        from app import Ext_dict

        _status = self.obj_model.status

        # это исходный шаблон 
        tmp_dict = spr_fields_models.get_list_fields_advDataExt(_status)
        if tmp_dict is None:
            raise ErrorRun_impl('ValueError##modify_models.Init_model._init_advdata _status: None стр.67')

        # шаблон заполненный по данным предОбработки
        _advData = AdvUser.get_advData(self.username)
        if _advData:
            # обновление tmp_dict исходными значениями
            Ext_dict.modifyTmplDict_byExt_dict(tmp_dict, _advData)

        # logincl and pswcl в форме не заполняются, поэтому загружаются из предОбработки
        # наложение данных, полученных из заполнения формы
        self.ext_dict.modifyExtDict_bySelf_dict(tmp_dict)

        s_advdata = json.dumps(tmp_dict, ensure_ascii=False)
        self.obj_model.advData = s_advdata
        

#********************************

# Операции с моделью AdvUser
class Modify_advuser:
    
    def add_advuser(user, arg_dict, commit=True):
        res = Res_proc(res=False)

        if not isinstance(user, User):
            raise ValueError('Отсутствует аргумент User')

        advuser = None
        advData = None

        advuser = AdvUser()
        advuser.user = user


        # Заполнение списка полей, используемых для этой модели
        arg_dict['list_fieldsModel'] = spr_fields_models.get_list_fields('advuser', onlyKeys=True, exclude='advData')
        init_advUser = Init_model(advuser, arg_dict)
        res.res_model = advuser

        if commit:
            try:
                advuser.save()
                res.mes = 'Создана модель AdvUser'
                res.res = True

                return res

            except Exception as ex:
                res.error = ex
                return res

        else:
            res.mes = 'Заполнены данные для профиля'
            res.res = True
            return res


    # Изменение модели
    def  update_advuser(user, arg_dict, commit=True):

        res = Res_proc(res=False)
        advuser = None
        advData = None
        
        advuser =  AdvUser.get_advUser(user)
        if advuser is None:
            res.error = 'ValueError##modify_models.Modify_advuser.update_advuser: Нет данных в AdvUser стр.150'
            return res            


        # Заполнение списка полей, используемых для этой модели
        arg_dict['list_fieldsModel'] = spr_fields_models.get_list_fields('advuser', onlyKeys=True, exclude='advData')

        for key,val in arg_dict.items():
            if val == res.PR_empty:
                arg_dict[key] = None

        init_advUser = Init_model(advuser, arg_dict)

        res.res_model = advuser
        if commit:
            try:
                advuser.save()
                res.mes = 'Выполнено обновление модели AdvUser'
                res.res = True

            except Exception as ex:
                res.error = ex
                return res
        else:
            res.mes = 'Заполнены данные для профиля'
            res.res = True

        return res


class Modify_user:

    @classmethod
    def add_user(cls, arg_dict:dict):        

        if not isinstance(arg_dict, dict):
            raise ValueError('arg_dict не соответствие типа')                
                

        res = Res_proc() 
        ext_dict = Ext_dict(arg_dict)

        tmp_dict = spr_fields_models.get_list_fields('user')
        ext_dict.modifyExtDict_bySelf_dict (tmp_dict)

        tmp_dict.update(dict(password=ext_dict.get_val('password')))
        user = CreateUser_ext.create_user(
                        username=tmp_dict['username'],
                        email = tmp_dict['email'] if tmp_dict['email'] !='empty' else None ,
                        password= tmp_dict['password']
                    )
        user.first_name = tmp_dict['first_name']
        user.last_name  = tmp_dict['last_name']

        res.res_model = user

        try:
            user.save()
            res.mes = 'Создан профиль участника проекта'
            res.res = True

            return res

        except Exception as ex:
            res.error = ex
            return res

    @classmethod
    def update_user(cls, user, arg_dict, commit=True):
        from app.models import spr_fields_models

        res = Res_proc(res=False)

        # Блок заполнения полей User для существующего пользователя
        if not isinstance(user, User):
            user = getUser(user)
            if user is None: 
                res.error ='ValueError##modify_models.Modify_user.update_user user Нет данных для логина стр.213'
                return res

        # Заполнение списка полей, используемых для этой модели
        arg_dict['list_fieldsModel'] = spr_fields_models.get_list_fields('user', onlyKeys=True)
        init_user = Init_model(user, arg_dict)
        
        res.res_model = user
        if commit:
            try:
                
                user.save(force_update=True)
                res.mes = 'Выполнено обновление модели User'
                res.res = True

            except Exception as ex:
                res.error = ex
                return res
        else:
            res.mes = 'Заполнены данные для модели User'
            res.res = True

        return res


# Базовый для Conv_advuser_into_dict and Conv_user_into_dict
class Conv_model_into_dict:
    def __init__(self, arg_model=None, arg_file=None):
        self.model = arg_model
        self.dict = {}
        self.file = arg_file


    def load_into_file(self):
        if not self.file: 
            return

        if not self.dict:
            _load_dict = dict(res=False, error='Нет данных для модели')
        else:
            _load_dict = self.dict

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        s_file = os.path.join(base_dir, self.file)


        if isinstance(self.model, User):
            _load_dict.update(dict(username= self.model.username))
        else:
            _load_dict.update(dict(username=_load_dict['user'].username))

        if _load_dict.get('user'):
            del _load_dict['user']

        try:
            with open(s_file, "w") as write_file:
                json.dump(_load_dict, write_file, ensure_ascii=False) 
                return dict(res=True, mes='Структура модели выгружена в файл: %s' % self.file)
        except Exception as ex:
            return dict(res=False, error=str(ex))

# Используется для извлечения данных, соответствующих advData
# advData содержит в виде dict ВСЕ данные по User
def initDict_from_advData(arg_advData, arg_statusID):

    perm_status = ('SprStatus','str')
    s_type_status = type(arg_advData).__name__
    if s_type_status not in perm_status:        
        raise ValueError('initDict_from_advData arg_statusID: не соответствие типа')

    perm_advData = ('str', 'dict')
    s_type_advData = type(arg_advData).__name__
    if s_type_advData == 'str':
        arg_advData = json.loads(arg_advData)

    tmp_dict = spr_fields_models.get_list_fields_advDataExt(arg_statusID)
    Ext_dict.modifyTmplDict_byExt_dict(tmp_dict, arg_advData)

    return tmp_dict


"""
testing:  
    modul: tests.advuser.test_advuser_user  
    procedure:test__class_ext_dict_on_association
    fileTesting: tests/advuser/advuser/test_modify_models

Конвертирование модели AdvUser into dict
    входящие аргументы:
    arg_model:
        типДанных str, int, User, AdvUser
            для str, int преобразование в User затем в AdvUser
    arg_file используется из Conv_model_into_dict для вывода данных в файл
"""
class InitDict_fromAdvuser(Conv_model_into_dict):
    def __init__(self, arg_model, arg_file=None):
        self.user  = None        

        _user = None
        perm_type = 'str, int, User, AdvUser'
        s_type = type(arg_model).__name__
        if s_type not in perm_type:
            raise ValueError('InitDict_fromAdvuser.__init__ arg_model: тип данных не определен ')

        if s_type == 'User':
            _user = arg_model
            arg_model = _user.advuser
        elif s_type == 'AdvUser':
                _user = arg_model.user

        else: # Последний вариант -> это идентификатор Use
            _user = getUser(arg_model)
            if _user:
                arg_model = _user.advuser
            else:
                raise ValueError('InitDict_fromAdvuser.__init__ arg_model: нет данных для User ')

        if not _user:
            raise ValueError('InitDict_fromAdvuser.__init__ arg_model: нет данных для User ')

        super().__init__(arg_model, arg_file)
        
        self.user = _user
        self._conv_into_dict()
            

    def _conv_into_dict(self):        

        if not self.model: return

        _advuser = self.model
        dict_model = {}

        tmp_dict_advuser = spr_fields_models.get_list_fields('advuser', exclude='advData')
        keys_tmp_dict = tuple(tmp_dict_advuser.keys())

        for key in keys_tmp_dict:
            if hasattr(_advuser, key):
                val = getattr(_advuser, key)
                if key == 'status':
                    val = val.pk

                dict_model.update({key:val})

        # Результирующий dict из объединения ext_dict.dict and tmp_dict_advuser
        Ext_dict.modifyTmplDict_byExt_dict(tmp_dict_advuser, dict_model)
        self.dict = tmp_dict_advuser

        # Выборка данных из advData
        dict_advData = initDict_from_advData(_advuser.advData, _advuser.status)
        
        self.dict.update(dict_advData)


"""
testing:  
    modul: tests.advuser.test_advuser_user  
    procedure:test__class_ext_dict_on_association
    fileTesting: tests/advuser/advuser/test_modify_models

Конвертирование модели User into dict
    Входящие аргументы:
        arg_mode:  типДанных str, int, User        
        если типДанных str or int -> преобразование в User
    arg_file используется из Conv_model_into_dict для вывода данных в файл
"""
class InitDict_fromUser(Conv_model_into_dict):
    from app.com_data.any_mixin import get_listKeys_user

    def __init__(self, arg_model, arg_file=None):

        s_type = ('User','str', 'int')

        if type(arg_model).__name__ in s_type:
            if s_type == 'User':
                self.model = arg_model
            else:
                arg_model = getUser(arg_model)
                if not arg_model:
                    raise TypeError('InitDict_fromUser.__init__ arg_model: не данных')
        else:
            raise TypeError('InitDict_fromUser.__init__ arg_model: не соответствие типа')

        if not arg_model:
            raise TypeError('InitDict_fromUser.__init__ arg_model: arg_mode не определен')

        super().__init__(arg_model, arg_file)

        self._conv_into_dict()


    def _conv_into_dict(self):

        tmp_dict = spr_fields_models.get_list_fields('user')
        _user = self.model

        _dict = {}
        _dict.update(dict(user_id=_user.pk, full_name=_user.get_full_name()))
        
        for key in tmp_dict.keys():
            if hasattr(_user,key):
                val = getattr(_user, key)
                _dict.update({key:val})

        # Заполнение tmp_dict данными из _dict
        # здесь же будут произведены все преобразования as default
        Ext_dict.modifyTmplDict_byExt_dict(tmp_dict, _dict)
        self.dict = tmp_dict


"""
testing: 
    modul:   tests.advuser.test_advuser_user
    procedure: test__class_ext_dict_forUpdate
    fileTesting: tests/advuser/advuser/test_modify_models

    Обновление поля AdvUser.advData 
        ввод данных по всем моделям: User, AdvUser, AdvUser.advData

Входящий аргумент arg_list м\быть типом:
    'str','int','list','tuple', 'User'
    'str','int' -> преобразуются к типу AdvUser
    'tuple'     -> в цикле преобразуются к типу AdvUser и добавляются self.lst_advuser
    
"""
class UpdateField_advData:

    def __init__(self, arg_list):
        self.lst_advuser = []  # список user.advuser
        self.error = []

        #------ верификация arg_list и инициализация self.lst_advuser ------
        perm_type = ('str','int','list','tuple', 'User')
        s_type = type(arg_list).__name__

        if s_type not in perm_type:
             self.error('UpdateField_advData.UpdateField_advData arg_list: не соответствие типа')
             return

        if s_type == 'str' and arg_list=='*': # Выбрать Все        
            res = []
            for item in AdvUser.objects.all():
                res.append(item)
            arg_list = res

        elif s_type in ('str', 'int') : # Одиночный строковый идентификатор User
            _advuser = AdvUser.get_advUser(arg_list)
            if _advuser:
                self.lst_advuser.append(_advuser)
            else:
                self.error.append('Идентификатор {0} не определен как User'.format(arg_list))

        elif s_type in  'list tuple'.split(' '):
            res = []
            perm_type = 'int str User'.split(' ')

            for item in arg_list:
                s_type = type(item).__name__

                if s_type not in perm_type:
                    self.error.append('Не соответствие типа')                                   

                else:
                    _advuser = AdvUser.get_advUser(item)
                    if _advuser: 
                        res.append(_advuser)
                    else:
                        self.error.append('Нет данных в advuser')
            if res:
                self.lst_advuser = res
                
        else: # Значит это User
            if isinstance(arg_list, User):
                _advuser = AdvUser.get_advUser(arg_list)
                if _advuser:
                    self.lst_advuser.append(_advuser)
                else:
                    self.error.append('UpdateField_advData.UpdateField_advData arg_list: нет данных для advuser')

            else:
                self.error.append('UpdateField_advData.UpdateField_advData arg_list: не соответствие типа ')

        if not self.lst_advuser:
            self.error.append('Не заполнен список для обработки')

    # Процедура обновления модели в БД 
    def modifyModel(self):

        res = []
        
        if self.error:
            res.append('Ошибка при инициализации')
            return res


        for key in self.lst_advuser:
            try:
                data = initDict_allModels(key.user)
                advData = json.dumps(data, ensure_ascii=False)

                AdvUser.objects.filter(pk=key).update(advData=advData)
                s_res = 'Обновлено: {0} {1}'.format(data['username'],  data['full_name'])
                res.append(s_res)

            except Exception as ex:
                res.append('error user_id:{1} {0}'.format(str(ex), key))                
                self.error.append('{0} {1} {2}'.format(type(ex).__name__, 'UpdateField_advData.modifyModel', str(ex) ))
                continue

        return res


"""
testing:  
    modul: test_advuser_user   
    file for testing: tests/advuser/advuser/test_modify_models

 Процедура создания общего dict по ВСЕМ моделям: User, AdvUser, AdvUser.advData
"""
def initDict_allModels(arg_user):
    try:
        dict_user = InitDict_fromUser(arg_user)
        dict_advuser = InitDict_fromAdvuser(dict_user.model)

        res_dict = dict_user.dict
        res_dict.update(dict_advuser.dict)

        return res_dict
    except Exception as ex:
        raise ValueError('modify_models.initDict_allModels: '+ str(ex))


"""
testing:
    file: tests/advuser/advuser/test__class_type_statusext.json
    modul: tests.advuser.test_advuser_user
    procedure: test__get_dictData_init_Form

Процедура выборки данных для редактирования профиля
"""
def get_dictData_init_Form(user, usercl):
    """ Процедура выборки данных для редактирования профиля """

    from .serv_typestatus import type_status_user
    from .serv_advuser import Com_proc_advuser


    res_proc = Res_proc(res=False)
    def run_raise(s_arg, showMes=None):
        s_err = 'modify_models.get_dictData_init_Form'

        if showMes:            
            raise ErrorRun_impl('verify##{0}'.format(s_arg))
        else:
            raise ErrorRun_impl('{0} {1}'.format(s_err, s_arg))

    # -------------------------------------------------------


    try:
        # ----------------- инициализация базовых параметров -------------------
        user = getUser(user)
        usercl = getUser(usercl)

        if user is None or usercl is None:
            run_raise('user or usercl is None')                            

        if usercl.is_superuser:
            run_raise('Профиль суперПользователя не меняется')    
            
        if usercl.username == user.username:
            run_raise('Свой профиль изменяется из панели Профиль', True)

        # ------------- Конец блока инициализации базовых параметров -------------


        type_status_cl = type_status_user(usercl)
        if not type_status_cl:
            run_raise('ошибка из advuser.models.Type_status_userExt(usercl')
                
        type_status_user = type_status_user(user)
        if not type_status_user:
            run_raise('ошибка из advuser.models.Type_status_userExt(user')
            
        # Профиль изменяется пользователями со статусом subheader, headerexp, proj-head,
        if type_status_cl.levelperm in (10,20): 
            run_raise('Профиль гостевого входа не меняется', True)

        if type_status_cl.levelperm == 100 : 
            run_raise('Изменение из панели Профиль под учетной записью рукПроекта', True)

        if type_status_user.levelperm  < 40:
            run_raise('Нет прав на изменение профиля', True)

        # выборочная верификация прав 
        levelperm_cl = type_status_cl.levelperm
        levelperm_user = type_status_user.levelperm

        if levelperm_user == 40 and levelperm_cl > 39:
            run_raise('Нет прав на изменение профиля рукГруппы', True)
        if levelperm_user == 70 and levelperm_cl > 69:
            run_raise('Нет прав на изменение профиля супер рукГруппы', True)
        

        # Загрузка данных из user.advuser.advData
        advData = Com_proc_advuser.get_advData(usercl)

        if not advData:
            run_raise('Нет данных для профиля. Обратитесь к рукГруппы',True)
            
        for key, val in advData.items():
            if val == res_proc.PR_empty:
                advData[key]=None

        res_proc.res = True
        res_proc.res_dict = advData

    except Exception as ex:
        res_proc.error = ex

    return res_proc

             
#**********************************

def get_dictData_init_Form_regQuest(user):        
    """ Инициализация базовых данных для измПрофиля участПроекта """

    from .serv_advuser import servAdvUser_get_advUser

    res_proc = Res_proc(res=False)
    perm_type = 'User, str, int'
    s_typeUser = type(user).__name__


    # ----------------- инициализация базовых параметров -------------------
    if 2>1:
        if user is None :
            res_proc.error = 'modify_models.get_dictData_init_Form_regQuest: user None'
            return res_proc

        if s_typeUser not in perm_type:
            res_proc.error = 'modify_models.get_dictData_init_Form_regQuest: user не соответствие типа'
            return res_proc

        if s_typeUser in ('str','int'):
            _user = getUser(user)
            if _user is None:
                res_proc.error = 'modify_models.get_dictData_init_Form_regQuest: user нет в БД'
                return res_proc
            else: user = _user        

        if user.is_superuser: # if type_status.is_proj_sadm:
            res_proc.error = 'Профиль superuser не меняется'
            return res_proc 

        advuser = servAdvUser_get_advUser(user)
        if advuser is None:
            res_proc.error = 'Для {0} нет данных для профиля'.format(user.get_full_name())
            return res_proc

    # ------------- Конец блока инициализации базовых параметров -------------

    dict_models = initDict_allModels(user)

    for key, val in dict_models.items():
        if val == res_proc.PR_empty:
            dict_models[key] = None

    res_proc.res = True
    res_proc.res_dict = dict_models


    return res_proc


def get_num_count_record_prof_data(arg_user, arg_list=None):
    """ """
    from app.com_serv_dbase.serv_modf_profil import serv_get_data_prof

    res = serv_get_data_prof(user, arg_list, num_count=1)

    return res;


"""
Создание списка данных для отображения в шаблоне prof_table_format
Предназначено для руководителей групп 
"""
def get_list_prof_memb(arg_user, arg_list=None, num_rows=5, sel_page=1):   
    """ Создание списка данных для отображения в шаблоне prof_table_format
    Предназначено для руководителей групп  
    Загрузка данных из БД
    arg_list формат '30,49,70'  строка levelperm
    num_rows кол-во записей в одной странице
    sel_page номер извлекаемой страницы    
    """
    
    from .serv_advuser import Struct_default_AdvUser as Struct_def
    from app.com_serv_dbase.serv_modf_profil import serv_get_data_prof
    import json

    def run_raise(s_arg, showMes=None):
        s_err = 'ValError##advuser.modify_models.get_list_prof_memb'

        if showMes:            
            raise ErrorRun_impl('verify##{0}'.format(s_arg))
        else:
            raise ErrorRun_impl('{0}: {1}'.format(s_err, s_arg))
    #---------------------------------------------------------

    res_proc = Res_proc();
    res_list = []

    arg_list = arg_list or '30,40,70'      

    try:
        user = getUser(arg_user)

        if user is None:
            run_raise('Пользователь не определен', True)

        res_data = serv_get_data_prof(user, arg_list, num_rows, sel_page, num_count=0)

        for item in res_data.res_list:
            _dict = json.loads(item['advData'])

            _dict['levelperm']  = item['levelperm']
            _dict['status']     = Struct_def.conv_status_into_str(_dict.get('status_id'))
            _dict['pol']        = Struct_def.conv_pol(_dict.get('pol'))
            _dict['sendMes']    = Struct_def.conv_send_mes(_dict.get('sendMes'))

            _dict['idcomp']     = res_proc.FN_get_val_dict(_dict, 'idcomp') or Struct_def.idcomp
            _dict['email']      = res_proc.FN_get_val_dict(_dict, 'email') or Struct_def.email
            _dict['ageGroup']   = res_proc.FN_get_val_dict(_dict, 'ageGroup') or Struct_def.ageGroup
            _dict['phone']      = res_proc.FN_get_val_dict(_dict, 'phone') or Struct_def.phone
            _dict['post']       = res_proc.FN_get_val_dict(_dict, 'post') or 'Нет'
            _dict['logincl']    = res_proc.FN_get_val_dict(_dict, 'logincl') or 'Нет'

            res_list.append(_dict)

        res_proc.res_list = res_list
        res_proc.res = True


    except Exception as ex:
        res_proc.error = ex

    return res_proc