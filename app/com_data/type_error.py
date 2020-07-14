"""
app.app_exp

modul: TypeError
"""



"""
testing:
    file: tests/app/test__class_TypeError_system.json
    modul: test_app
    procedure: test__TypeError_system
"""
class TypeError_system:
    import datetime
    import os
    from .user_except import ErrorRun_impl
    

    #Каталог размещения *.log
    @classmethod
    def _get_pathLoggin(cls):
        from app.com_data.spr_setting_serv import serv_loggin

        file_log = serv_loggin.get_actual_logginFile()

        baseDir_loggin = cls.os.path.dirname(cls.os.path.dirname(cls.os.path.abspath(__file__)))
        s_path = cls.os.path.join(baseDir_loggin, 'loggin', file_log)

        return s_path

    @property
    def PR_mes_forLoggin(self):
        return self.exception.error

    @property
    def PR_mes_browser(self):
        return self.exception.PR_mes_browser


    @property
    def PR_error(self):
        return self.exception.PR_error_forRes_proc
    
    @property
    def PR_typeError(self): return self.exception.levelError.PR_keyError


    def __bool__(self): 
        if self.exception.levelError: return True
        else: return False


    def __str__(self):
        res = str(self.exception)
        #'{0}: {1}'.format(self.PR_typeError, self.PR_error )
        return res


    """
    testing:
        file: tests/app/test__class_spr_fields_models_advdata.json
        modul: test.app.test_app
        procedure: test__spr_fields_models_advdata
    """
    def _error_to_file(self):        
        
        s_write = '{0}: {1} ERROR:{2}'.format( str(self.exception.levelError), self.PR_typeError, self.PR_mes_forLoggin)        

        # ----------------- Запись в файл *.log ----------------------
        today = self.datetime.datetime.today()
        s_datetime = today.strftime("%d.%m.%Y %H:%M:%S")

        s_path = self._get_pathLoggin()
        s_write_file = '{0} {1}\n'.format(s_datetime, s_write)
        with open ( s_path, 'a', encoding='utf-8') as file:            
            file.writelines(s_write_file)


    """
    Информация о типе ошибки
    str_error включает форматер: typeError##текстовое сообщение
    """
    def __init__(self, arg_except):        
        self.exception = None

        if  isinstance(arg_except, self.ErrorRun_impl):
            self.exception = arg_except
        else:
            self.exception = self.ErrorRun_impl(arg_except)
        
        # если уровень исключения превышает допустимое значение -> вывод сообщФайл
        # допустимый уровень определяется ErrorRun_impl.Lever_err
        if self.exception.PR_levelError:
            self._error_to_file()


   