
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


# file: test_sprstatus_serv
def test_simpl_proc():
    from advuser.serv_sprstatus import Com_proc_sprstatus as serv_status

    try:
        res = ['test## ']

        get_statusID_user = serv_status.get_statusID_user

        lst = ('suadm','podg-vl','kisl','')

        res.append('testing get_statusID_user: ')
        for item in lst:
            res_proc = get_statusID_user(item)
            res.append('user:{1} statusID:{0} ##'.format(res_proc, item or 'empty' ))


        # ---------- тестирование процедур без параметров ----------------

        get_status_qust_simp = serv_status.get_status_qust_simp
        res_status = get_status_qust_simp()
        if res_status:
            res.append( '##result get_status_qust_simp -> {0} %%%%%'.format(res_status.PR_strStatus) )
        else:
            res.append('get_status_qust_simp нет данных')


        get_status_qust_regs = serv_status.get_status_qust_regs
        res_status = get_status_qust_regs()
        if res_status:
            res.append( '##result get_status_qust_regs -> {0}'.format(res_status.PR_strStatus) )
        else:
            res.append('get_status_qust_regs нет данных')

        get_status_header = serv_status.get_status_header
        res_status = get_status_header()
        if res_status:
            res.append( '##result get_status_header -> {0}'.format(res_status.PR_strStatus) )
        else:
            res.append('get_status_header нет данных')

        get_status_pradm = serv_status.get_status_pradm
        res_status = get_status_pradm()
        if res_status:
            res.append( '##result get_status_pradm -> {0}'.format(res_status.PR_strStatus) )
        else:
            res.append('get_status_pradm нет данных')

        get_status_suadm = serv_status.get_status_suadm
        res_status = get_status_suadm()
        if res_status:
            res.append( '##result get_status_suadm -> {0}'.format(res_status.PR_strStatus) )
        else:
            res.append('get_status_suadm нет данных')

        get_status_notstatus = serv_status.get_status_notstatus
        res_status = get_status_notstatus()
        if res_status:
            res.append( '##result get_status_notstatus -> {0}'.format(res_status.PR_strStatus) )
        else:
            res.append('get_status_notstatus нет данных')

            

        return res
    except Exception as ex:
        return str(ex)


# Тестирование modul advuser.serv_sprstatus
# file: tests/advuser/modl_serv/test_sprstatus_serv.json
def test_getStatus_or_None():
    from advuser.serv_sprstatus import Com_proc_sprstatus, serv_SprStatus, getStatus_or_None
    from app import getUser

    try:
        res = ['Testing Com_proc_sprstatus## ']
        
        user = getUser('podg-vl')
        getStatus = Com_proc_sprstatus.getStatus_or_None


        res_status = getStatus_or_None(user)
        if res_status:
            res.append(str(res_status))
        else:
            res.append('Статус не определен')


        # ---------- тестирование через процедуру-диспетчер ------------

        # тестирование через arg_status
        res_serv = serv_SprStatus('getStatus_or_None', user)
        if res_serv:
            res.append(res_serv.PR_strStatus)
        else:
            res.append('serv_SprStatus: статус не определен')


        # тестирование через модель AdvUser
        res_serv = serv_SprStatus('getStatus_or_None', getUser('basam').advuser)
        if res_serv:
            res.append('##' + res_serv.PR_strStatus+ '##')
        else:
            res.append('serv_SprStatus: статус не определен')


        # тестирование через аргумент dict
        arg = dict(username='suadm')
        res_serv = serv_SprStatus('getStatus_or_None', **arg)
        if res_serv:
            res.append(res_serv.PR_strStatus)
        else:
            res.append('serv_SprStatus: статус не определен')

        # тестирование через строковый идентификатор status_id
        res_serv = serv_SprStatus('getStatus_or_None', 'proj-sadm')
        if res_serv:
            res.append(res_serv.PR_strStatus)
        else:
            res.append('serv_SprStatus: статус не определен')

        # тестирование через строковый идентификатор status_id
        arg = dict(statusID='proj-memb')
        res_serv = serv_SprStatus('getStatus_or_None', **arg)
        if res_serv:
            res.append(res_serv.PR_strStatus)
        else:
            res.append('serv_SprStatus: статус не определен')

            
        # тестирование выброса исключения и записи в файл *.log
        arg = dict(statusID='proj-memb', username='pradm_')
        res_serv = serv_SprStatus('getStatus_or_None', user, **arg)
        if res_serv:
            res.append(res_serv.PR_strStatus)
        else:
            res.append('serv_SprStatus: статус не определен')


        ## тестирование приоритетности
        #arg = dict(statusID='proj-memb')
        #res_serv = serv_SprStatus('getStatus_or_None', 'qust-simp', **arg)
        #if res_serv:
        #    res.append(str(res_serv))
        #else:
        #    res.append('serv_SprStatus: статус не определен')

        # тестирование приоритетности
        arg = dict(statusID='proj-memb')
        res_serv = serv_SprStatus('getStatus_or_None', 'qust-simp', **dict(statusID='proj-memb'))
        if res_serv:
            res.append(res_serv.PR_strStatus)
        else:
            res.append('serv_SprStatus: статус не определен')


        # тестирование выбороса исключения через параметр statusID
        res_serv = serv_SprStatus('getStatus_or_None', 'qust-simp_')
        if res_serv:
            res.append(res_serv.PR_strStatus)
        else:
            res.append('serv_SprStatus: статус не определен ')



        #res_serv = getStatus_or_None(**dict(statusID='proj-memb'))
        #if res_serv:
        #    res.append(str(res_serv))
        #else:
        #    res.append('serv_SprStatus: статус не определен')

        res_serv = getStatus_or_None('proj-memb')
        if res_serv:
            res.append('## ' + res_serv.PR_strStatus)
        else:
            res.append('serv_SprStatus: статус не определен')


        return res
    except Exception as ex:
        return str(ex)



def test_get_permModf_prof():
    from advuser.serv_sprstatus import get_permModf_prof
    from app import getUser

    try:
        res = []

        user = 'colch'

        # список доступных значений из SprStatus.pk
        lst_status = ('notstatus','qust-simp','qust-regs','proj-sadm','proj-memb','proj-head','subheader','headerexp')

        for item in lst_status:
            res_prof = get_permModf_prof(user, 'upd_{0}'.format( item) )
            if res_prof:
                res.append('# {0} ##'.format( str(res_prof.res_obj)))
            else:
                res.append('{0} {1}: права не определены'.format(user, item))

        return res
    except Exception as ex:
        return str(ex)
