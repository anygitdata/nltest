
"""
Тестирование использования серверверных процедур


    try:
        res = ['test## ']

        return res
    except Exception as ex:
        return str(ex)

"""

import json


# создание json для app_spr_fields_models
def test_create_json_fields_models():
    try:
        res = ['test_create_json## ']

        js_data = dict(
            info='Структура модели advdata статус subheader',
            permKeys=["user", "advuser", "advdata_proj_memb", "advdata_subheader", "advdata_headerexp", "advdata_qust_simp", "advdata_qust_regs"],
            type_upd=dict(
                info='Дополнительные параметры',
                add=["password_cl"],
                upd=[]
                )
            )

        res.append(json.dumps(js_data, ensure_ascii=False))

        return res
    except Exception as ex:
        return str(ex)


def test_con_mysql():
    from app.com_data.type_value import Type_value
    from app import loadJSON_withTempl
    from django.contrib.auth.hashers import make_password
    from app.com_data.any_mixin import getLogin_cl, getPassword_cl

    from app.use_mysql.conn_utils import getConnection

    try:
        res = ['test_con_mysql## ']
        file = 'advuser/arg_RegisterIns_profForm_member'
        path = Type_value.init_formatTempl(file,'jsn')


        dict_arg = loadJSON_withTempl(path)
        pswcl = 'earth' # взято из advData user test_podg
        logincl = getLogin_cl()
        dict_arg.update(
            dict(
               parentuser = 'test_podg',
               password = make_password(dict_arg['password']),
               password_cl = make_password(pswcl),
               logincl = logincl,
               pswcl = pswcl,
               full_name= dict_arg['first_name'] + ' ' + dict_arg['last_name'],
               is_active='true',
               status_id= dict_arg.get('status')
                )
            )

        con = getConnection()

        try:
            s_dict = json.dumps(dict_arg, ensure_ascii=False)
            with con.cursor() as cur:
                cur.callproc('sp_serv_verf_params_arg_ext', (s_dict,))
                res_call = cur.fetchall()[0];
                                
                # select res возврат из сервПроцедуры
                res.append(res_call['res'])  # этот идентиф. res исп. в dictResult

        except Exception as ex:
            res.append(str(ex))

        finally:
            con.close()

        # --------- завершение обработки обращения к БД -----------
        return res
    except Exception as ex:
        return str(ex)


def test_init_templ_json():
    from app.com_data.type_value import Type_value
    from app import loadJSON_withTempl
    from django.contrib.auth.hashers import make_password
    from app.com_data.any_mixin import getLogin_cl, getPassword_cl

    try:
        res = ['test_init_templ_json## ']
        file = 'advuser/arg_RegisterIns_profForm_member'
        path = Type_value.init_formatTempl(file,'jsn')


        pswcl = 'earth' # взято из advData user test_podg
        logincl = getLogin_cl()
        dict_arg = loadJSON_withTempl(path)
        dict_arg.update(
            dict(
               parentuser = 'test_podg',
               password = make_password(dict_arg['password']),
               password_cl_ = make_password(pswcl),
               logincl = logincl,
               pswcl = pswcl,
               full_name= dict_arg['first_name'] + ' ' + dict_arg['last_name'],
               is_active='true'
                )
            )

        res.append(json.dumps(dict_arg, ensure_ascii=False))

        return res
    except Exception as ex:
        return str(ex)


def test_create_prof():
    from django.contrib.auth.hashers import make_password
    from app.use_mysql.conn_utils import getConnection
    from app.com_data.any_mixin import getLogin_cl, getPassword_cl
    import json

    try:
        res = ['Подключение в БД mysq## ']

        #psw = make_password('test')
        #res.append(psw)
  
    
        con = getConnection()

        try:

            with con.cursor() as cur:

                if 1>2:
                    # хранПРоцедура завершается оператором select * from TEMPORARY table
                    cur.callproc('sp_row_advdata', (380,))

                    for row in cur:  # вывод данных из хранПроцедуры
                        res.append( f"{row['id_key']} {row['js_key']} {row['js_val']} ##" )

                # Создание dict для вставки нового профиля
                dc_all = dict(
                    username='test_sp_proc',
                    password=make_password('test'),
                    first_name='Имя_профиль',
                    last_name='Фам_профиль',
                   
                    ageGroup=65,
                    status_id='proj-memb',
                    status='proj-memb',
                    pol='М',
                
                    idcomp= "038-77-test",
                    logincl= getLogin_cl(),
                    pswcl= getPassword_cl()                    
                    
                    )
                res.append( json.dumps(dc_all, ensure_ascii=False))
                

        except Exception as ex:
            res.append(str(ex))

        finally:
            con.close()

        return res
    except Exception as ex:
        return str(ex)