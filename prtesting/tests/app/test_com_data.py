
"""
prtesting.tests.app

modul: test_com_data


 Шаблон для тестовых процедур
    --------------------------------------------------------------

    from AnyMixin.files import writeDict_into_JSON, conv_strPath

    s_json = Type_value.init_formatTempl(s_path, 'jsn')
    js_arg = loadJSON_withTempl(s_json)


    try:
        res = []

        return 'ok'
    except Exception as ex:
        return str(ex)

"""


def test_getUser():
    from app import getUser

    try:
        res = []

        user = getUser('podg-vl')
        if user is None:
            res.append('Не определен')
        else:
            res.append(user.get_full_name())

        user = getUser(80)
        if user is None:
            res.append('Не определен')
        else:
            res.append(user.get_full_name())

        user = getUser(user)
        if user is None:
            res.append('Не определен')
        else:
            res.append(user.get_full_name())


        return res
    except Exception as ex:
        return str(ex)


# file tests/app/com_data/test_res_proc.json
# Тестирование базового class Res_proc
def test_res_proc():
    from app import Res_proc
    from app import ErrorRun_impl

    try:
        res = []
               

        res_proc = Res_proc()
        s_empty = res_proc.PR_empty
        res_proc.any_str = s_empty
        res_proc.res_dict = dict(par=1)
        res_proc.res_list = [1,2]

        val_dict = res_proc.FN_get_val_dict(dict(par='anyDataDict'), 'par') 
        res.append(val_dict + '; ')

        s_proc = '{0} {1} {2}'.format(res_proc.FN_empty(), res_proc.FN_exist(), res_proc.PR_notRecord )
        res.append('## ' + s_proc)

        res_proc.error = ErrorRun_impl('ValueError##Пробное исключение')

        s_res = str(res_proc)

        res.append(s_res)


        return res
    except Exception as ex:
        return str(ex)