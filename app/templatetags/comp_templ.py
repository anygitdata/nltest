

from django import template
from app import ErrorRun_impl

register = template.Library()

# Отображение контента гостевого входа
@register.inclusion_tag('tags/tag_comp_prof_quest.html')
def templ_quest(prof):
    return dict(prof=prof)


# Отображение контента профиля
@register.inclusion_tag('tags/tag_comp_prof_title.html')
def templ_title(param):
    cont = dict(param=param)
    return cont

# Отображение контента наставника и рукПроекта
@register.inclusion_tag('tags/tag_comp_prof_head.html')
def templ_head(prof):
    cont = dict(prof=prof)
    return cont


# Отображение контента руководителя группы при создании профиля
@register.inclusion_tag('tags/tag_comp_prof_parentuser.html')
def templ_parentuser(user):
    from advuser.serv_typestatus import type_status_user
    from app import getUser

    user = getUser(user)
    data_parentuser = type_status_user(user).get_data_parentuser(user)
    cont = {}
    if data_parentuser:
        cont = dict(parentuser= data_parentuser)

    return cont
