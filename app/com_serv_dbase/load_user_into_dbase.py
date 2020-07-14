"""
Загрузка пользователй в БД
Только на начальном этапе создания БД
"""

from app import (Res_proc, ErrorRun_impl, PM_run_raise as run_raise, 
                 PM_write_except_into_log as write_into_log)


def load_user_into_dbase(arg_dict:dict)->Res_proc:
    """ Начальная загрузка пользователй в БД """
    
    from django.contrib.auth.hashers import make_password 
    from app.use_mysql.conn_utils import getConnection
    from app import getPassword_cl, getLogin_cl
    import json

    res_proc = Res_proc();

    try:
        
        con = getConnection()
        s_dict = json.dumps(arg_dict, ensure_ascii=False)
        with con.cursor() as cur:
            cur.callproc('sp_adm_load_user_into_dbase', (s_dict,))
            res_call = cur.fetchall()[0];
            
            res_call = res_call['res']
            res_call_dc = json.loads(res_call)
                
            if res_call_dc['res'] == 'err':
                err = res_call_dc['mes']
                run_raise('Ошибки исходных данных: ' + err, showMes=True)

            res_data = res_call_dc['data']

            res_proc.res = True
            res_proc.mes = 'Создан профиль : ' + res_data['username']
            
        res_proc.res = True

    except Exception as ex:
        res_proc.error = ex;

    return res_proc;
    

