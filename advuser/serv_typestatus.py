from app.com_data.any_mixin import getUser, Res_proc
from app import TypeError_system, ErrorRun_impl



"""
Процедура для выборки и анализа значения из SprStatus
    arg_init используется для инициализации объекта SprStatus
result  object Type_status_user
"""  
def type_status_user(arg_user):
    """ Процедура для выборки и анализа значений из SprStatus 
        arg_user -> User or username or иной объект, представлющий User
        return  object Type_status_user """

    def _run_raise(s_arg, showMes=None):
        s_err = 'advuser.serv_typestatus.type_status_user'

        if showMes:            
            raise ErrorRun_impl('verify##{0}'.format(s_arg))
        else:
            raise ErrorRun_impl('{0} {1}'.format(s_err, s_arg))

    #-------------------------------------------------------------

    from .serv_sprstatus import Com_proc_sprstatus        
    import json

    """
     Вспомогательный клас для выборки и логического сравнения поля AdvUser.status
     Базовый класс для Type_status_userExt
     Используется для многократного определения статуса в коде
     -----------------------------------------------------------
     return  Type_status_user.type_status(user) -> object Type_status_user

    """
    class Type_status_user:
        import json         


        def __init__(self):
            self.error        = None
            self.status       = None
            self.statusID     = None
            self.strIdent     = None
            self.is_notstatus = None
            self.is_qust_simp = None
            self.is_qust_regs = None
            self.is_proj_memb = None
            self.is_proj_head = None
            self.is_subheader = None
            self.is_proj_sadm = None
            self.is_superuser = None
            self.levelperm = 0
            self.str_info  = None
            self.username  = None


        def __str__(self):
            return self.str_info


        def __bool__(self):
            if self.error : return False
            else: return True


        """
        Создание структуры dict 
            full_name, status.strIdent
        """
        @classmethod
        def get_data_parentuser(cls, arg_user):                

            res_dict = {}
            try:
                user = getUser(arg_user)
                if user is None:
                    raise ErrorRun_impl('NotData##advuser.Type_status_user arg_user: нет данных ')

                _status = Com_proc_sprstatus.getStatus_or_None(user)
                if _status is None:
                    raise ErrorRun_impl('NotData##advuser.Type_status_user: нет статуса')

                res_dict = dict(
                        full_name=user.get_full_name(),
                        strIdent = _status.strIdent
                        )            

            except Exception as ex:
                TypeError_system(ex)
                raise ex

            return res_dict

    # ----------------------------------------------------


    res = Type_status_user()

    try:

        _user = getUser(arg_user)
        if _user is None:
            _run_raise('Пользователь не определен') 

        _status = Com_proc_sprstatus.getStatus_or_None(_user)
        if not _status:
            _run_raise('Статус не определен')                           

        exp_param = json.loads(_status.exp_param)

        #  {"conv": {"headerexp": "is_headerexp"} 
        key =  list(exp_param['conv'].keys())[0]
        conv = exp_param['conv'][key]
        setattr(res, conv, True)
        res.levelperm = _status.levelperm
        res.statusID  = _status.pk
        res.username = _user.username
        res.strIdent = _status.strIdent

        res.str_info = 'status:{0} ({2} levelPerm:{3}) - {1}'.format(_status.pk, 
                                                                     _status.strIdent, conv, 
                                                                     res.levelperm)

    except Exception as ex:
        res.is_notstatus = True
        res.error = str(ex)
        
    return res


        
