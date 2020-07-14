"""
AnyMixin 

modul proc_send_email 

"""


from django.core.mail import send_mail
from django.http import HttpResponse

from .files import loadJSON_file_modf


# Процедура отправки простого элСообщения в виде уведомления 
def send_simpl_email(argDict=None):
    from nltest import settings

    """
    title заголовок сообщения
    mes   текст сообщения
    mes_from  от кого отправление
    to    адресат отправления сообщения
    -------------------------------------
    входящий формат параметра argDict
    templDict = dict(
        title='ПробноеСообщение',
        mes='Простое сообщение для проверки работы электронного канала',
        mes_from='Руководитель',
        to='surorion@mail.ru'
        )
    """

    # Это тестовый вариант
    # загрузить из файла json
    if not argDict:
        argDict = loadJSON_file_modf('AnyMixin/test_send_email')

    res = dict(res=False)

    emailFrom = '%s <%s>' % (argDict['mes_from'], settings.EMAIL_HOST_USER)

    try:
        res_mail = send_mail(argDict['title'], 
                             argDict['mes'], 
                             emailFrom, 
                             [argDict['to']], 
                             fail_silently=False )

        if res_mail: 
            res['res'] = True

    except Exception as ex:
        res['error'] = str(ex)

    return res

