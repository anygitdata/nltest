"""
app.com_data.writ_exeption_into_log
---------------------------------------------------------------
Вынесенный модуль для обработки сообщений ошибок в журнал *.log
"""


"""
arg_mes: строка, место в коде возникновения исключения
arg_except: само сообщение исключения
"""
def PM_write_except_into_log(arg_mes, arg_except):
    """ Процедура на уровне модуля app.com_serv_dbase.serv_modf_profil
        Запись текста исключения в журнал *.log 
        ----------------------------------------------------------------
        arg_mes базовая строка для конфигурирования строки журнала *.log
        arg_except  строка детализации сообщения  """

    from app import TypeError_system, ErrorRun_impl
    
    """ тип и уровень сообщения определяется в arg_mes: verify, ValueError, SyntaxError, ...
        на пример: SyntaxError##текст сообщения исключения """
    s_mes = '{0} {1}'.format(arg_mes, arg_except)
    TypeError_system(ErrorRun_impl(s_mes))  # запись в файл app/loggin/*.log



def PM_run_raise(s_arg, showMes=None):
    """ Обработчик исключения в структуре кода 
    s_arg сообщение исключения
    showMes=True  -> сообщение будет использовано для браузера
    showMEs=False -> ErrorRun_impl данные будут записаны в журнал 
        через цепочку присвоения res_proc.error=ErrorRun_impl -> TypeError_system(value)
        поэтому s_arg д/быть сформирован с учетом формата сообщПомещяемых в *.log
    """

    from app import ErrorRun_impl

    s_err = 'встраиваемый шаблон'

    if showMes:            
        raise ErrorRun_impl('verify##{0}'.format(s_arg))
    else:
        raise ErrorRun_impl('{0} {1}'.format(s_err, s_arg))