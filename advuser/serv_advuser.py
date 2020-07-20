
from django.contrib.auth.models import User
import json
from app import getUser, Res_proc, ErrorRun_impl, TypeError_system
from .serv_typestatus import type_status_user


# Кортежи для classForm
POL = (('М','Муж'),('Ж','Жен'))
GET_MES = (('true','Да'),('false','Нет'))
ID_COMMAND = ((1, 'Изменить профиль'), (2,'Изменить пароль'), (0, 'Изменить статус')  )

 
"""
return res_proc.res_model = AdvUser  or  res_proc.error = Строка сообщения
    
    onError -> res_proc.error = Строка сообщения
    if res_proc   -> False

"""
def servAdvUser_get_advUser(arg_user):
    from .models import AdvUser    

    def _run_raise(cls, s_arg, showMes=None):
            _s_err = 'SyntaxError##advuser.serv_advuser.servAdvUser_get_advUser'

            if showMes:            
                raise ErrorRun_impl('verify##{0}'.format(s_arg))
            else:
                s_mes = '{0} {1}'.format(_s_err, s_arg)
                TypeError_system(ErrorRun_impl(s_mes))  # запись в файл app/loggin/*.log

                raise ErrorRun_impl(s_mes)
    #-----------------------------------------------------------------

    res_proc = Res_proc()

    try:
        _user = getUser(arg_user)
        if _user is None:
            _run_raise('Пользователь не определен User')

        row = AdvUser.objects.filter(user=_user)
        if row.exists():
            res_proc.res_model = row.first()
            res_proc.res = True

        else:
            _run_raise( 'Нет данных AdvUser')

    except Exception as ex:
        res_proc.error = ex


    return res_proc


"""
 testing 20.05.2020
    modul prtests.tests.advuser.test_serv_advuser
    procedure: test_modf_dict_by_setting_def
    file: tests/advuser/serv_advuser/test_serv_advuser.json
"""
def modf_dict_by_setting_def(arg_dict:dict):

    dc_attr = Struct_default_AdvUser.dc_attr
    dc_procConv = Struct_default_AdvUser.dc_procConv
    dev_val = dc_attr['def_val']

    lst_key = arg_dict.keys()
    for key in lst_key:
        val = Res_proc.FN_get_val_dict(arg_dict, key)

        if val is None:
            if dc_attr.get(key):
                arg_dict[key] = dc_attr[key]                
            else:
                arg_dict[key] = dev_val
        else:
            if dc_procConv.get(key):
                s_proc = dc_procConv[key]
                proc = getattr(Struct_default_AdvUser, s_proc)
                conv_data = proc(val) # процедура конвертирования
                arg_dict[key] = conv_data


# Нет ссылок на этом class modf_dict_by_setting_def
class Struct_default_AdvUser:    

    phone = 'Нет'
    email = 'Нет'
    full_name = 'Нет'
    full_name_su = 'СуперПользователь'
    psw = 'Нет'
    status = '-'
    statusID = '-'
    limitcon = 'откл'
    ageGroup = '-'        
    pswcl = 'Нет'
    logincl = 'Нет'
    idcomp = 'Не зарегистрирован'
        

    @classmethod
    def conv_pol(cls, arg_char:str):
        s_pol = '-'
        _empty = Res_proc.FN_empty()

        pol = arg_char or cls.pol
        if pol == _empty: pol = '-'

        if pol != '-':
            for p in POL:
                if p[0] == pol.upper():
                    s_pol = p[1]
                    break

        return s_pol

    @classmethod
    def conv_send_mes(cls, arg_send:str):
        res = 'Нет'

        if arg_send and arg_send.lower() == 'true':
            res = 'Да'

        return res

    @classmethod
    def conv_status_into_str(cls, statusID:str):        
        from .serv_sprstatus import Com_proc_sprstatus 

        res = cls.statusID

        status = Com_proc_sprstatus.getStatus_or_None(statusID)
        if status:
            res = status.strIdent

        return res


    dc_attr = dict(
        phone=phone,
        email=email,
        full_name=full_name,
        full_name_su=full_name_su,
        psw=psw,
        status=status,
        statusID=statusID,
        limitcon=limitcon,
        ageGroup=ageGroup,
        pswcl=pswcl,
        logincl=logincl,
        idcomp=idcomp,
        def_val='-'
        )

    dc_procConv = dict(
        pol='conv_pol',
        sendMes='conv_send_mes',
        status='conv_status_into_str',
        status_id='conv_status_into_str'
        )


class Com_proc_advuser:
#    from advuser.serv_sprstatus import Com_proc_sprstatus
    from .models import AdvUser 

    _s_err = 'SyntaxError##advuser.serv_advuser.Com_proc_advuser'
    _s_err_user_notData = 'Пользователь User не определен'


    @classmethod
    def _write_except_into_log(cls, arg_except):        
        s_mes = '{0} {1}'.format(cls._s_err, arg_except)
        TypeError_system(ErrorRun_impl(s_mes))  # запись в файл app/loggin/*.log

    #процедура вызова ErrorRun_impl
    @classmethod
    def _run_raise(cls, s_arg, showMes=None, s_err=None):       
        """s_arg строка сообщения исключения из кода
        s_err базовая строка к которой добавляется дополнительные данные
            s_err строка для перекрытия шаблона cls._s_err
        """

        s_err = s_err or cls._s_err

        if showMes:            
            raise ErrorRun_impl('verify##{0}'.format(s_arg))
        else:
            s_mes = '{0} {1}'.format(s_err, s_arg)
            TypeError_system(ErrorRun_impl(s_mes))  # запись в файл app/loggin/*.log
            raise ErrorRun_impl(s_mes)

    #**************** сервис обработки данных ***********************
    # testing 20.05.2020 in consol django
    # Получение path для фотографий пользователей 
    @classmethod
    def get_path_photo(cls, user):
        from app import verify_exists_file_photo
    
        user = getUser(user)
        if not user:
            return None        
       
        s_photo = user.username + '.png'
        s_path = verify_exists_file_photo(s_photo)
    
        return s_path


    # Консультант пользователя
    # return parentuser or None
    """
    testing 20.05.2020 
    modul: tests.advuser.test_servadvuser
    procedure: test_get_user_cons
    file: tests/advuser/serv_advuser/test_serv_advuser.json
    """
    @classmethod
    def get_user_cons(cls, user):        
        """ Получить User as Consultant  or None """
        try:            

            user = getUser(user)
            if user is None:
                cls._run_raise('get_user_cons: пользователь не определен')
        
            if user.is_superuser:
                return cls.get_user_head()            


            res_advUser = servAdvUser_get_advUser(user)
            if not res_advUser:
                cls._run_raise('get_user_cons: нет данных по модели AdvUser user:'+ str(user))
                
            advuser = res_advUser.res_model
            parentuser = getUser(advuser.parentuser)
                
            if parentuser is None: 
                cls._run_raise('get_user_cons: parentuser:{0} не найден как User'.format(advuser.parentuser))
            
            return parentuser

        except Exception as ex:
            return None


    @classmethod
    def get_js_struct(cls, arg_user)->dict:
        """ Выборка поля advUser.js_struct
        используется при изменении статуса
        return dict or None
        """
        from .models import AdvUser

        user = getUser(arg_user)
        advuser = AdvUser.objects.get(pk=user)
        res_dc = json.loads(advuser.js_struct)

        return res_dc


    @classmethod
    def get_head70_user(cls, arg_user)->User:
        """ Получить пользователя на уровне руководителя группы 
        with levelperm=70
        return User or None
        """

        from .serv_typestatus import type_status_user
        from .models import AdvUser

        try:

            user = getUser(arg_user);

            row = AdvUser.objects.get(pk=user)
            parentuser = row.parentuser

            parentuser = getUser(parentuser)
            row_master = AdvUser.objects.get(pk=parentuser)
            levelperm = row_master.status.levelperm
            while levelperm < 70 :
                parentuser = row_master.parentuser
                parentuser = getUser(parentuser)
                row_master = AdvUser.objects.get(pk=parentuser)

                levelperm = row_master.status.levelperm
                        

            return parentuser

        except:
            return None


    # Руководитель группы гостВхода, клиента, менеджера
    # Используется для пользователй с уровнемДоступа менее 40 
    # return res_proc.res_model руководитель группы 
    """
    testing 20.05.2020
    modul prtests.tests.advuser.test_serv_advuser
    procedure: test_get_head_user
    file: tests/advuser/serv_advuser/test_serv_advuser.json
    """
    @classmethod
    def get_head_user(cls, user)->Res_proc:  
        """ Get head user or None """
        from .serv_typestatus import type_status_user

        res_proc = Res_proc()
        userHead = None

        try:
            user = getUser(user)
            if user is None:
                cls._run_raise('get_head_user: нет данных для арг. user')                

            if user.is_superuser:
                userHead = cls.get_user_head()
                res_proc.res_model = userHead
                return res_proc

            obj_typeStatus = type_status_user(user)
            if not obj_typeStatus:
                cls._run_raise('get_head_user: ошибка вызваемой процедуры type_status_user(user)')
                
            levelperm = obj_typeStatus.levelperm
            if levelperm in (40, 70, 100):
                userHead = user

            else:                    

                level = levelperm
                user_next = cls.get_user_cons(user)

                # Подъем на следующий уровень, пока не будет достигнут level >= 40
                while level < 40:
                    obj_typeStatus = type_status_user(user_next)
                    if not obj_typeStatus:
                        cls._run_raise('get_head_user: ошибка вызваемой процедуры type_status_user(user)')
                                              
                    level = obj_typeStatus.levelperm
                    if level>39: 
                        break

                    user_next = cls.get_user_cons(user_next)
                    
                userHead = user_next

            if userHead:
                res_proc.res_model = userHead
                res_proc.res = True                        

        except Exception as  ex:
            res_proc.error = ex

        return res_proc


    #  Пользователь как руководитель проекта
    #  return User or raise 
    """
    testing 20.05.2020
    modul prtests.tests.advuser.test_serv_advuser
    procedure: test_get_user_head
    file: tests/advuser/serv_advuser/test_serv_advuser.json

    """
    @classmethod
    def get_user_head(cls)->User:        
        """ return User руководитель проекта """
        rowHead = cls.AdvUser.objects.filter(status__levelperm=100)
        if rowHead.exists():
            rowHead = rowHead.first()

        else:
            cls._run_raise('get_user_head: нет данных для рукПроекта')            

        user_head = rowHead.user

        return user_head


    # return advuser or None
    """
    testing 20.05.2020
    modul prtests.tests.advuser.test_serv_advuser
    procedure: test_get_advUser_header
    file: tests/advuser/serv_advuser/test_serv_advuser.json

    """
    @classmethod
    def get_advUser_header(cls):
        res = None

        try:            
            user_head = cls.get_user_head()
            res_advuser = servAdvUser_get_advUser(user_head)
            if not res_advuser:
                cls._run_raise('get_advUser_header Нет данных для модели AdvUser')

            res = res_advuser.res_model

        except :
            return None        

        return res


    #return dict or {}
    # Данные руководителя проекта
    """
    testing 21.05.2020
    modul prtests.tests.advuser.test_serv_advuser
    procedure: test_get_dataHeader
    file: tests/advuser/serv_advuser/test_serv_advuser.json
    """
    @classmethod
    def get_dataHeader(cls, modf_form=False):

        user_header = cls.get_user_head()

        out_dict = dict()
        if cls.get_advData_user(user_header, out_dict, modf_form):
            return out_dict
        
        return {}


    # return dict or None
    # возвращает объект dict AdvUser.advData   
    """
        testing 20.05.2020
        modul prtests.tests.advuser.test_serv_advuser
        procedure: test_get_advData
        file: tests/advuser/serv_advuser/test_serv_advuser.json

    """
    @classmethod
    def get_advData(cls, user, modf_form=False):
        """ return dict_advdata_or_None 
        modf_form=True -> модифицирует данные для отображения в браузере
        """

        user = getUser(user)
        if user is None:
            cls._run_raise('get_advData: user не определен')
            
        if user.is_superuser:
            return dict(username=user.username, full_name='СуперПользователь')

        res_advUser = servAdvUser_get_advUser(user)
        if res_advUser is None:
            return None

        advuser = res_advUser.res_model
        advData = advuser.advData
        if advData:
            advData = json.loads(advData)

            if modf_form:  # Конвертирование по шаблону из Struct_default_AdvUser
                modf_dict_by_setting_def(advData)

            return advData

        else: return None


    # return dict or None
    """
    testing 20.05.2020
    modul prtests.tests.advuser.test_serv_advuser
    procedure: test_get_dataUser
    file: tests/advuser/serv_advuser/test_serv_advuser.json

    """
    @classmethod
    def get_dataUser(cls, user)->dict: 

        user = getUser(user)
        if user is None:
            return None

        advData = cls.get_advData(user, modf_form=True)  # объект dict

        return advData


    # return True and out_dict=advData    or False and out_dict={}
    """
    testing 21.05.2020
    modul prtests.tests.advuser.test_serv_advuser
    procedure: test_get_dataUser
    file: tests/advuser/serv_advuser/test_serv_advuser.json
    """
    @classmethod
    def get_advData_user(cls, user, out_dict:dict, modf_form=False)->bool: 
        """ return True|False dict->out_dict """

        if isinstance(out_dict, dict): out_dict.clear()

        res = False
        try:

            advData = cls.get_advData(user, modf_form)  # объект dict
            if advData:
                out_dict.update(advData)
                res = True
            else:
                cls._write_except_into_log('get_advData_user: нет данных advData')

        except Exception as ex: 
            cls._write_except_into_log(str(ex))
            return False

        return res 


    # return res_proc.res = True если arg_head является рукГруппы arg_user
    # Анализ, что arg_head является рукГруппы или рукПроекта
    # используется для определения правРедактирования профиля
    """
        testing 21.05.2020
        modul prtests.tests.advuser.test_serv_advuser
        procedure: test_verify_yourHead
        file: tests/advuser/serv_advuser/test_serv_advuser.json
    """
    @classmethod
    def verify_yourHead(cls, arg_user, arg_head)->Res_proc:
        """ Анализ, что arg_head является рукГруппы или рукПроекта """
        s_err = 'verify_yourHead'
        res_proc = Res_proc()

        try:
            user = getUser(arg_user)
            user_head = getUser(arg_head)

            if user is None or user_head is None:
                cls._run_raise(f'{s_err}: arg_user or arg_head не определен')

            head_typeStatus = type_status_user(user_head)
            if not  head_typeStatus:
                cls._run_raise(f'{s_err}: статус рукГруппы не определен')

            if head_typeStatus.levelperm < 40:
                res_proc.mes = 'Статус пользователя не соответсвует рукГруппы'
                res_proc.error = 'verify##Статус пользователя не соответсвует рукГруппы'
                return res_proc

            # ------------- конец блока верификации --------------


            res_parentuser = cls.get_parentuser(user)
            if not res_parentuser:
                cls._run_raise('')

            parentuser = res_parentuser.any_str
            if user_head.username == parentuser:
                res_proc = True
            else:
                s_error = f'{user_head.get_full_name()} Не является рукГруппы для {user.username}'
                res_proc.error = ErrorRun_impl(f'verify##{s_error}')
                res_proc.mes = s_error

        except Exception  as ex:
            res_proc.error = ex

        return res_proc 


    # выборка данных для личного консультанта
    # return dict or None
    """
        testing 21.05.2020
        modul prtests.tests.advuser.test_serv_advuser
        procedure: test_get_dataCons
        file: tests/advuser/serv_advuser/test_serv_advuser.json
    """
    @classmethod
    def get_dataCons(cls, user, modf_form:bool=False)->dict:

        s_err = 'get_dataCons'

        res = None

        user = getUser(user)
        if user is None:
            cls._write_except_into_log(f'{s_err} arg user не определен')
            return None
        
        try:

            if user.is_superuser:
                parentuser = cls.get_user_head()                
                parent_user_login = parentuser.username

            else:
                res_parentuser = cls.get_parentuser(user)
                if not res_parentuser:
                    cls._run_raise(f'{s_err} parentuser не определен')

                parent_user_login = res_parentuser.username

            out_dict = dict()
            if cls.get_advData_user(parent_user_login, out_dict, modf_form ):
                res = out_dict

        except :
            return res

        return res

    
    """
    Тестирование 1.06.2020
    modul: tests.advuser.test_serv_advuser
    procedure: test_get_profil_user_for_teg
    file:  tests/advuser/serv_advuser/test_serv_advuser_next.json
    """
    @classmethod
    def get_profil_user_for_teg(cls, user):
        from app.com_data.any_mixin import get_valFromDict

        
        user = getUser(user)
        if user is None: 
            raise ValueError('get_profil_user_for_teg нет данных для user')

        prof_proc = cls.get_profil_user(user)

        try:
            advuser = user.advuser
        except:
            advuser = None

        if not prof_proc:  # если профиля нет по любой причине 
            res = dict(
                    full_name = user.get_full_name(),
                    email = user.email
                )
            if advuser:
                status = advuser.status
                res.update(status = '{0} {1}'.format(status.pk, status.strIdent))
            else:
                res.update(status='Нет данных')

            return res

        # ------- продолжение в штатном режиме ------------

        try:
            advData = json.loads(user.advuser.advData)
        except:
            advData = None

        param =  get_valFromDict(prof_proc.res_dict,'param')
        type_status = prof_proc.res_obj;

        if  not (param or statusID):
            raise ValueError('get_profil_user_for_teg: Нет профиля или statusID')

        param.update(dict(
                status='{0} {1}'.format( type_status.statusID, type_status.strIdent), 
                email = user.email
                ))
        if not advData:
            idcomp = get_valFromDict(advData,'idcomp')
            param.update(dict(idcomp=idcomp))

        del param['imgphoto']

        return param


    """
    Тестирование 1.06.2020
    modul: tests.advuser.test_serv_advuser
    procedure: test_get_profil_user
    file:  tests/advuser/serv_advuser/test_serv_advuser_next.json
    """
    @classmethod
    def get_profil_user(cls, user):
        """ Создание dict профиля """

        from app import Ext_dict
        from .serv_sprstatus import Com_proc_sprstatus

        structDef = Struct_default_AdvUser

        res_proc = Res_proc()
        
        s_err = 'get_profil_user'

        try:
            user = getUser(user)
            if user is None:
                raise ErrorRun_impl('{0} нет данных для аргумента user'.format(s_err))
                        
            res_proc.any_str = user.username
            type_status = type_status_user(user)
            res_proc.res_obj = type_status


            """
            imgphoto    = self.imgphoto,
                full_name   = self.full_name,
                status      = self.status,
                idcomp      = self.idcomp
            """
            if user.is_superuser:
                param = dict(
                        imgphoto  = cls.get_path_photo(user),
                        full_name = 'Супер-пользоатель',
                        status = Com_proc_sprstatus.get_status_suadm().strIdent,
                        idcomp = structDef.idcomp
                        )

                _dict =  dict(
                    btn_upd=False,
                    param     = param,
                    prof      = []
                    )
                res_proc.res_dict = _dict
                res_proc.res = True

                return res_proc
            

            # возврат нулевого статуса
            if not type_status:
                param = dict(
                    imgphoto  = servAdvUser_get_advUser.get_path_photo('suadm'),
                    full_name = 'Пользователь не определен',
                    status = cls.Com_proc_sprstatus.get_status_notstatus().strIdent,
                    idcomp = structDef.idcomp
                    )

                _dict =  dict(
                    btn_upd=False,
                    param     = param,
                    prof      = []
                    )

                res_proc.res_obj.levelperm = 20  # чтобы отображение стало как у клиента
                res_proc.res_dict = _dict
                res_proc.res = True

                return res_proc


            # ------------- обработка данных профиля -----------------
            status_strIdent = type_status.strIdent # structDef.conv_status_into_str(type_status.statusID)
            dict_head = cls.get_dataHeader()
            dict_cons = cls.get_dataCons(user)
            dict_user = cls.get_advData(user)
            dict_user['sendMes'] = structDef.conv_send_mes(dict_user.get('sendMes'))

            if dict_cons is None:
                dict_cont = dict_head

            Ext_dict.CL_modify_empty(dict_head)
            Ext_dict.CL_modify_empty(dict_cons)
            Ext_dict.CL_modify_empty(dict_user)

            param = dict(
                imgphoto    = cls.get_path_photo(user),
                full_name   = dict_user.get('full_name'),
                status      = status_strIdent,
                idcomp      = dict_user.get('idcomp') or structDef.idcomp
                )

            arrayProf = [ dict(val=user.username, str='Логин:') ]
            if type_status.levelperm < 30:
                arrayProf += [ dict(val=dict_user.get('pswcl'), str='Пароль:')]

            # Обработка гостВхода 
            if type_status.levelperm < 20:  # гостевой вход или клиент сайта

                arrayProf +=  [ 
                    dict(val=dict_cons.get('full_name') or structDef.full_name, str='Личн. консультант:', idrow='parentData'),                    
                    dict(val=dict_cons.get('phone')  or structDef.phone,     str='Тел. личн. консультанта:')]

                arrayProf += [ 
                    dict(val=dict_head.get('full_name') or structDef.full_name ,  str='Админ. проекта:', idrow='parentData'),
                    dict(val=dict_head.get('phone')     or structDef.phone,       str='Телефон адмПроекта:')]

            else:  # структура профиля для менеджеров и рукГрупп

                arrayProf +=[                    
                    dict(val= dict_user.get('phone') or structDef.phone , str='Телефон:'),
                    dict(val= dict_user.get('email') or structDef.email,       str='email:'),
                    dict(val= dict_user.get('sendMes'),   str='Получать сообщ.:'),
                    dict(val= dict_user.get('ageGroup') or structDef.ageGroup , str='ВозрГруппа:'),
                    dict(val= structDef.conv_pol(dict_user.get('pol')) , str='Пол:'),
                    ]

                if type_status.levelperm > 20:
                    arrayProf += [
                        dict(val= dict_user.get('pswcl') or structDef.pswcl , str='Пароль клиента:', idrow='parentData'),
                        dict(val= dict_user.get('logincl') or structDef.logincl , str='Логин клиента:')
                        ]                               

                if type_status.levelperm < 100:
                    arrayProf += [
                        dict(val=dict_cons.get('full_name') or structDef.full_name, str='Консультант:', idrow='parentData'),
                        dict(val=dict_cons.get('phone')  or structDef.phone,     str='Тел. консультанта:'),
                        dict(val=dict_cons.get('email')  or structDef.email,     str='email консультанта:')                        
                        ]

                if type_status.levelperm in (40, 70):
                    arrayProf += [
                        dict(val=dict_user.get('limitcon') or structDef.limitcon , str='Лимит подкл.:')]
                


            res_proc.res_dict = dict(  
                            btn_upd=True,                            
                            param    = param,
                            prof     = arrayProf 
                            )

            res_proc.res = True
            return res_proc

        except Exception as ex:
            res_proc.error = ex

        return res_proc
   
    # ************** конец процедуры get_profil_user ***********************


    # Выборка значений из advData
    # return val or None
    """
        testing 21.05.2020
        modul prtests.tests.advuser.test_serv_advuser
        procedure: test_get_val_from_advData
        file: tests/advuser/serv_advuser/test_serv_advuser.json
    """
    @classmethod
    def get_val_from_advData(cls, arg_user, arg_par:str):
        """ Значение из advData
        аргументы: arg_user, arg_par
        return val or None
        """
        try:
            advData = cls.get_advData(arg_user)  # dict or None
            if advData is None: return None
                        
            val = advData.get(arg_par)

            return val

        except Exception as ex:
            return None


    # Список пользователей рукГруппы
    # return  res_proc.res_list = list(username)
    """
        testing 21.05.2020
        modul prtests.tests.advuser.test_serv_advuser
        procedure: test_get_subRows_head
        file: tests/advuser/serv_advuser/test_serv_advuser.json
    """
    @classmethod
    def get_subRows_head(cls, arg_head):
        
        res_proc = Res_proc()

        try:
            user_head = getUser(arg_head)
            if user_head is None:
                cls._run_raise('get_subRows_head arg_head нет данных')

            _username_head = user_head.username

            type_status = type_status_user(user_head)
            if type_status:
                if type_status.levelperm < 40:
                    raise ErrorRun_impl('verify##Нет прав на доступ к ресурсам группы')

            else:
                cls._run_raise('Статус пользователя не определен')

            res_lst = list( ( row.user.username 
                for row in cls.AdvUser.objects.filter(parentuser=_username_head, 
                            status__levelperm__in=(30,40,70)) ))
            if res_lst:
                res_lst.append(_username_head) # включить самого рукГруппы
            else:
                raise ErrorRun_impl('verify##Нет данных по составу группы')

            res_proc.res_list = res_lst
            res_proc.res = True

        except Exception as ex:
            res_proc.error = ex

        return res_proc


    # возвращает строку res_proc.any_str=parentuser
    # parentuser 
    """
        testing 21.05.2020
        modul prtests.tests.advuser.test_serv_advuser
        procedure: test_get_parentuser
        file: tests/advuser/serv_advuser/test_serv_advuser.json
    """
    @classmethod
    def get_parentuser(cls, arg_user)->str:
        """ return User for parentuser or None """

        from .models import AdvUser

        res_proc = Res_proc()

        try:
            user = getUser(arg_user)
            if user is None:
                cls._run_raise(f'get_parentuser: arg_user не определен')

            if user.is_superuser:
                parentuser = cls.get_user_head()
                res_proc.any_str = parentuser.username
                return res_proc

            row = AdvUser.objects.get(pk=user) 

            parentuser = row.parentuser
            parentuser = getUser(parentuser) 

        except Exception as ex:
            return None

        return parentuser


