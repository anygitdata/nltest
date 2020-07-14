
"""
prtesting.tests.app

modul: test_app_models


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




# Тестирование class Type_status_user
# file: tests/advuser/modl_serv/test_sprstatus_serv.json
def test_type_status_user():
    from advuser.serv_typestatus import type_status_user

    try:
        res = []

        type_status = Type_status_user.type_status('podg-vl')

        if type_status:
            res.append(str(type_status))
        else:
            res.append(type_status.error)

        return res
    except Exception as ex:
        return str(ex)



