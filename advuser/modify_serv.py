"""
advuser

modify_serv

Процессы обновления моделей 
"""

import json
from django.db import transaction

from app.models import log_modf_models, spr_pswcl
from .models import AdvUser,  SprStatus
from app import getUser, Res_proc, ErrorRun_impl, TypeError_system
from app.com_data.any_mixin import getEMTPY_id
from .serv_typestatus import type_status_user


# процедура для обновления advData по значениям из arg_dict
def FM_init_advData(arg_advUser, arg_dict):
        advData_user = json.loads(arg_advUser.advData)
        advData_user.update(arg_dict)
        s_advData = json.dumps(advData_user, ensure_ascii=False)

        arg_advUser.advData = s_advData


"""
Процедура прошла тестирование anymixins.any_mixin.test_any_data4 04.05.2020

Сброс статуса на уровень 30
-------------------------------------------------------------
    переподчинение: parentuser, advData[parentuser] 
    всех подчиненных клиентов по полю parentuser and advData 
------------------------------------------------------------

    return res_proc.lst  - список обновлений подчиненной структуры arg_user
"""
def resubm_parentuser(arg_user):
    def run_raise(s_arg):
        s_err = 'ResError##advuser.modify_serv.resubm_parentuser'
        raise ErrorRun_impl('{0} {1}'.format(s_err, s_arg))
    # -----------------------------------------------------------

    res_proc = Res_proc()
    lst = []

    try:
        user = getUser(arg_user)
        if user is None:
            run_raise('arg_user не определен')            

        user_typeStatus = type_status_user(user)

        if not user_typeStatus:
            run_raise('нет данных для статуса')

        #if user_typeStatus.levelperm < 40:
        #    run_raise('нет прав на переопределение parentuser')

        res_parentuser = AdvUser.get_parentuser(user)
        if not res_parentuser:
            run_raise('нет данных для руководителя группы')

        _parentuser = res_parentuser.any_str
        
        level_user = user_typeStatus.levelperm
        rows = AdvUser.objects.filter(parentuser=user, status__levelperm__gte=10, status__levelperm__lt=level_user)
        if rows.exists():
            for row in rows:
                row.parentuser = _parentuser

                advData = json.loads(row.advData)
                advData['parentuser'] = _parentuser
                row.advData = json.dumps(advData, ensure_ascii=False)

                row.save()
                lst.append('{0} обновл. pswcl; '.format(row.user.username))

        res_proc.res = True
        res_proc.res_list = lst

    except Exception as ex:
        res_proc.error = ex


    return res_proc


"""
    Пароль гостВхода
    ------------------------------------
    Определяется по pswcl рукГруппы

    return res_proc.any_str
"""
def get_pswcl_fromHead(arg_user):
    res_proc = Res_proc()
    s_notData = 'NotData##advuser.modify_serv.get_pswcl_fromHead:'

    try:
        user = getUser(arg_user)
        if user is None:
            raise ErrorRun_impl('{0} arg_user нет в БД'.format(s_notData))

        type_status = type_status_user(user)
        if not type_status:
            raise ErrorRun_impl('{0} {1} нет статуса'.format(s_notData, user.username))

        user_head = None
        if type_status.levelperm >39 :
            user_head = user
        else:
            res_head = AdvUser.get_head_user(user)
            user_head = res_head.res_model

        if user_head is None:
            raise ErrorRun_impl('{0} {1} нет данных для рукГруппы '.format(s_notData, user.username) )

        advData = AdvUser.get_advData(user_head)

        pswcl = advData.get('pswcl')
        if pswcl is None:
            raise ErrorRun_impl('{0} {1} advData нет pswcl'.format(s_notData, user.username))

        res_proc.any_str = pswcl

    except Exception as ex:
        res_proc.error = ex

    return res_proc


"""
Проверено на ВСЕх рукГрупп 03.05.2020
------------------------------
Обновление пароля гостВхода
Обновение parentuser
"""
class Upd_pswcl_in_dependData:
    
    # обновление подчиненной структуры
    # при изменении пароля гостевого входа
    def upd_pswcl(arg_head):
        
        # встроенная процедура обновления advData 
        def upd_advData(row, pswcl):
            advData = json.loads(row.advData)
            advData['pswcl'] = pswcl
            row.advData = json.dumps(advData, ensure_ascii=False)
        # --------------------------------------------------------

        res_proc = Res_proc()
        res_lst = []
        res_proc.res_list = res_lst

        s_resError = 'ResError##advuser.modify_serv.Upd_pswcl_in_dependData.upd_pswcl:'
        s_notData = 'NotData##advuser.modify_serv.Upd_pswcl_in_dependData.upd_pswcl:'

        try:

            # --------------- верификация и инициализация ---------------
            # --------- поля log_modf_models: id_log, row_parent, id_parent, id_end, inf_modf, arg_modf

            # для удобства отображения кода 
            if 1<2:

                # базовые параметры обновленя 
                empty_key  = getEMTPY_id(15)    # empty идентификатор  for: id_log and row_parent
                word_pswcl = None                  # новый пароль гостВхода

                user_head = getUser(arg_head)
                if user_head is None:
                    res_lst.append('нет данных по аргументу user_head')
                    raise ErrorRun_impl('{0} нет данных по аргументу user_head'.format(s_notData) )

                type_status = type_status_user(user_head)
                if not type_status:
                    raise ErrorRun_impl('{0} {1} нет статуса'.format(s_notData, user_head.username))

                if type_status.levelperm < 40 or type_status.levelperm > 100 :
                    res_lst.append('Нет прав на обработку')
                    raise ErrorRun_impl('{0} нет прав на обработку'.format(s_resError))

                res_pswcl = spr_pswcl.get_rand_pswcl()  
                if res_pswcl:
                    word_pswcl = res_pswcl.res_obj[0]
                else:
                    raise ErrorRun_impl('{0} ошибка вызываемой процедуры'.format(s_resError) )

            # ********************* конец блока верификации и инициализации *****************


            _row_parent    = '{0}##{1}'.format(empty_key, user_head.username)

            # вставить базовую запись рукГруппы
            if not log_modf_models.objects.filter(row_parent=_row_parent).exists():
                log_modf_models.objects.create(
                    id_log = _row_parent,
                    row_parent = _row_parent,
                    arg_modf  = word_pswcl,
                    id_parent = True,
                    inf_modf  = 'пароль гостВхода рукГруппы:'+ user_head.username
                    )

                # Создание дочерних записей - пользователей рукГруппы
                for row in AdvUser.objects.filter(parentuser=user_head, 
                                  status__levelperm__gte=10, status__levelperm__lt=40).exclude(status__levelperm=20):

                    _username = row.user.username
                    id_log = '{0}##{1}'.format(_row_parent, _username)

                    if not log_modf_models.objects.filter(id_log=id_log).exists():
                        log_modf_models.objects.create(
                            id_log = id_log,
                            row_parent = _row_parent,
                            arg_modf  = word_pswcl,
                            inf_modf  = 'пароль гостВхода user:'+ _username
                            )
            
                # обновление паролей гостВхода
                with transaction.atomic():
                    for row_log in log_modf_models.objects.filter(row_parent=_row_parent).exclude(id_end=True):

                        if row_log.id_parent:
                            _login = row_log.id_log.split('##')[1]
                        else:
                            _login = row_log.id_log.split('##')[2]

                        pswcl = row_log.arg_modf
                        row_cl_advuser = AdvUser.objects.filter(parentuser=_login, status__levelperm=10)
                        if row_cl_advuser.exists():
                            row_cl_advuser = row_cl_advuser.first()

                            head_advuser = AdvUser.get_advUser(_login)

                            upd_advData(row_cl_advuser, pswcl) # обновление advData клиента                     
                            upd_advData(head_advuser, pswcl)         # обновление advData наставника

                            user_cl = getUser(row_cl_advuser.user)

                            user_cl.set_password(pswcl)
                            user_cl.save()          # сохранение пароля
                            head_advuser.save()     # сохранение head_advuser.advData

                            row_cl_advuser.save()   # сохранение row_cl_advuser.advData
                            
                        res_lst.append('{0} pswcl:{1} обновлено; '.format(_login, pswcl))                    

                res_proc.res = True

        except Exception as ex:
            res_lst.append('Сервер остановил обработку')
            res_proc.error = ex

        return res_proc


"""
Процедура прошла тестирование на восстановление паролей 03.05.2020
Восстановление паролей из файла 
advuser/arg_restor_psw.json
-------------------------------
обновление паролей по ВСЕму списку из файла
"""
def restor_psw():
    from app import loadJSON_withTempl
    from app import Type_value
    from django.contrib.auth.models import User

    res_proc = Res_proc()
    _lst = []
    s_err = 'ResError##advuser.modify_serv.restor_psw'

    try:

        path = Type_value.init_formatTempl('advuser/arg_restor_psw','jsn')
        dict_psw = loadJSON_withTempl(path)

        for item in dict_psw:
            username = item[0]
            psw = item[1]

            user = getUser(username)            
            if user:
                user.set_password(psw)
                _lst.append('{0} обновлено; '.format(username))

            else:
                _lst.append('{0} не найден в User; '.format(username))


        res_proc.res_list = _lst

    except Exception as ex:
        res_proc.error = ex

    return res_proc

# Обновление pswcl гостВхода
def upd_pswcl_quest(arg_user, arg_pswcl=None):
    res_proc = Res_proc()

    def run_raise(s_arg, showMes=None):
        s_err = 'advuser.modify_serv.upd_pswcl_quest'

        if showMes:            
            raise ErrorRun_impl('verify##{0}'.format(s_arg))
        else:
            raise ErrorRun_impl('{0} {1}'.format(s_err, s_arg))

    try:
        user = getUser(arg_user)
        if user is None:
            run_raise('arg_user не найден в User')

        if arg_pswcl is None:
            res_pswcl = get_pswcl_fromHead(user)
            if not res_pswcl:
                run_raise('пароль гостВхода не определен из get_pswcl_fromHead')
            arg_pswcl = res_pswcl.any_str

        # ---------------- конец блока предОбработки входящих параметров ---------


        advuser = AdvUser.get_advUser(user)
        if not advuser:
            run_raise('нет данных для advuser ' + user.username )
        
        FM_init_advData(advuser, dict(pswcl=arg_pswcl) )

        advuser.save()
        res_proc.any_str = arg_pswcl
        res_proc.res = True

    except Exception as ex:
        res_proc.error = ex

    return res_proc



"""
Процедура восстановления данных гостВхода
обновление advData

если logincl is None or empty

"""
def restor_data_quest(arg_user):
    from .models import AdvUser
    from .forms import Base_profForm as profForm

    res_proc = Res_proc()

    def run_raise(s_arg, showMes=None):
        s_err = 'advuser.modify_serv.restor_data_quest'

        if showMes:            
            raise ErrorRun_impl('verify##{0}'.format(s_arg))
        else:
            raise ErrorRun_impl('{0} {1}'.format(s_err, s_arg))

    # ------------------------------------------------------------

    try:
        logincl = None
        pswcl   = None

        _user = getUser(arg_user)
        if _user is None:
           run_raise('arg_user не определен как User')

        # Поиск последней записи гостВхода
        advUser_cl = AdvUser.objects.filter(parentuser=_user.username, status__levelperm=10)
        if advUser_cl.exists():

            # запись гостВхода найдена -> выборка значений logincl and pswcl
            advUser_cl = advUser_cl.last()
            advData_cl = json.loads(advUser_cl.advData)

            logincl = advUser_cl.user.username
            pswcl   = advData_cl.get('pswcl')
            
            if pswcl is None:

                # Обновление pswcl гостВхода 
                res_upd_pswcl = upd_pswcl_quest(logincl)
                if not res_upd_pswcl:
                    run_raise('ошибка обновления pswcl из upd_pswcl_quest')
                                    
                pswcl = res_upd_pswcl.any_str

            _dict = dict(
                        logincl = logincl,
                        pswcl   = pswcl
                )

            # Обновление advData
            advUser_user = AdvUser.get_advUser(_user)
            if not advUser_user:                
                run_raise('нет данных для advuser ' + _user.username)

            FM_init_advData(advUser_user, _dict)
            advUser_user.save()                

            res_proc.res_dict = _dict
            res_proc.res = True

        else:  # продолжение, если запись гостВхода не найдена

            res_templ = profForm.create_templDict_qust(_user)
            if not res_templ:
                run_raise('шаблон templDict_quest не создан')

            dict_templ = res_templ.res_dict
            _dict = dict(
                        logincl = dict_templ['username'],
                        pswcl   = dict_templ['pswcl']
                )

            advUser_user = AdvUser.get_advUser(_user)
            if not advUser_user:
                run_raise('Нет данных advuser для ' + _user.username )

            # Обновление advData
            FM_init_advData(advUser_user, _dict)

            with transaction.atomic():
                advUser_user.save()
                res_addProf = profForm.addProfilUser(dict_templ)
                if not res_addProf:
                    run_raise('сбой сохранения пакета advUser_user and addProfUser')

            res_proc.res_dict = _dict
            res_proc.res = True

    except Exception as ex:
        res_proc.error = ex

    return res_proc


"""
Верификация и обновление данных по паролю гостВхода
"""
class Ver_upd_quest:
    from .forms import Base_profForm as profForm
    
    generate_pswcl = profForm.generate_pswcl

    s_err = 'advuser.modify_serv.Ver_upd_modl'
    s_err_serv = 'Сервер остановил обработку процедуры'
        

    def _init_err(self, arg_err, arg_mes):
        TypeError_system(arg_err) # запись в file log
        self.error = arg_mes
        

    def __init__(self, arg_user):

        self.user_quest = None
        self.pswcl = None
        self.error = None

        self.user_quest = getUser(arg_user)
        if self.user_quest is None:
            raise ErrorRun_impl('{0} arg_user не инициализированы'.format(self.s_err))

        self._initData_quest()        


    def _initData_quest(self):

        try:
            row_cl = AdvUser.objects.filter(user=self.user_quest)

            if row_cl.exists():
                row_cl = row_cl.first()

                advuser = row_cl.user.advuser
                advData = json.loads(advuser.advData)
                _pswcl   = Res_proc.FN_get_val_dict(advData,'pswcl')

                if _pswcl is None:
                    _pswcl = generate_pswcl()
                    if _pswcl :
                        self._upd_quest(row_cl, dict(pswcl=_pswcl) )                    
                    else:
                        raise ErrorRun_impl('{0} pswcl не определен из advuser.forms.Base_profilForm.generate_pswcl'.format(self.s_err))
                else:
                    self.pswcl = _pswcl               
                
            else:
                self._add_quest(self.user_quest)
           
        except Exception as ex:
            self._init_err(ex, self.s_err_serv)


    def _upd_quest(self, row_cl, arg_dict, updUser=None):

        try:            
            
            FM_init_advData(row_cl, arg_dict)

            row_cl.save()

            advData = AdvUser.get_advData(row_cl.user)
            if advData is None:
                raise ErrorRun_impl('{0}._upd_quest advData не определено'.format(self.s_err))

            if updUser:
                self.logincl_user = Res_proc.FN_get_val_dict(advData, 'logincl')
                self.pswcl_user   = Res_proc.FN_get_val_dict(advData, 'pswcl')

            else:
                self.logincl = Res_proc.FN_get_val_dict(advData, 'username')
                self.pswcl   = Res_proc.FN_get_val_dict(advData, 'pswcl')

        except Exception as ex:            
            self._init_err(ex, self.s_err_serv)
        

    def _add_quest(self, arg_user):

        try:
            res_templ = self.profForm.create_templDict_qust(arg_user)
            if not res_templ:
                raise ErrorRun_impl('{0} процедура create_templDict_qust вернула None '.format(self.s_err))

            dict_templ = res_templ.res_dict

            res_add = self.profForm.addProfilUser(dict_templ)
            if not res_add:
                raise ErrorRun_impl('{0} Ошибка создания объекта user_cl'.format(self.s_err))

            advData = AdvUser.get_advData(dict_templ['username'])
            if not advData:
                raise ErrorRun_impl('{0} нет данных advData '.format(self.s_err))

            self.logincl = advData['username']
            self.pswcl   = advData['pswcl']

        except Exception as ex:
            self._init_err(ex, self.s_err_serv)


# ***************

"""
Верификация и обновление пароля и логина гостВхода для менеджеров и рукПроекта
"""
class Ver_upd_modl:
    from .forms import Base_profForm as profForm

    s_err = 'advuser.modify_serv.Ver_upd_modl'
    s_err_serv = 'Сервер остановил обработку процедуры'
        

    def _init_err(self, arg_err, arg_mes):
        TypeError_system(arg_err) # запись в file log
        self.error = arg_mes
        

    def __init__(self, arg_user):

        self.user = None
        self.logincl_user = None
        self.pswcl_user = None

        self.logincl = None
        self.pswcl = None
        self.error = None

        self.user = getUser(arg_user)
        if self.user is None:
            raise ErrorRun_impl('{0} arg_user не инициализированы'.format(self.s_err))

        self._ver_exists_quest()
        if self.error is None:
            self._verify_user()

    def _verify_user(self):        

        try:

            type_statusUser = type_status_user(self.user)
            if not type_statusUser:
                raise ErrorRun_impl('{0} Нет данных Type_status_user'.format(self.s_err))

            if type_statusUser.levelperm > 39: return

            advData = AdvUser.get_advData(self.user)
            if advData is None:
                raise ErrorRun_impl('{0} нет данных advData for self.user'.format(self.s_err))

            logincl = Res_proc.FN_get_val_dict(advData, 'logincl')
            pswcl   = Res_proc.FN_get_val_dict(advData, 'pswcl')

            # Обновление по значениям, полученным из гостВхода
            if logincl != self.logincl or pswcl != self.pswcl:
                _dict = dict(logincl=self.logincl, pswcl=self.pswcl)

                self._upd_quest(self.user.advuser, _dict, True )

        except Exception as ex:
            self._init_err(ex, self.s_err_serv)


    def _ver_exists_quest(self):

        try:
            row_cl = AdvUser.objects.filter(parentuser=self.user.username, status__levelperm=10)

            if row_cl.exists():
                row_cl = row_cl.last()

                self.logincl = row_cl.user.username

                advuser = row_cl.user.advuser
                advData = json.loads(advuser.advData)
                _pswcl   = Res_proc.FN_get_val_dict(advData,'pswcl')

                if _pswcl is None:
                    res_pswcl = get_pswcl_fromHead(self.user)
                    if res_pswcl:
                        _pswcl = res_pswcl.any_str

                        self._upd_quest(row_cl, dict(pswcl=_pswcl) )
                        

                    else:
                        raise ErrorRun_impl('{0} pswcl не определен из get_pswcl_fromHead'.format(self.s_err))
                else:
                    self.pswcl = _pswcl               
                
            else:
                self._add_quest(self.user)
           
        except Exception as ex:
            self._init_err(ex, self.s_err_serv)


    def _upd_quest(self, row_cl, arg_dict, updUser=None):

        try:            
            
            FM_init_advData(row_cl, arg_dict)

            row_cl.save()

            advData = AdvUser.get_advData(row_cl.user)
            if advData is None:
                raise ErrorRun_impl('{0}._upd_quest advData не определено'.format(self.s_err))

            if updUser:
                self.logincl_user = Res_proc.FN_get_val_dict(advData, 'logincl')
                self.pswcl_user   = Res_proc.FN_get_val_dict(advData, 'pswcl')

            else:
                self.logincl = Res_proc.FN_get_val_dict(advData, 'username')
                self.pswcl   = Res_proc.FN_get_val_dict(advData, 'pswcl')

        except Exception as ex:            
            self._init_err(ex, self.s_err_serv)
        

    def _add_quest(self, arg_user):

        try:
            res_templ = self.profForm.create_templDict_qust(arg_user)
            if not res_templ:
                raise ErrorRun_impl('{0} процедура create_templDict_qust вернула None '.format(self.s_err))

            dict_templ = res_templ.res_dict

            res_add = self.profForm.addProfilUser(dict_templ)
            if not res_add:
                raise ErrorRun_impl('{0} Ошибка создания объекта user_cl'.format(self.s_err))

            advData = AdvUser.get_advData(dict_templ['username'])
            if not advData:
                raise ErrorRun_impl('{0} нет данных advData '.format(self.s_err))

            self.logincl = advData['username']
            self.pswcl   = advData['pswcl']

        except Exception as ex:
            self._init_err(ex, self.s_err_serv)
        



