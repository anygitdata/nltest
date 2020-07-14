
from django.core.cache import cache
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required


"""
 Ajax  обработчик <script> ...</script> from  base_layout.html
 Обработка специальных сообщений через модальноеОкно в браузере
 key in dict for session:  system_send_mes
    Структура request.session['system_send_mes']:
        dict(title='Сессия', mes=s_mes, res='exists')
        res='exists' - идентификатор для отображения в диалоговом окне
        title='Сессия' заголовок сообщения
        mes=s_mes      строка сообщения
 url:  sendspecialmes
 name: sendspecialmes 
"""
def Send_special_message(request): 

    type_requery = request.method
    
    data = request.GET
    if data:
        # из Ajax параметр:  data = {type_mes:'system_send_mes'}
        # через GET параметры type_mes 
        type_mes = data.get('type_mes')
    else:
        type_mes = None
    
    dc = dict(res='empty')
    if type_mes == 'system_send_mes': # запрос на системные сообщения для отображения в браузере
        
        # Обработка системых сообщений, если они были 
        if 'system_send_mes' in request.session:
            dict_session = request.session.get('system_send_mes')

            title = dict_session.get('title') or 'Сообщение'
            mes   = dict_session.get('mes') or 'Сообщение empty'

            dc = dict(res='exists', title=title, mes=mes )

            # удаление данных по сообщению 
            del request.session['system_send_mes'] 

    return JsonResponse(dc, json_dumps_params=dict(ensure_ascii=False))


 #url: '/'   name=mainapp
@login_required
def index(request):
    from advuser.serv_typestatus import type_status_user

    #request.session.clear_expired()  # обнуление буфера session 
    status = type_status_user(request.user)
    cont_dc = dict(levelperm=status.levelperm)

    return render(request, 'app/index.html', cont_dc)


def logout(request):
    return render(request, 'registration/logout.html')


"""
url: name=emptyext   
/emptyext/
Контроллер empty с использованием cache
"""
def Empty_ext(request):
    cont = {}

    try:
        if cache.has_key('emptyext'):
            dict_cache = cache.get('emptyext')
            cont['title'] = dict_cache.get('title')
            cont['mes']   = dict_cache.get('mes')
            cache.delete('mepty_mes')
        else:
            cont['title'] = 'Отказано сервером'
            cont['mes']   = 'Сервер отклонил обработку сообщения'

        return render(request, 'app/empty_data.html', cont)

    except:
        return render(request, 'app/empty_data.html', cont)