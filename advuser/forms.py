from django import forms
from django.contrib.auth.models import User
from django.core import validators
from django.core.exceptions import ValidationError
import json
from django.db import transaction

from .models import AdvUser, SprStatus

from .serv_sprstatus import Com_proc_sprstatus
from .serv_advuser import Struct_default_AdvUser, Com_proc_advuser, POL, GET_MES, ID_COMMAND
from app import (ErrorRun_impl, getUser, getLogin_cl, getPassword_cl, 
                 get_valFromDict, Res_proc)
from app import PM_write_except_into_log as write_into_log, PM_run_raise as run_raise

from app.com_data.any_mixin import verify_exists_email,  verify_exists_email_ext 
from app.com_data.proc_send_email import send_simpl_email

from .modify_models import Modify_user, Modify_advuser
from .serv_typestatus import type_status_user


# Удаление начальных/конечных пробелов in dict
def clear_space(arg_dict:dict)->dict:
    """ Удаление начальных/конечных пробелов в элементах словаря """    
    res = arg_dict
    lst = ('email', 'parentuser', 'username', 'first_name', 'last_name','idcomp')
    for item in lst:
        if res.get(item):
            res[item] = res[item].strip()            

    return res


def upd_space_into_empty(arg_dict:dict)->dict:
    """ Преобразование значений None or '' -> empty """
    keys = arg_dict.keys();
    for key in keys:
        if arg_dict.get(key) is None or arg_dict.get(key) == '':
            arg_dict[key] = 'empty'
    return arg_dict


# Изменение password участников проекта
class UpdPassword_byHeadForm(forms.Form):
    """ Форма изменения пароля на уровне руководителя группы """

    password = forms.CharField(label='Введите пароль', max_length=50, widget=forms.PasswordInput())
    password2 = forms.CharField(label='Повторите пароль', max_length=50, widget=forms.PasswordInput())

    # Верификация паролей на уровне формы 
    def clean(self):
        from django.contrib.auth.hashers import check_password

        super().clean()
        errors = {}

        password = self.cleaned_data['password']
        password2 = self.cleaned_data['password2']        

        if password != password2:
            errors['password'] = ValidationError('Пароли не совпадают')
                    
        if errors:
            raise ValidationError(errors)


    def save(self, arg_session:dict)->Res_proc:
        """ Сохранение пароля пользователя проекта
      arg_session используется для значений upd_username """

        from django.contrib.auth.hashers import make_password
        from app.com_serv_dbase.serv_modf_profil import user_upd_psw

        res_save = Res_proc()

        try:
            cd_clean = self.cleaned_data

            user = getUser(arg_session['upd_username'])
            if user is None:
                run_raise('Логин не определен', showMes=True)
            
            #user.password = make_password(cd_clean['password'])

            type_status = type_status_user(user);
            statusID = type_status.statusID
            pswcl = None
            if type_status.levelperm >=30:
                pswcl = Com_proc_advuser.get_val_from_advData(user, 'pswcl')

            dc_sp = dict(
                username = user.username,
                password = make_password(cd_clean['password']),
                pswcl    = pswcl or 'empty',
                status_id   = statusID
                )

            res_proc = user_upd_psw(dc_sp);            
            res_save.mes = 'Пароль пользователя изменен'

            #user.save()
            #res_save.res = True

            res_save.mes = 'Пароль пользователя обновлен'

        except Exception as ex:
            res_save.error = ex

        return res_save


# Изменение пароля предназначено для пользователей
class UpdPsw_byUserForm(UpdPassword_byHeadForm):
    """ Форма изменения пароля самими пользователями """

    datapsw_base = forms.CharField(label='Начальный пароль', max_length=50, widget=forms.PasswordInput())    
        
    field_order = ['datapsw_base','password','password2']

    # верификация ввода пароля на уровне формы
    def clean(self):
        from django.contrib.auth.hashers import check_password

        super().clean()
        errors = {}

        password = self.cleaned_data['password']
        password2 = self.cleaned_data['password2']
        datapsw_base = self.cleaned_data['datapsw_base']

        password_encode = getUser(self.data_username).password

        if not check_password(datapsw_base, password_encode ) :  # Проверка ввода исходного пароля
            errors['datapsw_base'] = ValidationError('Введите правильный начальный пароль')

        if password != password2:
            errors['password'] = ValidationError('Пароли не совпадают')
                    
        if errors:
            raise ValidationError(errors)

    def save(self, arg_user:User)->Res_proc:
        """ Сохранение пароля пользователя проекта
      arg_user используется для значений password from User """

        from django.contrib.auth.hashers import make_password
        from app.com_serv_dbase.serv_modf_profil import user_upd_psw

        res_save = Res_proc()

        try:

            psw = self.cleaned_data['password']
            password = make_password(psw)
            
            user = getUser(arg_user)            
            status = Com_proc_sprstatus.getStatus_or_None(user);

            dc_sp = dict(
                username = user.username,
                password = password,
                pswcl    = psw,
                status_id   = status.pk
                )

            res_proc = user_upd_psw(dc_sp);            
            res_save.mes = 'Пароль пользователя изменен'

        except Exception as ex:
            res_save.error = ex

        return res_save


class UpdStatus_userForm(forms.Form):
    """ Верификация и сохранение изменений status_id """

    from collections import namedtuple

    status = forms.ModelChoiceField(label='Статус', 
                    widget=forms.Select(attrs={"class":"form-control"}),
                    empty_label='--- Выберите статус ---',
                    queryset = SprStatus.objects.order_by('levelperm').filter(levelperm__gt=10, levelperm__lt=100).exclude(status='proj-sadm') )

    limitcon30 = forms.IntegerField(label='Лимит подкл.', 
                    help_text='Лимит подключений',
                    required=False,  
                    widget=forms.TextInput(attrs={"class":"form-control", "placeholder":"Лимит подключений"}))

    limitcon = forms.IntegerField(label='Лимит подкл.', 
                    help_text='Лимит подключений',
                    required=False,  
                    widget=forms.TextInput(attrs={"class":"form-control", "placeholder":"Лимит подключений"}))

    limitcon40 = forms.IntegerField(label='Лимит подкл. рукГрупп', 
                    help_text='Лимит подключений',
                    required=False,  
                    widget=forms.TextInput(attrs={"class":"form-control", "placeholder":"Лимит подкл. рукГрупп"}))

    limitcon70 = forms.IntegerField(label='Лимит подкл. супер-РукГр', 
                    help_text='Лимит подключений',
                    required=False,  
                    widget=forms.TextInput(attrs={"class":"form-control", "placeholder":"Лимит супер-РукГр"}))

    # Проверка на уровне формы
    def clean(self):

        super().clean()
        errors = {}
    
        res_clean  = namedtuple("res_clean", "used30 used40 used70 limit30 limit40 limit70")
        res_clean40  = namedtuple("res_clean40", "used30 limit30")
        dc_clean = None
        dc_clean40 = None

        dc_cleaned = self.cleaned_data;

        user_head = getUser(self.dc_param_verf.user_head)
        user_modf = getUser(self.dc_param_verf.user_modf)
        status_head = type_status_user(user_head)
        
        levelperm_sel = dc_clean['status'].levelperm
        levelperm_head = status_head.levelperm


        if levelperm_sel > levelperm_head:
            errors['status'] = 'Статус больше допустимого'

        if levelperm_sel == 40: #верификация заполнения поля limitcon30
            if not dc_cleaned.get('limitcon30'):
                errors['limitcon30'] = 'Укажите кол-во подключений менеджеров'
            
        if levelperm_sel == 70: # Проверка прав 
            if not dc_cleaned.get('limitcon'):
                errors['limitcon'] = 'Укажите кол-во подключений менеджеров'
            if not dc_cleaned.get('limitcon40'):
                errors['limitcon40'] = 'Укажите кол-во подключений рукГрупп'


        if not errors:
            limit_max = sys.maxsize

            if levelperm_sel > 30:  
                if levelperm_sel == 40:
                    
                    if levelperm_head < 100:
                        row = AdvUser.objects.filter(parentuser=user_head.username, status_levelperm=30).exclude(pk=user_modf)
                        limitcon_used = row.count()
                
                    dc_clean40 = res_clean40(
                        limit30= limit_max if levelperm_head > 99 else fields.get_limitcon40(40),
                        used30=0 if levelperm_head > 99 else limitcon_used
                        )
                        

                    # Верификация введенных значений для levelperm_sel=40
                    if dc_clean40.limit30 < (dc_clean40.used30 + dc_cleaned['limitcon30']) :
                        errors['limitcon30'] = 'Превышен лимит подключений'


                if levelperm_sel == 70:
                    if levelperm_head < 100:
                        row30 = AdvUser.objects.filter(parentuser=user_head.username, status_levelperm=30).exclude(pk=user_modf)

                        row40 = AdvUser.objects.filter(parentuser=user_head.username, status_levelperm=40).exclude(pk=user_modf)

                        row70 = AdvUser.objects.filter(parentuser=user_head.username, status_levelperm=70).exclude(pk=user_modf)

                        dc_limit70 = fields.get_limitcon70()     
                        dc_limit70 = dc_limit70.res_dict


                    dc_clean = res_clean(
                                used30= 0 if levelperm_head>99 else row30.count(), 
                                used40= 0 if levelperm_head>99 else  row40.count(), 
                                used70= 0 if levelperm_head>99 else  row70.count(),
                                limit30= limit_max if levelperm_head>99 else dc_limit70.get('limitcon') or 0,
                                limit40= limit_max if levelperm_head>99 else dc_limit70.get('limitcon40') or 0,
                                limit70= limit_max if levelperm_head>99 else dc_limit70.get('limitcon70') or 0
                                )

                    # Верификация введенных значений для levelperm_sel = 70
                    if dc_clean.limit30 < dc_clean.used30 + dc_cleaned['limitcon']:
                        errors['limitcon'] = 'Превышен лимит подключений'

                    if dc_clean.limit40 < dc_clean.used40 + dc_cleaned['limitcon40'] :
                        errors['limitcon40'] = 'Превышен лимит подключений'

                    if dc_cleaned.get('limitcon70') and (dc_clean.limit70 < (dc_clean.used70 + dc_cleaned['limitcont70'])):
                            errors['limitcon70'] = 'Превышен лимит подключений'

        if errors:
            raise ValidationError(errors)

    # используются в процедуре clean(self)
    param_verf = namedtuple("param_verf", "user_head user_modf")
    

    dc_param_verf = None
    #dc_clean = None

    @classmethod
    def save_data_status(cls, arg_head, arg_session)->Res_proc:
        """ Процедура на уровне class -> сохранение изменений status_id/limitcon """

        # Структура arg_session
        #lst_lvperm = lst_lvperm,
        #s_limit=s_limit,
        #upd_username=dc_datauser['username'],
        #upd_full_name=dc_datauser['full_name'],
        #upd_status=type_status.strIdent

        def clear_dict(arg_dict:dict, arg_tuple:tuple)->dict:
            """ Локальная процедура обработки dict js_struct """

            keys = arg_dict.keys()
            for k in keys:
                if k in arg_tuple:
                    del arg_dict[k]

            return arg_dict


        res_proc = Res_proc()       
        dc_clean = self.cleaned_data;

        user_head = getUser(arg_head)
        user_modf = getUser(arg_session['upd_username'])
        status_head = type_status_user(user_head)
        
        levelperm_sel = cd_clean['status'].levelperm
        levelperm_head = status_head.levelperm
        levelperm_user_base = type_status_user(user_modf).levelperm

        dc_servproc = dict(
                           user_modf=user_modf.username, 
                           user_head=user_head.username, 
                           status_id=cd_clean['status'].pk)

        num = 1
        dc_levelperm = {}
        for item in (20, 30, 40, 70) :
            dc = {item:num }
            dc_levelperm.update(dc)
            num += 1

        try:

            div = dc_levelperm[levelperm_sel] - dc_levelperm[levelperm_user_base]
            if  abs(div) > 1:
                run_raise('Изменение статуса более чем на один порядок - отклонено',showMes=True)

            if div < 0: # Понижение привелигий

                js_struct = Com_proc_advuser.get_js_struct(user_modf)
                keys = js_struct.keys()                    

                if levelperm_sel == 40:
                    js_struct = clear_dict(js_struct, ('limitcon40','limitcon70'))
                    js_struct['limitcon'] = dc_clean['limitcon30']
                    lst = [70,40]

                elif levelperm_sel in (20, 30):
                    js_struct = clear_dict(js_struct, ('limitcon','limitcon40','limitcon70'))

                    if levelperm_sel == 30:
                        lst = [70,40,30]
                    else:
                        lst = [70,40,30,20,10]

                dc_servproc['reduce'] = lst
                # ---------- Конец контента обработки понижения статуса

            if div > 0:                    
                if levelperm_sel == 40:
                    js_struct.update(dict(
                        limitcon=dc_clean['limitcon30']
                        ))

                if levelperm_sel == 70:
                    js_struct.update(dict(
                        limitcon=dc_clean['limitcon'],
                        limitcon40=dc_clean['limitcon40'],
                        limitcon70=dc_clean('limitcon70') or 0
                        ))

            dc_servproc['js_struct'] = js_struct                



        except Exception as ex:
            res_proc.error = ex

        return res_proc


# используется для подтверждения перед удалением профиля
class AdvPanel_form(forms.Form):
    proj_memb  = forms.CharField(label='Логин менеджера', max_length=50, 
                    widget=forms.TextInput(
                        attrs={"class":"form-control", 
                               "placeholder":"Участник проекта",
                               "disabled" : "disabled"             
                               }) ) 


# Для руководителей проекта
# addprof_member
class AdvPanel_profForm(forms.Form):
    id_command = forms.ChoiceField(label='Метод обработки',                     
                    choices=ID_COMMAND,widget=forms.RadioSelect())
    proj_memb  = forms.CharField(label='Логин менеджера', max_length=50, 
                widget=forms.TextInput(attrs={"class":"form-control", "placeholder":"Участник проекта"}) ) 


"""
Базовый класс для редактирования данных профиля
"""
class Base_profForm(forms.Form):
    """ Форма для клиентов  """

    # -------------- Поля формы для модели User ------------

    first_name = forms.CharField(label='Имя', max_length=50, 
                    widget=forms.TextInput(attrs={"class":"form-control", "placeholder":"Имя"}) ) 
    last_name  = forms.CharField(label='Фамилия', max_length=50,
                    widget=forms.TextInput(attrs={"class":"form-control",  "placeholder":"Фамилия"}) )
    email      = forms.EmailField(label='Эл. почта', max_length=50, 
                    required=False,
                    widget=forms.TextInput(attrs={"class":"form-control",  "placeholder":"Адрес элПочты" }),
                    help_text='Обратная связь, восстановление пароля')

    # ------------ Поля формы для модели AdvUser ---------------

    phone       = forms.CharField(label='Телефон', max_length=15,
                    required=False,
                    help_text = 'Обратная связь',
                    widget=forms.TextInput(attrs={"class":"form-control", "placeholder":"Телефон" }) )    
    idcomp      = forms.CharField(label='ID компании',
                    help_text='Для зарегистрированных клиентов',
                    required=False,
                    widget=forms.TextInput(attrs={"class":"form-control", "placeholder":"ID компании" } ))
    post        = forms.IntegerField(label='ПочтИндекс', 
                    help_text='Регион клиента',
                    required=False,  
                    widget=forms.TextInput(attrs={"class":"form-control", "placeholder":"Почтовый индекс"}))    
    sendMes     = forms.ChoiceField(label='Получать сообщ.', 
                    help_text = 'Интересная информация, восстановление пароля',
                    choices=GET_MES,
                    widget=forms.RadioSelect())
                    
    pol         = forms.ChoiceField(label='Пол', choices=POL,widget=forms.RadioSelect())
   
    ageGroup    = forms.IntegerField(label='Возраст',
                    required=False,
                    help_text = 'Важно, для отбора подаваемой информации!',
                    widget=forms.TextInput(attrs={"class":"form-control", "placeholder":"Возраст" }) )  

    """
    Процедура создания шаблона dict для добавления qust-simp
    return res_proc.res_dict 
    """
    @classmethod
    def create_templDict_qust(cls, arg_user, arg_pswcl=None):        
        from .serv_sprstatus import Com_proc_sprstatus 

        res_proc = Res_proc()

        def run_raise(s_arg, showMes=None):
                s_err = 'advuser.forms.Base_profForm.create_templDict_quest'

                if showMes:            
                    raise ErrorRun_impl('verify##{0}'.format(s_arg))
                else:
                    raise ErrorRun_impl('{0} {1}'.format(s_err, s_arg))

        try:
            _username = ''
            _user = getUser(arg_user)
            if _user is None:
                _username = arg_user
            else:
                _username = _user.username

            logincl = getLogin_cl()
            pswcl = ''
            if arg_pswcl:
                pswcl = arg_pswcl
            else:
                res_pswcl = getPassword_cl()
                if res_pswcl: pswcl = res_pswcl
                else:
                    ErrorRun_impl('NotData##advuser.forms.Base_profForm.create_templDict_quest пароль не создан')

            _dict = dict( 
                        username = logincl,
                        first_name = 'Гость',
                        last_name ='сайта',
                        password = pswcl,
                        pswcl    = pswcl,
                        parentuser = _username,
                        status_id = Com_proc_sprstatus.get_status_qust_simp().pk,
                        sendMes = 'false',
                        pol = '-'
                        )

            res_proc.res_dict = _dict

        except Exception as ex:
            res_proc.error = ex

        return res_proc


    def save_add(self, arg_user:User)->Res_proc:
        """ Процедура обработки добавления профиля клиента """
        
        from django.contrib.auth.hashers import make_password        
        from app.com_serv_dbase.serv_modf_profil import serv_add_profil
               

        res_proc = Res_proc()
        cd_dict = self.cleaned_data

        s_error = 'ValueError##advuser.form.Base_profilForm.save_add'

        try:
            parentuser = Com_proc_advuser.get_user_cons(arg_user)
            if parentuser is None:
                run_raise(s_error+' Консультант гостВхода не найден')

            pswcl = getPassword_cl()
            if pswcl is None: 
                run_raise(s_error +' Пароль гостВхода не создан')

            statusID = Com_proc_sprstatus.get_status_qust_regs().pk
            cd_dict.update(
                    dict(
                            parentuser = parentuser.username,
                            pswcl = pswcl,
                            password = make_password(pswcl),
                            username = getLogin_cl(),
                            is_active='true',
                            status_id= statusID,
                            status= statusID,
                            full_name= cd_dict['first_name'] + ' ' + cd_dict['last_name']
                        ))

            cd_dict = clear_space(cd_dict)
            cd_dict = upd_space_into_empty(cd_dict)

            res_proc = serv_add_profil(cd_dict)

        except Exception as ex:
            res_proc.error = ex

        return res_proc


    def save_upd(self, arg_user:User, arg_parentuser)->Res_proc:
        """ Процедура обработки обновления профиля клиента """

        from app.com_serv_dbase.serv_modf_profil import serv_add_profil               
        from .serv_sprstatus import Com_proc_sprstatus

        try:
            
            res_proc = Res_proc()
            cd_dict = self.cleaned_data
            s_error = 'ValueError##advuser.form.Base_profilForm.save_upd'

            statusID = Com_proc_sprstatus.get_statusID_user(arg_user)

            cd_dict.update(
                dict(username=arg_user.username,
                     # pswcl=dict_user.get('pswcl') or '',
                     # idcomp=cd_dict.get('idcomp') or 'empty',                    
                     status_id=statusID,
                     status = statusID,
                     parentuser=arg_parentuser.username
                     ))
            
            cd_dict = clear_space(cd_dict)
            cd_dict = upd_space_into_empty(cd_dict)                        

            res_proc = serv_add_profil(cd_dict, serv_proc='sp_serv_upd_profil')
            
        except Exception as ex:
            res_proc.error = ex

        return res_proc
    

#************** Конец контента class Base_profForm  *****************


# ****************************************************************************

# Форма обновленияПрофиля для руководителя проекта или его субРуководители
class Modf_prof_byHeaderForm(Base_profForm):    
    """ Для рукГрупп -> форма обновления профиля """

    ageGroup    = forms.IntegerField(label='Возраст',
                    widget=forms.TextInput(attrs={"class":"form-control", "placeholder":"Возраст" }) ) 
     
    status      = forms.ModelChoiceField(label='Статус', 
                    widget=forms.Select(attrs={"class":"form-control"}),
                    empty_label='--- Выберите статус ---',
                    queryset = SprStatus.objects.order_by('levelperm').filter(levelperm__gt=10, levelperm__lt=100).exclude(status='proj-sadm') )


    def save(self, arg_username, arg_parentuser): 
        """ Сохранение изменений профиля 
        arg_username для обработки профиля
        arg_parentuser для доступа к значению pswcl на уровне рукГруппы 
        """

        from app.models import spr_fields_models
        from app.com_serv_dbase.serv_modf_profil import serv_add_profil    

        def set_limitcon(levelperm:int):
            """ Инициализация значения limitcon """
            nonlocal cd_dict

            limitcon = spr_fields_models.get_limitcon40(levelperm) 
            if limitcon == 0 :
                run_raise('form.AddProf_memberForm: Нет данных limitcon')

        # --------------------------------------------------------------


        res_proc = Res_proc();
        s_errDown = 'Резкое понижение статуса. Обработка остановлена'
        s_errUp = 'Резкое повышение статуса. Обработка остановлена'

        try:

            user = getUser(arg_username)
            if user is None:
                run_raise('Сбой обработки профиля: пользователь не определен' , showMes=True) 

            cd_dict = self.cleaned_data

            statusID = cd_dict.get('status').pk
            levelperm = Com_proc_sprstatus.get_levelperm(statusID)

            type_status_base = type_status_user(user)
            statusID_base = type_status_base.statusID
            levelperm_base = type_status_base.levelperm

            if levelperm_base == 70:    # Резкое понижение статуса допустимо на уровень 40
                if levelperm < 40:
                    run_raise(s_errDown, showMes=True)

            elif levelperm_base == 40:  # Резкое понижение статуса допустимо на уровень 30
                if levelperm < 30:      
                    run_raise(s_errDown, showMes=True)

            else:
                if levelperm_base == 20 and levelperm > 30: # Резкое повышение статуса только на уровень 30
                    run_raise(s_errUp, shwoMes=True)
                if levelperm_base == 30 and levelperm > 40: # Резкое повышение статуса только на уровень 40
                    run_raise(s_errUp, shwoMes=True)

            # Обработка понижения статуса 

            # Инициализация limitcon повышение привилегий 
            if levelperm_base == 40 and levelperm == 70 :
                set_limitcon(levelperm)

            # Инициализация limitcon при понижении привилегий 
            if levelperm_base == 70 and levelperm == 40 :
                set_limitcon(levelperm)
                
                       
            pswcl = res_proc.FN_get_val_dict(cd_dict,'pswcl')
            logincl = res_proc.FN_get_val_dict(cd_dict,'logincl')

            if pswcl is None:   #восстановление пароля гостВхода по значению pswcl рукГруппы 
                pswcl = Com_proc_advuser.get_val_from_advData(arg_parentuser, 'pswcl')
                cd_dict['pswcl'] = pswcl

            if logincl is None:
                logincl = getLogin_cl()
                cd_dict['logincl'] = logincl

            cd_dict.update(dict(
                               username = user.username,
                               status_id= statusID,
                               status= statusID
                                )
                        )

            # удаление пробелов. Для подстраховки 
            cd_dict = clear_space(cd_dict)
            cd_dict = upd_space_into_empty(cd_dict)

            res_proc = serv_add_profil(cd_dict, serv_proc='sp_serv_upd_profil')

        except Exception as ex:
            res_proc.error = ex;

        return res_proc
   
    
# *********** RegisterExt_profForm ***********

# Форма для редактирования профиля самими proj_member
# предназначена для участников проекта
# отличаетс от AddProf_memberForm набором полей
class Modf_prof_byuserForm(Base_profForm):   
    """ Для пользователй проекта -> измПрофиля """
    ageGroup    = forms.IntegerField(label='Возраст',
                    widget=forms.TextInput(attrs={"class":"form-control", "placeholder":"Возраст" }) ) 
   

    def save(self, arg_user, arg_parentuser)->Res_proc:
        from app.com_serv_dbase.serv_modf_profil import serv_add_profil

        res_proc = Res_proc()
        cd_dict = self.cleaned_data
        s_error = 'ValueError##advuser.form.UpdProf_memberForm.save'

        try:

            user = getUser(arg_user)
            if user is None:
                run_raise(s_error + ' Пользователь не найден в БД')
            

            # Верификация pswcl and logincl 
            pswcl = res_proc.FN_get_val_dict(cd_dict, 'pswcl')
            logincl = res_proc.FN_get_val_dict(cd_dict, 'logincl')
            if pswcl is None:
                pswcl = Com_proc_advuser.get_val_from_advData(arg_parentuser, 'pswcl')
                cd_dict['pswcl'] = pswcl

            if logincl is None:
                logincl = getLogin_cl()
                cd_dict['logincl'] = logincl

            statusID = Com_proc_sprstatus.get_statusID_user(user)  
            
            cd_dict.update(
	            dict(username=user.username,                        
			            status_id=statusID,
			            status = statusID,
			            parentuser=arg_parentuser.username
			            ))

            # удаление пробелов. Для подстраховки
            cd_dict = clear_space(cd_dict)
            cd_dict = upd_space_into_empty(cd_dict) # дополнительное преобразование

            res_proc = serv_add_profil(cd_dict, serv_proc='sp_serv_upd_profil')

                        
        except Exception as ex:
            res_proc.error = ex;

        return res_proc



# Добавление профиля участника проекта
# форма используется только proj_header or proj_subheader
class AddProf_memberForm(Modf_prof_byHeaderForm):
    """ Для руководителй групп -> создание профиля участников проекта """
    username    = forms.CharField(label='Логин менеджера', max_length=50, 
                    widget=forms.TextInput(attrs={"class":"form-control", "placeholder":"Логин"}) ) 

    password    = forms.CharField(label='Пароль', max_length=50, 
                    widget=forms.PasswordInput(attrs={"class":"form-control", "placeholder":"Пароль"}) ) 
    password1    = forms.CharField(label='Повт. пароль', max_length=50, 
                    widget=forms.PasswordInput(attrs={"class":"form-control", "placeholder":"Повторить"}) ) 
    


    field_order = ['username', 'password','password1', 'first_name','last_name', 'email', 'phone', 'idcomp', 'post','sendMes','pol', 'ageGroup', 'status','parentuser' ]


    # Создание нового профиля - участника проекта
    # использование сервПроцедуры 
    def save(self, arg_user):    
        """ Сохранение профиля пользователя на уровне рукГруппы """

        from django.contrib.auth.hashers import make_password        
        from .serv_advuser import Com_proc_advuser
        from app.com_serv_dbase.serv_modf_profil import serv_add_profil
        from collections import namedtuple
        from app.models import spr_fields_models

        cd_dict = self.cleaned_data
        Perm = namedtuple('Perm','levelperm,statusID,parentuser')
        s_error = 'advuser.form.AddProf_memberForm.save'
        s_err   = 'verify##'

        def get_perm(arg_user:User)->Perm:
            """ Верификация привилегий, statusID, parentuser """

            nonlocal cd_dict

            parentuser = None
            if arg_user.is_superuser:
                try:
                    parentuser = Com_proc_advuser.get_user_head();
                except:
                    parentuser = arg_user

            else: parentuser = arg_user

            type_status = type_status_user(arg_user)

            res_tupl = Perm(levelperm=type_status.levelperm, 
                            statusID=cd_dict['status'].pk,
                            parentuser=parentuser.username)
            return res_tupl

        def seting_pswcl(user):
            """ Обработка пароля госВхода pswcl """
            nonlocal cur_levelperm, cd_dict

            pswcl = None

            if user.is_superuser :
                pswcl = getPassword_cl()
            
            else:
                if cur_levelperm > 30:  # Если это рукГруппы назначить новый пароль pswcl
                    pswcl = getPassword_cl()
                else:
                    pswcl = Com_proc_advuser.get_val_from_advData(arg_user, 'pswcl')

            if pswcl is not None:
                cd_dict['pswcl'] = pswcl
            else:
                run_raise('Пароль гостВхода не создан')


        res_proc = Res_proc();

        try:            

            # Верификация ввода пароля 
            if cd_dict['password'] != cd_dict['password1']:
                run_raise('Не совпадение полей ввода пароля', showMes=True)

            user = getUser(arg_user)
            cd_perm = get_perm(user)           

            logincl = getLogin_cl()


            statusID = cd_dict['status'].pk
            cur_levelperm = Com_proc_sprstatus.get_levelperm(statusID)

            if cur_levelperm == 20 :
                run_raise('Профиль клиента должен создавать пользователь гостВхода', showMes=True)

            if cd_perm.levelperm  < 40 or cur_levelperm >= cd_perm.levelperm :
                run_raise(s_err + 'Нет прав на создание профиля', showMes=True)

            if cur_levelperm > 30 :
                limitcon = spr_fields_models.get_limitcon40(cur_levelperm) 
                if limitcon == 0 :
                    run_raise('form.AddProf_memberForm: Нет данных limitcon')

                cd_dict.update(dict(limitcon=limitcon))
            
            seting_pswcl(user)  # Создание заполнение cd_dict[pswcl]

            cd_dict.update(
                dict(
                   parentuser = cd_perm.parentuser,
                   password = make_password(cd_dict['password']),
                   password_cl = make_password(cd_dict['pswcl']),
                   logincl = logincl,
                   full_name= cd_dict['first_name'] + ' ' + cd_dict['last_name'],
                   is_active='true',
                   status_id= statusID,
                   status= statusID
                    )
                )

            res_proc = serv_add_profil(cd_dict)            

        except Exception as ex:
            res_proc.error = ex;

        return res_proc
        


# Форма контактов
class ContUser_extForm(forms.Form):
    username = forms.CharField(label='Имя', 
                               max_length=30,
                               widget=forms.TextInput(attrs={"class":"form-control border border-primary", 
                                                             "placeholder":"Имя"}))
    email = forms.EmailField(label='Эл. адрес',
                               max_length=50, 
                               widget=forms.EmailInput(attrs={"class":"form-control border border-primary",
                                                             "placeholder":"Email"} ))
    subject = forms.CharField(label='Тема сообщения', 
                               max_length=50, 
                               widget=forms.TextInput(attrs={"class":"form-control border border-primary",  
                                                             "placeholder":"Тема"}))
    mes = forms.CharField(label='Текст сообщения', 
                          widget=forms.Textarea(attrs={'rows':'2', 
                             "class":"md-textarea form-control border-0"
                                                       }))