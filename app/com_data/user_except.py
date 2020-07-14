"""
app.app_exp

modul: user_except

Модуль исключений 
"""


class ErrorRun_impl(Exception):

    class Lever_err:

        _levelError = dict(verify=10, debug=20, 
                           NotData=30, ResError=30, ValueError=30, TypeError=30, SyntaxError=30,
                           SystemError=50, high=100)

        # Минимально допустимый уровень исключения для отображения error into browser
        # используется для свойства __bool__
        _minLevel = 10  

        # Инициализация объекта Lever_err
        def __init__(self, arg_level):
            self.num_level = None
            self.key_level = None


            if isinstance(arg_level, str):
                arg_level = arg_level.strip()

                if self._levelError.get(arg_level):
                    self.num_level = self._levelError[arg_level]
                    self.key_level = arg_level
                else:
                    self.num_level = self._levelError['high']
                    self.key_level = 'high'

            else:
                _class = arg_level.__class__.__name__
                if self._levelError.get(_class):
                    self.num_level = self._levelError[_class]
                    self.key_level = _class
                else:
                    self.num_level = self._levelError['high']
                    self.key_level = _class
            


        @property
        def PR_keyError(self):
            s_err = self.key_level
            return s_err


        def __str__(self):
            s_err = 'keyLevel:{0}  numLevel:{1}'.format(self.key_level, self.num_level)
            return s_err

        @property
        def PR_levelError(self):
            if self.num_level> self._minLevel : return True
            else: return False

    # **************************************************************************

    # Инициализация объекта ErrorRun_impl
    def __init__(self, arg_error):
        self.error = None      # сообщение error для browser or file.log
        self.typeError = None  # строковый идентификатор error
        self.levelError = None # уроверь error  -> объект типа Lever_err

        s_type = type(arg_error).__name__
        if s_type == 'str': # есть ли '##' - форматер сообщения
            inx = arg_error.find('##')
            if inx>-1:
                self.levelError = self.Lever_err(arg_error[:inx])
                self.typeError = self.levelError.PR_keyError
                self.error = arg_error[inx+2:]               
            else:
                self.levelError = self.Lever_err(arg_error)
                self.typeError = self.levelError.PR_keyError
                self.error = arg_error

        elif s_type == 'ErrorRun_impl':
            self.levelError = arg_error
            self.typeError = self.levelError.PR_keyError
            self.error     = arg_error.PR_error           
                
        else:                
            self.levelError = self.Lever_err(arg_error)
            self.typeError = self.levelError.PR_keyError
            self.error = str(arg_error)


    def __str__(self):
        res = '{0}  err:{1}'.format(str(self.levelError), self.error)

        return res
        

    @property
    def PR_error(self):
        return self.error

    # критерий вывод в файл *.log
    @property
    def PR_levelError(self):
        return self.levelError.PR_levelError

    @property
    def PR_numError(self):
        return self.levelError.num_level

    @property
    def PR_keyError(self):
        return self.typeError


    # Какое сообщение поступит в Res_proc
    # если уровень больше допустимого -> из PR_mes_browser
    # иначе фактическое сообщение self.error
    @property
    def PR_error_forRes_proc(self):
        if self.PR_levelError: 
            return self.PR_mes_browser
        else: return self.PR_error

    @property
    def PR_mes_browser(self):
        if self.PR_levelError: return 'Закрыт доступ к базе данных'
        else: return self.error


