from django.shortcuts import render, redirect
from django.core.cache import cache

from .forms import (Base_profForm, AddProf_memberForm, AdvPanel_profForm, 
                    Modf_prof_byHeaderForm, Modf_prof_byuserForm, 
                    UpdPassword_byHeadForm, UpdPsw_byUserForm, UpdStatus_userForm )

from django.contrib.auth.decorators import login_required
from .serv_advuser import Com_proc_advuser
from app import PM_run_raise as run_raise, getUser
from .serv_typestatus import type_status_user



def modf_data_dict(arg_dc:dict)->dict:
    """ Сброс значений empty or ''  into None """
    dc_res = arg_dc
    for key in dc_res.keys():
        val = dc_res.get(key)
        if val == 'empty' or val == '':
            dc_res[key] = None

    return dc_res


# Контроллеры перенаправления на редактирование
# Перенаправление сообщения на страницу empty 
# используется для верификации или отсутствия данных 
def redirect_empty(arg_title=None, arg_mes=None):
    """ Перенаправление по url emptyext
    arg_title  заголовок на странице default None -> Сообщение сервера
    arg_mes    текстовое сообщение   default None -> Сервер отклонил обработку
    """
    cache.set('emptyext', dict( title=arg_title or 'Сообщение сервера' , mes=arg_mes or 'Сервер отклонил обработку' ) )
    return redirect('emptyext')


# url  /advuser/modpanelprof
# Административная панель 
@login_required
def AdvPanel_prof(request):
    from .serv_typestatus import type_status_user


    user = request.user
    type_status = type_status_user(user)

    if type_status.levelperm < 40:
        return redirect_empty(arg_title='Нет прав', arg_mes='Нет прав на обработку профиля участника проекта')


    if request.method == 'POST':

        form = AdvPanel_profForm(request.POST)
        if form.is_valid():

            proj_memb = form.cleaned_data['proj_memb']
            id_command = int(form.cleaned_data['id_command'])
            if id_command == 1:  # изменить профиль
                
                cache.set('Upd_prof_member', proj_memb)
                return redirect('updprofiluser')                                
            elif id_command == 2: # изменение пароля 

                cache.set('UpdPassword_user', proj_memb) # передает данные для username 
                return redirect('updpswuser')                

            else: # Изменение status
                cache.set('UpdStatus_user', proj_memb)
                return redirect('updpermuser')          
    else:
        form = AdvPanel_profForm()
        return render(request,'advuser/header_panel.html', dict(form=form, error=None))
 

# url: updpermuser
# Изменение levelperm -> status_id  только для рукГрупп
@login_required
def UpdStatus_user(request):
    """ Контроллер обраотки изменений status_id
    Изменения осуществляются только рукГрупп
    """

    if not cache.has_key('UpdStatus_user'): 
        return redirect_empty(arg_title='Сервер отклонил обработку', arg_mes='Параметры запроса устарели')

    user = cache.get('UpdStatus_user')
    user = getUser(user)
    if user is None:
        cache.delete('UpdStatus_user')
        return redirect_empty(arg_title='Сервер отклонил обработку', arg_mes='Нет данных по логину')
    

    if request.method == 'POST':
        form = UpdStatus_userForm(request.POST)
        cd_session = request.session['UpdStatus_user']

        if form.is_valid():
            if form.is_valid():
                user = request.user;

                res_save = form.save_data_status(user, cd_session)




    else: # Обработка запроса GET 
        
        from .serv_sprstatus import Com_proc_sprstatus
        from app.models import spr_fields_models
        import json

        type_status = type_status_user(user)
        user_master = getUser( request.user)
        type_status_master = type_status_user(user_master)

        if type_status_master.levelperm < 40 or type_status_master.levelperm <= type_status.levelperm:
            return redirect_empty(arg_title='Сервер отклонил обработку', arg_mes='Нет прав на обработку')

        if type_status.levelperm < 30:
            return redirect_empty(arg_title='Сервер отклонил обработку', arg_mes='Статус клиента не меняется')


        if type_status.levelperm == 100 :
            return redirect_empty(arg_title='Сервер отклонил обработку', arg_mes='Статус руководителя проекта постоянный')


        dc_limit = spr_fields_models.get_limitcon70()
        res_dict = dc_limit.res_dict
        lst_lvperm = Com_proc_sprstatus.get_list_levelperm().res_list
        res_dict.update( dict(lvperm=lst_lvperm) )

        s_limit = json.dumps(res_dict, ensure_ascii=True)

        dc_datauser = Com_proc_advuser.get_advData(user)


        dc_session = dict( 
                       lst_lvperm = lst_lvperm,
                       s_limit=s_limit,
                       upd_username=dc_datauser['username'],
                       upd_full_name=dc_datauser['full_name'],
                       upd_status=type_status.strIdent                       
            )


        request.session['UpdStatus_user'] = dc_session  

        dc_initial = dict(status=type_status.statusID, limitcon=dc_datauser.get('limitcon') or 0)
        form = UpdStatus_userForm(initial=dc_initial)
        
        res_cont = dict(form=form)
        res_cont.update(dc_session)

        return render(request, 'advuser/upd_status_user.html', res_cont)


"""
url: updpswuser 
"""
@login_required
def UpdPassword_user(request):
    """ Контроллер изменения пароля участника проекта """
    
    from .serv_typestatus import type_status_user
    from .serv_sprstatus import Com_proc_sprstatus

    user = request.user
    type_status = type_status_user(user)

    if not type_status:
        return redirect_empty(arg_title='Статус', 
                              arg_mes='Сервер остановил обработку: статус не определен ')
        

    if type_status.levelperm < 40 :
        return redirect_empty(arg_title='Нет прав', 
                              arg_mes='Нет прав на создание профиля участника проекта')

    if request.method == 'POST':
        form = UpdPassword_byHeadForm(request.POST)
        dc_session = request.session['UpdPassword_user']

        if form.is_valid():

            res_save = form.save(dc_session)

            if res_save:                
                
                dict_cache = dict(username=dc_session['upd_username'], mes=res_save.mes)                
                cache.set('Success_register_user', dict_cache)
                del request.session['UpdPassword_user']

                return redirect('ver_profil')  # переход на view Success_register_user

            else:
                # возврат формы на доработку и отображение сообщений об ошибках 
                dc_cont = dict(form=form)
                dc_cont.update(dc_session)
                dc_cont.update(error=res_save.error )

            return render(request, 'advuser/upd_password_user.html', dc_cont) 


        else: # возврат формы на доработку 

            dc_cont = dict(form=form)  # отображение ошибок, выявленных на уровне валидации form
            dc_cont.update(dc_session) 

            return render(request, 'advuser/upd_password_user.html', dc_cont) 

    else:   # Обработка GET

        if not cache.has_key('UpdPassword_user'):  
                return redirect_empty(arg_mes='Данные устарели')

        upd_username = cache.get('UpdPassword_user')
        cache.delete('UpdPassword_user')        
        
        dc_cont = Com_proc_advuser.get_advData(upd_username)
        if dc_cont is None:
            return redirect_empty(arg_title='Нет данных', 
                                  arg_mes='Сервер остановил обработку: нет данных для обработки ')


        form = UpdPassword_byHeadForm()
        kwargs=dict(username=upd_username)
        status = Com_proc_sprstatus.getStatus_or_None(**kwargs)

        dc_session = dict(
                       title='Изменение пароля пользователя проекта',
                       username_header=user.username,
                       full_name=user.get_full_name(),
                       statusInfo=type_status.strIdent,
                       upd_username=dc_cont['username'],
                       upd_full_name=dc_cont['full_name'],
                       upd_status=status.strIdent 
            )

        request.session['UpdPassword_user'] = dc_session  # перенос данных из cache into session

        res_cont = dict(form=form)
        res_cont.update(dc_session)
        
        return render(request, 'advuser/upd_password_user.html', res_cont)


# Изменение пароля самими пользователями
# url: updpswbyUser
@login_required
def UpdPsw_byUser(request):
    """ Изменение пароля самими пользователями """

    from .serv_typestatus import type_status_user

    user = getUser(request.user)
    
    if request.method == 'POST':

        form = UpdPsw_byUserForm(request.POST)
        form.data_username = user.username
        dc_session = request.session['UpdPsw_byUser']

        if form.is_valid():

            res_save = form.save(user)

            if res_save:                
                
                dict_cache = dict(username=user.username, mes=res_save.mes)                
                cache.set('Success_register_user', dict_cache)
                del request.session['UpdPsw_byUser']

                return redirect('ver_profil')  # переход на view Success_register_user

            else:
                # возврат формы на доработку и отображение сообщений об ошибках 
                dc_cont = dict(form=form)
                dc_cont.update(dc_session)
                dc_cont.update(error=res_save.error )

            return render(request, 'advuser/upd_password_by_user.html', dc_cont) 


        else: # возврат формы на доработку 

            dc_cont = dict(form=form)  # отображение ошибок, выявленных на уровне валидации form
            dc_cont.update(dc_session) 

            return render(request, 'advuser/upd_password_by_user.html', dc_cont) 


    else:   # Обработка GET запроса
              
        type_status = type_status_user(user)
        dc_cont = Com_proc_advuser.get_advData(user)

        dc_session = dict(
                       title='Изменение пароля пользователя проекта',                      
                       upd_username=dc_cont['username'],
                       upd_full_name=dc_cont['full_name'],
                       upd_status=type_status.strIdent                       
            )

        request.session['UpdPsw_byUser'] = dc_session  

        dc_init = dict(dataupd=user.username)
        form = UpdPsw_byUserForm(initial=dc_init)

        res_cont = dict(form=form)
        res_cont.update(dc_session)

        return render (request, 'advuser/upd_password_by_user.html' , res_cont)
    



# Создание профиля для участника проекта
# url /advuser/addprof_member
@login_required
def AddProf_member(request):
    """ Для рукГрупп -> создание профиля участников проекта """

    from .serv_typestatus import type_status_user

    user = request.user
    type_status = type_status_user(user)

    if not type_status:
        return redirect_empty(arg_title='Статус', arg_mes='Сервер остановил обработку: статус не определен ')
        

    if type_status.levelperm < 40 :
        return redirect_empty(arg_title='Нет прав', arg_mes='Нет прав на создание профиля участника проекта')
        

    parentuser = Com_proc_advuser.get_user_cons(user)
    if parentuser is None:
        if user.is_superuser:
            parentuser = user
        else:
            return redirect_empty(arg_title='Сообщение сервера', arg_mes='Наставник не определен')
        

    if request.method == 'POST':
        form = AddProf_memberForm(request.POST)
        if form.is_valid():
            res_save = form.save(user)

            if res_save:
                dict_cache = dict(username=res_save.any_str, mes=res_save.mes)
                cache.set('Success_register_user', dict_cache)
                
                return redirect('ver_profil')

            else:
                return render(request, 'advuser/regUser_ext.html', dict(
                            res=False,
                            parentuser=parentuser.username,
                            error=res_save.error,
                            title='Редактор профиля', 
                            form=form
                            ))

        else:
            return render(request, 'advuser/regUser_ext.html', dict(
                            res=False,
                            parentuser=parentuser.username,
                            error='Ошибка/и заполнения полей формы',
                            title='Создание профиля', 
                            form=form
                            ))

    else:

        # Загрузить данные из внешнего файла 
        # используется при тестировании ввода 
        #         
        #from app import loadJSON_file_modf
        #dict_js = loadJSON_file_modf('advuser/arg_RegisterIns_profForm_member')       
        #form = AddProf_memberForm(initial=dict_js)

        form = AddProf_memberForm()
        
        return render(request, 'advuser/regUser_ext.html', dict(
                            parentuser=parentuser.username,
                            res=True,
                            error='',
                            title='Создание профиля', 
                            form=form
                            ))

# конец контроллеров адмПанели 

"""
Только для рукГруппы
Вместо RegisterExt_profForm 
url: updprofiluser
name: updprofiluser
"""
def Modf_prof_byheader(request):
    """ Для рукГрупп -> изменение профиля участников проекта """

    from .modify_models import get_dictData_init_Form
    from .serv_advuser import Com_proc_advuser

    parentuser = request.user #Com_proc_advuser.get_user_cons(user)

    if request.method == 'POST':
        form = Modf_prof_byHeaderForm(request.POST)

        if form.is_valid():

            if 'Upd_prof_member' in request.session:
                username = request.session['Upd_prof_member']['username']
               
            else:
                return redirect_empty(arg_mes='Сервер отклонил обработку: пользователь не определен' )
                

            res_save = form.save(username, parentuser)
            if res_save:

                #Success_register_user заполнение cache 
                dict_cache = dict(username=username, mes=res_save.mes)

                cache.set('Success_register_user', dict_cache)
                del request.session['Upd_prof_member']

                return redirect('ver_profil')  # переход на view Success_register_user

            else:

                return render(request, 'advuser/regUser_ext.html', dict(
                            parentuser=parentuser.username,
                            res=False,
                            error=res_save.error,
                            title='Редактор профиля', 
                            form=form
                            ))
            
        else:
            return render(request, 'advuser/regUser_ext.html', dict(
                            parentuser=parentuser.username,
                            res=False,
                            error='Проверьте введенные данные',
                            title='Редактор профиля', 
                            form=form
                            ))

    else:  # GET запрос
        try:
            # cache инициализируется из AdvPanel_prof
            if not cache.has_key('Upd_prof_member'):  
                return redirect_empty(arg_mes='Данные устарели')

            username = cache.get('Upd_prof_member')
            cache.delete('Upd_prof_member')

            res_verify = Com_proc_advuser.verify_yourHead(username, parentuser)
            if not res_verify:
                if res_verify.mes: # сообщение для отображения 
                    return redirect_empty(res_verify.mes)
                else:
                    return redirect_empty(arg_title='Отказ сервера', arg_mes='Процедура обработки остановлена на сервере')
               
            # Выполняется проверка привилегий parentuser 
            dict_param = get_dictData_init_Form(parentuser.pk, username)
            if dict_param:

                dict_session = dict(username=username)
                request.session['Upd_prof_member'] = dict_session  # перенос данных из cache into session

                dict_initial = dict_param.res_dict
                dict_initial = modf_data_dict(dict_initial)  # сброс значений '' or 'empty'

                form = Modf_prof_byHeaderForm(initial=dict_initial)
                return render(request, 'advuser/regUser_ext.html', dict(
                                parentuser=parentuser.username,
                                res=True,
                                title='Редактор профиля', 
                                form=form
                                ))
        except Exception as ex:
            return redirect_empty()


"""
Изменение профиля самими участниками проекта proj_member
"""
@login_required
def Modf_prof_byuser(request):
    """ Изменение профиля самими участниками проекта """
    
    user = request.user
    parentuser = Com_proc_advuser.get_user_cons(user)
    if parentuser is None:
        return redirect_empty(arg_mes='Сервер отклонил обработку: наставник не определен' )

    if request.method == "POST":
        form = Modf_prof_byuserForm(request.POST)
        if form.is_valid():
            res_save = form.save(user.username, parentuser)
            if res_save:

                #Success_register_user заполнение cache 
                dict_cache = dict(username=user.username, mes=res_save.mes)

                cache.set('Success_register_user', dict_cache)

                return redirect('ver_profil')  # переход на view Success_register_user

            else:
                return render(request, 'advuser/regUser_ext.html', dict(
                            parentuser=parentuser.username,
                            res=False,
                            error=res_save.error,
                            title='Редактор профиля', 
                            form=form
                            ))

        else:
            return render(request, 'advuser/regUser_ext.html', dict(
                            parentuser=parentuser.username,
                            res=False,
                            error='Проверьте введенные данные',
                            title='Редактор профиля', 
                            form=form
                            ))
    else:
        try:

            dict_param = dict()

            if not Com_proc_advuser.get_advData_user(user, dict_param) :
                return redirect_empty(
                        arg_title='Отказ сервера', 
                        arg_mes='Нет данных для обработки' )

            dict_param = modf_data_dict(dict_param)  # сброс значений '' or 'empty'
            form = Modf_prof_byuserForm(initial=dict_param)

            dc_cont = dict(
                            parentuser=parentuser.username,
                            res=True,
                            title='Редактор профиля', 
                            form=form
                            )

            return render(request, 'advuser/regUser_ext.html', dc_cont)
        except Exception as ex:
            return redirect_empty()

"""
Контроллер обр-ки запроса на создание профиля гостевогоВхода
url: /advuser/addprofquestins   /advuser/addprofquestupd

"""
@login_required
def AddProf_quest(request):
    """ Добавление/изм профиля клиента """

    from .serv_advuser import type_status_user, Com_proc_advuser
   

    user = request.user 
    parentuser = Com_proc_advuser.get_user_cons(user)
    if parentuser is None:
        return redirect_empty(arg_mes='Наставник не определен')


    if request.method == 'POST':

        form = Base_profForm(request.POST)

        # dict по умолчанию для сообщений об ошибках 
        dc_cont_err = dict(
            res=False,
            parentuser=parentuser.username,
            error= 'Сервер отклонил обработку. Проверьте введенные данные',
            title='Создание профиля',
            form=form
            )

        if form.is_valid():
            user = getUser(request.user)

            res_save = form.save_add(user)
            if res_save:  # успешное обновление 

                #Success_register_user заполнение cache 
                dict_cache = dict(username=res_save.any_str, mes=res_save.mes)
                cache.set('Success_register_user', dict_cache)

                return redirect('ver_profil')

            else:  # ошибка обработки 
                dc_cont_err.update(dict(error=res_save.error))
                return render(request, 'advuser/regUser_ext.html', dc_cont_err)
        

        return render(request, 'advuser/regUser_ext.html', dc_cont_err )
            
    else:   # Обработка создания профиля клиента
        type_status = type_status_user(user)
        if not type_status:
            return redirect_empty(arg_title='Статус', arg_mes='Нет данных статуса')           
        
        if type_status.levelperm == 10:
        
            form = Base_profForm()

            return render(request, 'advuser/regUser_ext.html', dict( 
                                parentuser=parentuser.username,
                                res=True,
                                error='',
                                title='Создание профиля', 
                                form=form
                                ))
        else:
            return redirect_empty(arg_mes='Нет прав. Только для гостевого входа')
            

def UpdProf_quest(request):
    """ Изменение профиля клиента самим пользователем """

    from .serv_advuser import type_status_user, Com_proc_advuser
   

    user = request.user 
    parentuser = Com_proc_advuser.get_user_cons(user)
    if parentuser is None:
        return redirect_empty(arg_mes='Наставник не определен')


    if request.method == 'POST':

        form = Base_profForm(request.POST)
        if form.is_valid():
            user = getUser(request.user)

            res_save = form.save_upd(user, parentuser)
            if res_save:  # успешное обновление 

                #Success_register_user заполнение cache 
                dict_cache = dict(username=res_save.any_str, mes=res_save.mes)
                cache.set('Success_register_user', dict_cache)

                return redirect('ver_profil')

            else:  # ошибка обработки 
                return render(request, 'advuser/regUser_ext.html', dict(
                            res=False,
                            parentuser=parentuser.username,
                            error= res_save.error,
                            title='Обновление профиля', 
                            form=form
                            ))

        else:  # Не прошла валидация данных
            return render(request, 'advuser/regUser_ext.html', dict(
                            res=False,
                            parentuser=parentuser.username,
                            error='Ошибка заполнения полей формы',
                            title= 'Обновление профиля' , 
                            form=form
                            ))
    
    else:
        # Проверка, кто делает запрос                
        type_status = type_status_user(user)
        if not type_status:
            return redirect_empty(arg_title='Статус', arg_mes='Нет данных статуса')
            
        from .modify_models import get_dictData_init_Form_regQuest

        if not (type_status.levelperm == 20):
            return redirect_empty(arg_mes='Только для зарегистрированных клиентов')

        dict_param = dict()

        if not Com_proc_advuser.get_advData_user(user, dict_param) :
            return redirect_empty(
                    arg_title='Отказ сервера', 
                    arg_mes='Нет данных для обработки' )
        
        dict_param = modf_data_dict(dict_param) # сброс значений '' or 'empty'
        form = Base_profForm(initial=dict_param)
            
        return render(request, 'advuser/regUser_ext.html', dict(
                        parentuser=parentuser.username,
                        res=True,
                        title='Редактор профиля', 
                        form=form
                        ))


"""
Используется для отображения результатов регистрации клиента на сайте
url: ver_profil/
"""
@login_required
def Success_register_user(request):    
    """ Подтверждение успешной регистрации """

    if 'Success_register_user' not in cache:
        return redirect('/')  # На случай, если делается попытка перезапуска
    
    dict_cache = cache.get('Success_register_user')
    user = dict_cache.get('username')
    mes  = dict_cache.get('mes')

    cache.delete('Success_register_user')
    
    prof = Com_proc_advuser.get_profil_user(user)
    if prof:
        cont = prof.res_dict
        cont.update(dict(mes=mes))
        return render(request, 'advuser/prof_conf_modf.html', cont)
    else:
        return redirect_empty(arg_title='Профиль')


"""
url:  listprofils
name: listprofils
------------------------
Табличная форма показа менеджеров

"""
""
@login_required
def List_profils(request):
    from .modify_models import get_list_prof_memb    
    from advuser.serv_typestatus import type_status_user

    user = request.user
    type_status = type_status_user(user)
    if type_status.levelperm < 40:
        return redirect_empty(arg_title='Уровень прав', arg_mes='Нет прав на просмотр данных')

    res_data_prof = get_list_prof_memb(user, arg_list=None)
    if res_data_prof is None:
        redirect_empty('Нет данных для просмотра')

    res_list = res_data_prof.res_list   
    if res_list is None:
        return redirect_empty(arg_title='Сообщение сервера', arg_mes='Нет данных построения списка')

    cont = dict(rows=res_list)

    return render(request, 'advuser/prof_table_format.html', cont)



@login_required
def Index(request):
    from .serv_typestatus import type_status_user
    
    return render(request, 'advuser/index.html')


# url из nltest.urls
# # path('profile/', Profile, name='profile' ),
@login_required
def Profile(request):    
    from .serv_advuser import Com_proc_advuser

    prof = Com_proc_advuser.get_profil_user(request.user)
    if prof:        
        if prof.res_obj.levelperm == 10:
            cont = dict(prof=prof.res_dict['prof'])

            return render(request,'advuser/prof_quest.html', cont )

        else:
            return render(request, 'advuser/profile_user.html', prof.res_dict)

    else:
        idmes = empty_mes.CreateEMPTY_mes(prof.error, 'Отказ сервера')
        return redirect('empty', mes=idmes)



"""
Перенаправление на редактирование профиля из списка 
url: updmesdata<str:mes>  name:updmesdata
"""
def Redir_upd_prof_listProf(request, mes):    
    """ Перенаправление на редактирование профиля из списка участников рукГруппы """
    user = request.user

    parentuser = Com_proc_advuser.get_user_cons(mes)
    if parentuser is None:
        return redirect_empty(arg_mes='Наставник не определен')

    if user.username != parentuser.username:
        return redirect_empty(arg_title='Права редактирования', arg_mes='Нет прав на редактирование профиля')

    #dict_cache = dict(username=mes)
    cache.set('Upd_prof_member', mes)

    return redirect ('updprofiluser')        


"""
Перенаправление 
    для доступа к редактированию профиля пользователя
"""
@login_required
def Redir_updprof(request):
    """ Перенаправление на редактПрофиля самими участниками проекта """

    from .serv_advuser import type_status_user

    user = request.user
    type_status = type_status_user(user)

    if type_status.levelperm == 10:        
        return redirect('addprofquest')    

    elif type_status.levelperm == 20:
        return redirect('updprofquest')

    else:
        # Обновление профиля участниками проекта
        cache.set('Upd_prof_member', user.username)
        return redirect('modf_prof_byuser')

