
from app import ErrorRun_impl, TypeError_system
from app.com_data.any_mixin import getUser, Res_proc
from .serv_advuser import servAdvUser_get_advUser
import json


class Com_proc_sprstatus:
    """ class содержащий сервис обработки атрибутов модели SprStatus """

    _s_err = 'SyntaxError##advuser.serv_sprstatus.Com_proc_sprstatus'
    _s_err_user_notData = 'Пользователь User не определен'

    #процедура вызова ErrorRun_impl
    @classmethod
    def _run_raise(cls, s_arg, showMes=None, s_err=None):        

        s_err = s_err or cls._s_err

        if showMes:            
            raise ErrorRun_impl('verify##{0}'.format(s_arg))
        else:
            s_mes = '{0} {1}'.format(s_err, s_arg)
            TypeError_system(ErrorRun_impl(s_mes))  # запись в файл app/loggin/*.log
            raise ErrorRun_impl(s_mes)


    @classmethod
    def get_list_levelperm(cls)->Res_proc:
        """ Выборка значений status_id, levelperm по ВСЕМУ справочнику SprStatus
        return Res_proc.res_list = list( dict(lvperm=Number, status=str), ... )
        """
        from .models import SprStatus

        res_proc = Res_proc()
        lst = []

        try:

            rows = SprStatus.objects.filter(levelperm__gte=10)
            if rows.exists():
                for row in rows:
                    lst.append( dict(lvperm=row.levelperm, status=row.status) )

            res_proc.res_list = lst
            res_proc.res = True

        except Exception as ex:
            res_proc.error = ex

        return res_proc


    @classmethod
    def get_levelperm(cls, arg_statusID:str)->int:
        """ По значению arg_statusID выборка levelperm 
        return val_levelperm or 0
        """
        from .models import SprStatus

        res = 0

        try:

            row = SprStatus.objects.get(pk=arg_statusID)
            res = row.levelperm

            return res

        except:
            return 0



    # Процедура доступа к объекту cls.SprStatus
    """
    testing: 19.05.2020
        modul: prtesting.tests.advuser.serv_sprstatus
        file: tests/advuser/serv_sprstatus/test_sprstatus_serv.json
        -----------------------------------------------
        возвращает объект cls.SprStatus or None
        -----------------------------------------------
        username   -> извлекается из kwages[username] 
                      ВСЕ параметры игнорируются 
                      извлекается row SprStatus for User                      
                      ---------------------------------
        agr_status -> User, AdvUser, str==statusID            
    """
    @classmethod
    def getStatus_or_None(cls, arg_status=None, **kwargs):        
        """return obj_sprStatus_or_None  
           username   -> извлекается из kwages {username:data_username}
                          ВСЕ параметры игнорируются 
                          извлекается row SprStatus for User                      
                          ---------------------------------
           agr_status -> User, AdvUser, str==statusID """

        def _get_status_or_None(arg_user):
            try:
                _user = getUser(arg_user)
                if _user is None: 
                    cls._run_raise(cls._s_err_user_notData)
                
                if _user.is_superuser:
                    return cls._get_filter_obj('superuser')

                _advUser = _user.advuser

                return _advUser.status

            except Exception as ex :
                return None


        username = kwargs.get('username')
        statusID = kwargs.get('statusID')
        arg_status= arg_status or kwargs.get('arg_status')
        #-------------------------------------------------------
        
        if username:  # Поиск по логину
            return _get_status_or_None(username)

        else:
            s_type = type(arg_status).__name__

            if s_type == 'User':
                return _get_status_or_None(arg_status)                 

            elif s_type == 'AdvUser':
                return arg_status.status

            else:

                if arg_status is None or s_type == 'str':
                    s_param = arg_status or statusID
                    if s_param :
                        return cls._get_filter_obj(s_param)
                else:
                    return None


    @classmethod
    def _get_filter_obj(cls, statusID):
        """ return obj_or_None  Основная процедура доступа к атрибутам модели sprStatus """

        from .models import SprStatus

        try:
            res = None

            if not isinstance(statusID, str): 
                cls._run_raise('_get_filter_obj: Аргумент statusID не соответствие типа')

            filter = SprStatus.objects.filter(pk=statusID)
            if filter.exists():
                res = filter.first()

            else:
                cls._run_raise('_get_filter_obj: статус не определен: '+ statusID)

            return res

        except Exception as ex: 
            return None


    """
    Тестирование 19.05.2020 :
        modul: prtests.tests.advuser.serv_sprstatus.test_serv_sprtatus
        file : tests/advuser/serv_sprstatus/test_sprstatus_serv.json
    ----------------------------------------------------------------------

    Возвращает res.res_obj == class PermModf_prof(...) в котором определены 
               ВСЕ атрибуты привелегий
    ------------------------------------------------------
    Права на обработку профиля, указанный в arg_modf
    arg_modf -> строка формата:  add_STATUS or upd_STATUS
                STATUS  -> proj-memb, subheader и другие значени из SprStatus.pk
                из arg_modf извлекаются первые 3 символа -> идентификатор метода обработки

    arg_model ->  str, int, User, AdvUser
        преобразование в STATUS
        из STATUS.any_option -> извлекаются ВСЕ необходимые данные
    --------------------------------------------------------------
    Возвращается объект res.res_obj = permMod_prof(arg_status)
    """
    @classmethod
    def get_permModf_prof(cls, arg_model, arg_modf):
        """ return class PermModf_prof(...) в котором определены ВСЕ атрибуты ПРИВЕЛЕГИЙ
            class PermModf_prof создан внутри вызываемой процедуры """

        class _PermModf_prof:
            """
            Формат входящего аргумента arg_dict: 
            структура dict из sprStatus.any_option

            {exist="exist or empty", mes="КраткИнформ", prof={add_prof:[lst_STATUS], upd_prof:[lst_STATUS] },
              err_add="Сообщение при отсутствии прав на создПроф", 
              err_upd="Сообщение при отсутствии на измПроф"  }
            """
        
            def __init__(self, arg_status):                
                self.err_add = None
                self.err_upd = None
                self.mes = None

                self.perm_addProf = False
                self.perm_updProf = False
                self.status_modf = None

                #---------- инициализация уровня привилегий пользователя ------------
                # ------ 
                self.levelperm = arg_status.levelperm
                self.statusID = arg_status.pk

                self._init_perm()  # процедурная инициализаци
                    

            # верификация вхождения self.statusID в списки 
            # допустимых привилегий add_prof and upd_prof 
            def _init_perm(self):
                _statusID = arg_modf[4:]
                self.status_modf = _statusID

                status = cls.getStatus_or_None(_statusID)

                # считывание дополнительных параметров из sprStatus.any_option, определяющие 
                # привилегии изм/созд профиля
                # там считываются значения для отображения сообщений отсутствия привилегий
                if status:
                    any_option = json.loads(status.any_option)
                    _exist = Res_proc.FN_exist()

                    self.mes = any_option['mes']
                    self.err_add = any_option.get('err_add') or self.mes
                    self.err_upd = any_option.get('err_upd') or self.mes
                    
                    if any_option[_exist] == _exist:
                        prof = any_option['prof']
                        if prof:
                            add_perm = prof.get('add_prof')
                            upd_perm = prof.get('upd_prof')
                            if self.statusID in add_perm:
                                self.perm_addProf = True
                            if self.statusID in upd_perm:
                                self.perm_updProf = True

                else:
                    cls._run_raise(' get_permMod_prof.class PermModf_prof._init_perm status:{0} не определен'.format(_statusID))                    

            @property
            def PR_permAdd(self): return self.perm_addProf

            @property
            def PR_permUpd(self): return self.perm_updProf

            def __str__(self):

                s_res = ''
                _empty = Res_proc.FN_empty()

                s_err_add = ''
                s_err_upd = ''

                if not self.PR_permAdd:
                    s_err_add = 'err_add:{0}'.format(self.err_add)
                if not self.PR_permUpd:
                    s_err_upd = 'err_upd:{0}'.format(self.err_upd)

                s_res = '{0}: level:{1} modfProf:{2} permAdd:{3} permUpd:{4} {5} {6}'.format(
                                self.statusID, 
                                self.levelperm,
                                self.status_modf,
                                self.PR_permAdd or _empty, 
                                self.PR_permUpd or _empty,
                                s_err_add,
                                s_err_upd
                                )
                return s_res

        # ****************** PermModf_prof ********************


        res = Res_proc()
        _status = None

        s_type = type(arg_model).__name__
        
        try:

            if arg_modf[:3] not in ('add','upd'):
                res.error = ('ValueError##cls.SprStatus.get_permMod_prof arg_prof: не соответствие стурктуре формата add_* or upd_*')
                return res


            if s_type == 'AdvUser': 
                _advuser = arg_model
                _status  = _advuser.status

            else: 
                if s_type in ('User','str','int' ):
                
                    # если это суперПользователь разрешить изменение, добавление любого профиля
                    user = getUser(arg_model)
                    if user:
                        if user.is_superuser:
                            _status = cls.getStatus_or_None(user)
                            if _status is None:
                                cls._run_raise(' get_permModf_prof: статус суперПользователя не определен')

                            permModf = _PermModf_prof( _status )

                            res.res = True
                            res.res_obj = permModf
                            return res

                        else:
                            res_advUser = servAdvUser_get_advUser(user)        
                            if res_advUser is None:
                                res.error = ErrorRun_impl('ValueError##cls.SprStatus.get_permMod_prof: нет данных в модели AdvUser')
                                return res

                            _advuser = res_advUser.res_model
                            _status  = _advuser.status
            
            # ----------------- конец блока верификации и инциализации ------------------


        
            permModf = _PermModf_prof(_status)

            res.res = True
            res.res_obj = permModf

        except Exception as ex:
            res.error = ex

        return res
# ----------- Конец get_permMod_prof -------------------

    # return statusID or None
    """
    testing 20.05.2020
    modul: prtesting.tests.advuser.serv_sprstatus.test_serv_sprstatus
    procedure: test_simpl_proc
    file: tests.advuser.serv_sprstatus.test_sprstatus_serv.json
    """
    @classmethod
    def get_statusID_user(cls, user):
        """ возврString statusId or None
            входАргумент user преобразуется/проверяется через getUser(user)
            --------------------------------------------------
        return statusID_or_None for User """

        user = getUser(user)

        if user is None: return None

        _status = cls.getStatus_or_None(user)
        if _status is None:
            return None

        return _status.pk


    
    #**************** Вспомогательный сервис  ****************

    """
    testing 20.05.2020
    modul: prtesting.tests.advuser.serv_sprstatus.test_serv_sprstatus
    procedure: test_simpl_proc
    file: tests.advuser.serv_sprstatus.test_sprstatus_serv.json
    
    Выполнено тестирование перечисленных процедур
    get_status_qust_simp, get_status_qust_regs
    get_status_header, get_status_pradm, get_status_suadm, get_status_notstatus
    """
    @classmethod
    def get_status_qust_simp(cls):
        """ return obj_or_None Объект sprStatus for qust-simp гостевой вход  """

        return cls.getStatus_or_None('qust-simp')


    @classmethod
    def get_status_qust_regs(cls):
        """ return obj_or_None Объект sprStatus for qust_regs зарегистрированный клиент  """

        return cls.getStatus_or_None('qust-regs')
    
    
    # объект sprStatus_or_None for руководПроекта
    @classmethod
    def get_status_header(cls):
        """ return sprStatus_or_None объект sprStatus for proj-head руководитель проекта """

        res = cls._get_filter_obj('proj-head')
        if not res:
            cls._run_raise('Нет данных для руководителя проекта')

        return res


    # объект sprStatus_or_Exception for руководПроекта
    @classmethod
    def get_status_pradm(cls):
        """ return obj sprStatus_or_Exception  Администратор проекта"""

        res = cls.getStatus_or_None('proj-sadm')        
        if not res:
            cls._run_raise('Нет данных для администратора проекта')

        return res
    
    # объект sprStatus_or_Exception for суперПользователя
    @classmethod
    def get_status_suadm(cls):
        """ return obj sprStatus_or_Exception суперПользователь """

        res = cls._get_filter_obj('superuser')        
        if not res:  
            cls._run_raise('Нет данных для суперпользователя проекта')

        return res

    @classmethod
    def get_status_notstatus(cls):
        res = cls._get_filter_obj('notstatus')        
        if not res:
            cls._run_raise('Нет данных для notstatus')

        return res





def serv_SprStatus(arg_proc, arg_param=None, **kwargs):
    """ Процедура-диспетчер обработки сервиса
        arg_proc стрИдентиф процедуры из Com_proc_sprstatus
        arg_dict_param  dict параметров:
            key - идентифПараметра
            val - значениеПараметра    """

    if not hasattr(Com_proc_sprstatus, arg_proc):
        raise ErrorRun_impl('NotData##advuser.serv_sprstatus.serv_SprStatus arg_param не найдена процедура в Com_proc_sprstatus')
        
    proc = getattr(Com_proc_sprstatus, arg_proc)
    
    return proc(arg_param, **kwargs)


# ------------------- Ссылочный интерфейс процедур обработки данных SprStatus ------------------

getStatus_or_None = Com_proc_sprstatus.getStatus_or_None
get_permModf_prof = Com_proc_sprstatus.get_permModf_prof  # 
