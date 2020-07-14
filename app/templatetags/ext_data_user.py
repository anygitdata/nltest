"""
Project AnyMixin 
Модуль  ext_data_user.py

Инициализация собстенных тэгов, используемых на страница сайта

"""


from django import template
from django.contrib.auth.models import User

register = template.Library()


@register.inclusion_tag('tags/tag_cons.html')
def cons_data(user):
    """ cons_user='',
        cons_full_name='', 
        cons_email='',
        cons_idcomp='',
        cons_phone=''    """

    from advuser.serv_advuser import Com_proc_advuser

    if not isinstance(user, User): return {}
    
    if user.is_superuser:
        return {}

    dataCons = Com_proc_advuser.get_dataCons(user)

    if not dataCons:
        dataCons = dict(
            full_name = 'Не определен',
            email = 'Нет',
            phone = 'Нет'
            )

    return dict(items=[
            dict(val=dataCons['full_name'], str='ФИО', item='full_name'),
            dict(val=dataCons['email'], str='email', item='email'),
            dict(val=dataCons['phone'], str='Телефон', item='phone')
        ])  


@register.inclusion_tag('tags/tag_cons.html')
def header_data():
    """
    header_user='',
                    cons_full_name='', 
                    cons_email='',
                    cons_idcomp='',
                    cons_phone=''
    """
    
    from advuser.serv_advuser import Com_proc_advuser

    try:

        advuser = Com_proc_advuser.get_advUser_header()    
        dataCons = Com_proc_advuser.get_dataUser(advuser.user)
        res = dict(
                typedata='header_data',
                items=[
                dict(val=dataCons['full_name'], str='ФИО', item='full_name'),
                dict(val=dataCons['email'], str='email', item='email'),
                dict(val=dataCons['phone'], str='Телефон', item='phone')
            ])
        
        return res

    except:
        return dict(
                typedata='header_data',
                items=[
                dict(val='Не определен', str='ФИО', item='full_name'),
                dict(val='Не определен', str='email', item='email'),
                dict(val='Не определен', str='Телефон', item='phone')
            ])  
   


@register.simple_tag
def user_data(user):
    """ Отображение полного имени входа """
    from app import getUser
    from advuser.serv_sprstatus import Com_proc_sprstatus    

    user = getUser(user)
    if isinstance(user, User):
        status = Com_proc_sprstatus.get_statusID_user(user)
        if status == 'qust-simp': return 'Гостевой вход'
        elif user.is_superuser: return 'superuser'

        else: return user.get_full_name()
    else:
        return 'data_user empty'



@register.inclusion_tag('tags/tag_head_panel.html')
def head_panel(user):
    """ отображение статуса """
    from app import getUser
    from advuser.serv_typestatus import type_status_user

    user = getUser(user)
    
    if user :
        _status =  type_status_user(user)
        res = dict(
            level = _status.levelperm
            )

        return res

    else: return 'data_head empty'
        

#@register.inclusion_tag('tags/tag_instr_for_user.html')
#def instr_for_user(user):
#    _status = type_status_user(user)
#    if _status.levelperm == 30:
#        return 