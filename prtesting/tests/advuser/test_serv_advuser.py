
"""
prtesting.tests.app

modul: test_app_models


 Шаблон для тестовых процедур
    --------------------------------------------------------------

    from AnyMixin.files import writeDict_into_JSON, conv_strPath

    s_json = Type_value.init_formatTempl(s_path, 'jsn')
    js_arg = loadJSON_withTempl(s_json)


    try:
        res = ['test## ']

        return res
    except Exception as ex:
        return str(ex)

"""

from app import getUser
from advuser.serv_advuser import Com_proc_advuser as serv_advUser


def test_spr_status():
    from advuser.serv_sprstatus import Com_proc_sprstatus

    try:
        res = ['test_spr_status## ']

        res_proc = Com_proc_sprstatus.get_status_qust_regs().pk;


        res.append(res_proc)

        return res
    except Exception as ex:
        return str(ex)


def test_get_profil_user_for_teg():
    from advuser.serv_advuser import Com_proc_advuser

    try:
        res = ['test_get_profil_user_for_teg## ']

        user = getUser('mysql_test');

        profil_user = Com_proc_advuser.get_profil_user_for_teg
        res_proc = profil_user(user)  # выборка данных нормально 

        return res
    except Exception as ex:
        return str(ex)


# file: test_serv_advuser_next
def test_get_profil_user():
    from advuser.serv_advuser import Com_proc_advuser

    try:      
        res = ['test_get_profil_user## ']

        user = getUser('mysql_test');

        profil_user = Com_proc_advuser.get_profil_user
        res_proc = profil_user(user)  # выборка данных нормально 


        return res
    except Exception as ex:
        return str(ex)


def test_get_val_from_advData():
    try:
        res = ['get_val_from_advData## ']

        lst = ('idcomp','username','pswcl','status', 'limitcon')
        user = 'VFPF-2736'
        get_val_from_advData = serv_advUser.get_val_from_advData

        for v in lst:
            res_val = get_val_from_advData(user, v)
            if res_val:
                res.append(f'{v}: {res_val}')
            else:
                res.append(f'{v} нет данных')


        return res
    except Exception as ex:
        return str(ex)


def test_get_parentuser():
    try:
        res = ['get_parentuser## ']

        get_parentuser = serv_advUser.get_parentuser

        lst = ('suadm','podg-vl','NSZZ-9347','FDUF-8247')

        for item in lst:
            res_parentuser = get_parentuser(item)
            if res_parentuser:
                res.append(f'{item} parentuser:{res_parentuser.any_str}')
            else:
                res.append(f'{item}   error:{res_parentuser.error} ')


        return res
    except Exception as ex:
        return str(ex)


#file: test_serv_advuser
def test_get_dataCons():

    try:
        res = ['get_dataCons## ']

        get_dataCons = serv_advUser.get_dataCons

        res_data = get_dataCons('suadm')
        if res_data:
            res.append(res_data)
        else:
            res.append('Нет данных для консультанта')


        return res
    except Exception as ex:
        return str(ex)


#file: test_serv_advuser
def test_get_dataHeader():

    try:
        res = ['get_dataHeader## ']

        get_dataHeader = serv_advUser.get_dataHeader

        res_dict = get_dataHeader()
        if res_dict:
            res.append(f'{res_dict}')
        else:
            res.append('Нет данных для рукПроекта')

        #-----------------------------------------------

        res_dict = get_dataHeader(modf_form=True)
        if res_dict:
            res.append(f'## {res_dict}')
        else:
            res.append('Нет данных для рукПроекта')


        return res
    except Exception as ex:
        return str(ex)


#file: test_serv_advuser
def test_verify_yourHead():
    try:
        res = ['verify_yourHead## ']

        verify_yourHead = serv_advUser.verify_yourHead

        arg_user = 'NSZZ-9347'
        arg_head = 'podg-vl'
        res_ver = verify_yourHead(arg_user, arg_head)

        if res_ver:
            res.append(f'{arg_head} is header for {arg_user} ')
        else:
            res.append(f'error:{res_ver.error}')
    
        return res
    except Exception as ex:
        return str(ex)


#file: test_serv_advuser
def test_get_subRows_head():
    try:
        res = ['get_subRows_head ## ']

        get_subRows_head = serv_advUser.get_subRows_head

        res_list = get_subRows_head('test_podg')
        if res_list:
            res.append(res_list.res_list)
        else:
            res.append(f'error:{res_list.error}')

        return res
    except Exception as ex:
        return str(ex)


#file: test_serv_advuser
def test_get_dataUser():

    try:
        res = ['test## ']

        get_dataUser = serv_advUser.get_dataUser

        lst = ('POB-7787',84,'suadm', 'suadm_')
        #for user in lst:
        #    res.append(get_dataUser(user))


        res_dict = {}
        if serv_advUser.get_advData_user('lolga', res_dict):
            res.append(res_dict)
        else:
            res.append('Возврат False')


        res_dict = {}
        if serv_advUser.get_advData_user('test_podg', res_dict, modf_form=True):
            res.append(res_dict)
        else:
            res.append('Возврат False')


        return res
    except Exception as ex:
        return str(ex)


#file: test_serv_advuser
def test_get_advData():


    try:
        res = ['test get_advData## ']

        get_advData = serv_advUser.get_advData

        res_dict = get_advData('CZV-8115')
        res.append(res_dict)

        res_dict = get_advData('CZV-8115', modf_form=True)
        res.append(res_dict)

        return res
    except Exception as ex:
        return str(ex)


#file: test_serv_advuser
def test_modf_dict_by_setting_def():
    from advuser.serv_advuser import modf_dict_by_setting_def as modf_dict

    try:
        res = ['test modf_dict_by_setting_def## ']

        dc_test = {"phone": "79185404662", "ageGroup": 65, "post": 347900, "pol": "Ж", "status_id": "proj-memb", "parentuser": "podg-vl", "idcomp": "007-3200", "sendMes": "true", "logincl": "CZV-LOG-01", "pswcl": "region", "is_acitve": "true", "user_id": 76, "full_name": "Галина Егорова", "email": "grafika1946@mail.ru", "last_name": "Егорова", "username": "egorova", "first_name": "Галина", "is_active": "true"}

        res_modf = modf_dict(dc_test)

        res.append(dc_test)


        return res
    except Exception as ex:
        return str(ex)


#file: test_serv_advuser
def test_get_advUser_header():
    try:
        res = ['test get_advUser_header## ']

        get_advUser_header = serv_advUser.get_advUser_header

        res_advuser = get_advUser_header()
        
        res.append('user:{0} из структуры advuser'.format( res_advuser.user.username))

        return res
    except Exception as ex:
        return str(ex)


#file: test_serv_advuser
def test_get_user_head():

    try:
        res = ['test get_user_head## ']

        get_user_head = serv_advUser.get_user_head

        res_head = get_user_head()
        
        res.append(res_head.username)

        return res
    except Exception as ex:
        return str(ex)


# file: test_serv_advuser.json
def test_get_head_user():

    try:
        res = ['test_get_head_user##### ']

        get_head_user = serv_advUser.get_head_user

        lst_user = ('suadm','pradm','podg-vl','CZV-8115','kisl', 'memb_1','NSZZ-9347',  395)

        for user in lst_user:
            res_proc = get_head_user(user)
            if res_proc:
                user_head = res_proc.res_model
                res.append('user:{0} headerUser:{1} #####'.format(user, user_head.username))
            else:
                res.append('{0} нет данных для parentuser'.format(user))


        return res
    except Exception as ex:
        return str(ex)


# file: test_serv_advuser.json
def test_get_user_cons():     

    try:
        res = ['test## ']
            
        lst_user = ('suadm','pradm','podg-vl','CZV-8115','kisl', 'memb_1',389,  395)

        res.append('testing Com_proc_advuser.get_user_cons #####')
        get_user_cons = serv_advUser.get_user_cons
        for user in lst_user:
            res_proc = get_user_cons(user)
            if res_proc:
                res.append('user:{0} parentuser:{1} #####'.format(user, res_proc.username))
            else:
                res.append('{0} нет данных для parentuser'.format(user))

        return res
    except Exception as ex:
        return str(ex)


