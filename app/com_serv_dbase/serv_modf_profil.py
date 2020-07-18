"""
app.com_serv_dbase.serv_modf_profil
--------------------------------------------------------------
Сервис взаимодействия с БД на уровне хранимых процедур/функций
"""

from app.use_mysql.conn_utils import getConnection
from app import Res_proc, ErrorRun_impl, PM_run_raise as run_raise, getUser
import json
# from django.contrib.auth.models import User

def serv_add_profil (arg_dc:dict, serv_proc='sp_serv_add_profil'):
    """ Процедура взаимодействия с сервПроцедурой 
        общая процедура для создПрофиля через рукГруппой или через гостВХод  """

    
    from . .com_data.write_exception_into_log import PM_write_except_into_log as write_into_log
    
    res_proc = Res_proc()    
    s_error_not_show = 'verify#app.com_serv_dbase.serv_modf_profil.serv_add_profil'

    try:

        con = getConnection()
        s_dict = json.dumps(arg_dc, ensure_ascii=False)
        with con.cursor() as cur:
            cur.callproc(serv_proc, (s_dict,))
            res_call = cur.fetchall()[0];

            # возврат из сервПроцедуры в виде select {res:ok/err, mes:ok/strMessage} as res
            # {"mes": "Создан профиль: mysql_test", "res": "ok", "data": {"username": "mysql_test", "str_status": "Участник проекта"}}
            # {"mes": "Повторный ввод данных профиля: insert into auth_user", "res": "err"}
            res_call = res_call['res']
            res_call_dc = json.loads(res_call)
                
            if res_call_dc['res'] == 'err':   # элемент, созданный в процессе проверки входящих данных 
                err = None
                if res_call_dc.get('err'):
                    err = res_call_dc['err']    
                else:
                    err = res_call_dc['mes_error']  # элемент, который используется в блоке обработчика исключений сервПроцедуры 
            
                write_into_log(s_error_not_show, res_call_dc['mes_error'] );
                run_raise('Ошибки исходных данных', showMes=True)

            res_data = res_call_dc['data']

            res_proc.res = True
            res_proc.any_str = res_data['username']   
            if serv_proc == 'sp_serv_add_profil':
                res_proc.mes = 'Создан профиль со статусом: ' + res_data['str_status']
            else:
                res_proc.mes = 'Изменен профиль со статусом: ' + res_data['str_status']


    except Exception as ex:
        res_proc.error = ex

    return res_proc


def sp_modf_data (arg_dc:dict, serv_proc='sp_serv_add_profil'):
    """ Процедура взаимодействия с сервПроцедурой 
    Общая для ВСЕх операций взаимодействия с БД
    """
    
    from . .com_data.write_exception_into_log import PM_write_except_into_log as write_into_log
    
    res_proc = Res_proc()    
    s_error_not_show = 'verify#app.com_serv_dbase.serv_modf_profil.sp_modf_data'

    try:

        con = getConnection()
        s_dict = json.dumps(arg_dc, ensure_ascii=False)
        with con.cursor() as cur:
            cur.callproc(serv_proc, (s_dict,))
            res_call = cur.fetchall()[0];

            # возврат из сервПроцедуры в виде select {res:ok/err, mes:ok/strMessage} as res
            # {"mes": "Создан профиль: mysql_test", "res": "ok", "data": {"username": "mysql_test", "str_status": "Участник проекта"}}
            # {"mes": "Повторный ввод данных профиля: insert into auth_user", "res": "err"}
            res_call = res_call['res']
            res_call_dc = json.loads(res_call)
                
            if res_call_dc['res'] == 'err':   # элемент, созданный в процессе проверки входящих данных 
                err = None
                if res_call_dc.get('err'):
                    err = res_call_dc['err']    
                else:
                    err = res_call_dc['mes_error']  # элемент, который используется в блоке обработчика исключений сервПроцедуры 
            
                write_into_log(s_error_not_show, res_call_dc['mes_error'] );
                run_raise('Ошибки исходных данных', showMes=True)

            res_data = res_call_dc['data']
            dc = dict(mes=res_call_dc['mes'], data_mes=res_data['mes'] )

            res_proc.res = True
            res_proc.res_dict = dc


    except Exception as ex:
        res_proc.error = ex

    return res_proc


def serv_get_data_prof(arg_user, str_levelperm=None):
    """ Выборка данных профиля для отображения в виде списка пользователй проекта
        Предназначено для рукПроекта
    """

    from . .com_data.write_exception_into_log import PM_write_except_into_log as write_into_log

    
    res_proc = Res_proc()    
    s_error_not_show = 'verify#app.com_serv_dbase.serv_modf_profil.serv_add_profil'
        
    user = getUser(arg_user)

    try:
        con = getConnection()
        if str_levelperm is None:
            str_levelperm = '30,40,70'

        dc_arg = dict(username=user.username, lstlevelperm=str_levelperm )
        s_dict = json.dumps(dc_arg, ensure_ascii=False)
        lst_res = []

        with con.cursor() as cur:
            cur.callproc('sp_serv_dataprof', (s_dict,))
            res_call = cur.fetchall();
            res_proc.res_list = res_call
            res_proc.res = True

    except Exception as ex:
        res_proc.error = ex

    return res_proc


def user_upd_psw (arg_dc:dict)->Res_proc:
    from . .com_data.write_exception_into_log import PM_write_except_into_log as write_into_log
    
    s_error_not_show = 'verify#app.com_serv_dbase.serv_modf_profil.serv_add_profil'
    res_proc = Res_proc()    

    try:
        con = getConnection()
        s_dict = json.dumps(arg_dc, ensure_ascii=False)
        with con.cursor() as cur:
            cur.callproc('sp_user_upd_psw', (s_dict,))
            res_call = cur.fetchall()[0]
            
            # {"res": "err", "mes_error": "текст сообщений ошибки"}
            # {"mes": "Обновление пароля: XEMP-9069", "res": "ok", "data": {"username": "XEMP-9069"}}
            res_call = res_call['res']
            res_call_dc = json.loads(res_call)
                
            if res_call_dc['res'] == 'err':   # элемент, созданный в процессе проверки входящих данных 
                write_into_log(s_error_not_show, res_call_dc['mes_error'] );
                run_raise('Ошибки исходных данных', showMes=True)                

            res_data = res_call_dc['data']

            res_proc.res = True
            res_proc.any_str = res_data['username']   
            
            res_proc.mes = 'Изменен пароль: ' + res_data['username']



    except Exception as ex:
        res_proc.error = ex
    
    return res_proc
        
