
from django.db import models
from . import Res_proc


# Отладка на уровне MySQL
class templ_buf(models.Model):
    id_key  = models.CharField(max_length=150, blank=True, null=True)
    val_buf = models.CharField(max_length=250, blank=True, null=True)
    val_any = models.CharField(max_length=250, blank=True, null=True)
    id_info = models.CharField(max_length=200,  blank=True, null=True)



"""
Справочник используемых строковых идентификаторов в других справочниках
    используетя в spr_setting -> Запись настроек ВСЕх приложений 
"""
class spr_usedIdent(models.Model):
    usedId = models.CharField(max_length=50, primary_key=True)
    s_info = models.CharField(max_length=250, blank=True, null=True)


"""
Справочник настроек ВСЕх приложений решения
usedId строковый идентификатор настроек -> spr_usedIdent.usedId
dict_param  -> dict формат параметров
id_used     -> идентификатор актуальности параметра  

testing:
    file tests/app/test__class_spr_setting_read_param.json
    modul: tests.app.test_app
    procedure: test__class_spr_setting_read_param
"""
class spr_setting(models.Model):    

    usedId = models.ForeignKey(spr_usedIdent, on_delete=models.CASCADE, verbose_name='СтрИдентификатор')
    dict_param =  models.CharField(max_length=2000, verbose_name='dict параметры')
    id_used = models.BooleanField(verbose_name='Актуальность настройки')


"""
Справочник содержит данные о структуре полей моделей  User, AdvUser, AdvUser.advData 
    id_field строковый идентификатор поля -> идентификатор модели
    js_data  json формат:  keyField:'empty'
"""
class spr_fields_models(models.Model):
    id_field = models.CharField(max_length=50, unique=True)
    js_data  = models.CharField(max_length=500)
    id_key   = models.SmallIntegerField(default=0, unique=True)

    #_permKeys = ('user','advuser', 'advdata_proj_memb',
    #             'advdata_subheader', 'advdata_headerexp',
    #             'advdata_qust_simp','advdata_qust_regs')  # список допустимых строковых идентификаторов модели

    _permDict  = ('info', 'fields_model')  # Список допустимых значений key в самом dict
    _perExclud = 'list, str, tuple'

    # идентифицирует способ обработки записи в БД
    from json import dumps, loads   


    @classmethod
    def get_limitcon70(cls)->Res_proc:
        """ Получить значение лимитПодкл на уровне рукГруппы максПрава
        arg_levelperm значение  spr_fields_models.id_key
        """

        res = Res_proc()

        try:

            row = spr_fields_models.objects.filter(id_key=70)
            if row.exists():
                row = row.first()
                dc_data = row.js_data
                dc_data = cls.loads(dc_data)  # конвертирование в формат json

                dc_fields_model = dc_data['fields_model']

                limitcon_dc = dict(limitcon=dc_fields_model['limitcon'],
                              limitcon40=dc_fields_model['limitcon40'],
                              limitcon70=dc_fields_model['limitcon70']                              
                              )
                res.res_dict = limitcon_dc
                res.res = True

        except Exception as ex:
            res_proc.error=er

        return res;


    @classmethod
    def get_limitcon40(cls, arg_levelperm:int)->int:
        """ Получить значение лимитПодкл Менеджеров
        arg_levelperm значение  spr_fields_models.id_key
        если arg_levelperm=70 будет считан параметр limitcon
        хотя для этого уровня имеются другие значения см. get_limitcon70
        """

        res = 0

        try:

            row = spr_fields_models.objects.filter(id_key=arg_levelperm)
            if row.exists():
                row = row.first()
                dc_data = row.js_data
                dc_data = cls.loads(dc_data)
                res = dc_data['fields_model'].get('limitcon') or 0

        except :
            res = 0

        return res;


    @classmethod
    def get_js_struct(cls, arg_levelperm)->dict:
        """ 
        return dict spr_fields_models.js_data[fields_model]  for arg_levelperm or None  
        """
        
        row = cls.objects.filter(id_key=arg_levelperm)
        if row.exists():
            row = row.first()
        else:
            return None

        res = cls.loads( row.js_data)
        res = res['fields_model']

        return res


    class Type_mod:        
        def __init__(self,  _upd=None, _ins=None):
            self.upd = None
            self.ins = None
            if _upd: 
                self.upd = True
                return 
            if _ins: 
                self.ins = True

    # return None or str
    @classmethod
    def get_dataField(cls, arg_status, arg_par):
        res = ''

        try:
            s_conv = cls.convStatus_into_strField(arg_status)
            if s_conv is None: return None

            row = cls.objects.filter(id_field=s_conv)
            if not row.exists():
                return None
            row = row.first()
            _dict = cls.loads(row.js_data)
            fields_model = _dict.get('fields_model')
            if fields_model is None: return None

            val = fields_model.get(arg_par)

            return val

        except:
            return None

        return res

    
    # используется из cls.update_model()...
    # Выборки из БД списка допустимых значений permKeys (из spr_setting)
    @classmethod
    def get_permKeys(cls):
        res = Res_proc()

        row = cls.objects.filter(id_field='permKeys_upd_param')
        if row.exists():
            row = row.first()

            _dict = cls.loads(row.js_data)
            _list = _dict.get('permKeys')
            if _list is None:
                res.error = ErrorRun_impl('ValueError##spr_fields_models.get_permKeys:  spr_setting.dict_param[permKeys] нет данных')
                return res

            res.res_list = _list
            res.res = True
        else:
            res.error = ErrorRun_impl('ValueError##spr_fields_models.get_permKeys: в spr_setting нет данных usedId_id=permKeys_upd_param, id_used=True ')

        return res


    @classmethod
    def convStatus_into_strField(cls, arg_status):
        if not isinstance(arg_status, str):
            raise ValueError('spr_fields_models.convStatus_into_strField arg_status: не соответствие типа')

        res = None

        if arg_status == 'headerexp':
            res ='advdata_headerexp'
            return res

        if  arg_status == 'subheader': 
            res = 'advdata_subheader'
            return res

        if  arg_status in ('proj-memb','proj-sadm', 'proj-head', 'superuser'):
            res = 'advdata_proj_memb'
            return res

        if  arg_status == 'qust-regs': 
            res = 'advdata_qust_regs'
            return res
        if  arg_status == 'qust-simp': 
            res = 'advdata_qust_simp'
            return res
        else:
            raise ValueError('spr_fields_models.convStatus_into_strField arg_status:%s не определен' % arg_status)


    """
    Используется для обновления структуры lst_fields в справочнике spr_fields_models
    lst_fields используется для шаблона dict as default для структур User, AdvUser, AdvUser.advData,
    который используется при манипуляциях с указанными объектами данных
        Входящий формат:
            [
            idModel1:{
                info:'Справочное поле',
                lst_fields:('idField',...)
                },
                idModel2:{
                info:'Справочное поле',
                lst_fields:('idField',...)
                },
                ...
                ]

            idMode из списка (user, advuser, advdata)
    """
    @classmethod
    def update_model(cls, _lstArg):      
        
        # Проверка наличия записи в spr_fields_models 
        def _verExists(arg_key):
            if spr_fields_models.objects.filter(id_field=arg_key).exists():
                return cls.Type_mod(_upd=True)
            else: return cls.Type_mod(_ins=True)

        res = []
        res_proc = cls.get_permKeys() # Выборка допустимых значений из БД 
        if res_proc.error:
            res.append(res_proc.error)
            return res

        _permKeys = res_proc.res_list

        for item in _lstArg:
            key = list(item.keys())[0]
            if key not in _permKeys:
                s_error = 'App.models.spr_fields_models.update_model {0} нет в списке допустимых значений'.format(key)
                res.append('{error: {0}'.format(keу, s_error))
                continue


            dict_data = item[key]

            # Проверка идентификатора key в списке допустимых значений
            for dct_key in dict_data.keys():
                if dct_key not in cls._permDict:
                    s_error = 'App.models.spr_fields_models.update_model: key in json д\быть info or lst_fields '
                    res.append('error: {0}'.format(s_error))
                    continue
            try:
                type_mod = _verExists(key)
                js_data = cls.dumps(dict_data, ensure_ascii=False)

                if type_mod.ins:
                    spr_fields_models.objects.create(id_field=key, js_data=js_data)
                else:
                    spr_fields_models.objects.filter(id_field=key).update(js_data=js_data)

                if type_mod.ins: s_res = '{0} вставлено'.format(key)
                else: s_res = '{0} обновлено'.format(key)

                res.append(s_res)

            except Exception as ex:
                res.append('{0} error:{1}'.format(key,str(ex)))
                return res
        return res


    """
    Используется для доступа к списку полей моделей Use, AdvUser 
    и структуры поля AdvUser.advData
    параметры 
        _model  строковый идентификатор запрашиваемого набора keys
                набор допустимых значений лимитирован в справочнике 
                                        spr_fields_models.id_field=permKeys_upd_param
                этот параметр можно получить из cls.convStatus_into_strField(statusID)
        exclude = строка или list или tuple списков полей, которые исключить из результата вывода
        onKeys  = True  в результирующем списке только keys
                  False в результирующем списке вся структура dict fields_model
    """
    @classmethod
    def get_list_fields(cls, _model, exclude=None, onlyKeys=None):

        if not isinstance(_model, str):
            type_error = Type
            raise ValueError('ValueError##app.spr_fields_models.get_list_fields _model: не соответствие типа')
        
        _permKeys = cls.get_permKeys()
        if _model not in _permKeys.res_list:            
            raise ValueError('ValueError##app.spr_fields_models.get_list_fields _model=%s: \n\t\t\t\t\tнет данных в списке доступных значений' % _model)

        dct_fields = {}
        model = cls.objects.filter(id_field=_model)
        if model.exists():
            model = model.first()
        else: model = None

        if model is None:
            raise ValueError('ValueError##app.spr_fields_models.get_list_fields %s: нет данных в модели' % s_type)

        try:
            js_dict = cls.loads(model.js_data)
            dct_fields = js_dict['fields_model']
            if exclude:                
                s_type = type(exclude).__name__
                if s_type not in cls._perExclud:
                    raise TypeError('TypeError##app.spr_fields_models.get_list_fields exclude: не соответствие значения')

                if s_type == 'str':  # одиночное исключение из общего списка
                    if dct_fields.get(exclude):
                        del dct_fields[exclude]
                    else:
                        raise ValueError('ValueError##app.spr_fields_models.get_list_fields: exclude=%s нет в списке' % exclude)

                else:
                    for k in exclude:
                        if dct_fields.get(k):
                            del dct_fields[k]
                        else:
                            raise ValueError('ValueError##app.spr_fields_models.get_list_fields: exclude=%s нет в списке' % k)

            if onlyKeys:
                res = tuple(dct_fields.keys())
                return res

            return dct_fields

        except Exception as ex:
            raise ex


    """
    Список полей для advData по значению status
    """
    @classmethod
    def get_list_fields_advDataExt(cls, arg_statusID, exclude=None, onlyKeys=None):
        from advuser.models import SprStatus

        if arg_statusID is None:
            raise ErrorRun_impl('ValueError##spr_fields_models.get_list_fields_advDataExt arg_statusID: значение None')

        s_type = type(arg_statusID).__name__
        if s_type in ('str', 'SprStatus'):
            if s_type == 'SprStatus':
                arg_statusID = arg_statusID.pk
        else:
            raise ErrorRun_impl('ValueError##spr_fields_models.get_list_fields_advDataExt arg_statusID: не соответствие типа')

        tmpl_str = cls.convStatus_into_strField(arg_statusID)

        res = cls.get_list_fields(tmpl_str, exclude, onlyKeys)
        return res 
        

    """
    testing:
        file: tests/app/test__class_spr_fields_models_advdata
        modul: app.test_app
        procedure: test__spr_fields_models_advdata
    """
    @classmethod
    def get_list_fields_advData(cls, arg_model, exclude=None, onlyKeys=None):
        from advuser.models import AdvUser
        from advuser.models import SprStatus

        perm_type = ('User','AdvUser','str','int')
        s_error = 'SystemError##spr_fields_models.get_list_fields_advData arg_model:'

        if arg_model is None:
            raise ErrorRun_impl('ValueError##{0} is None'.format(s_error))

        s_type = type(arg_model).__name__
        if s_type not in perm_type:
            raise ErrorRun_impl( 'ValueError##{0} не соответствие типа'.format(s_error))

        if s_type in ('str','int'):
            status = SprStatus.getStatus('',arg_model)
        else:
            status = SprStatus.getStatus(arg_model)

        tmp_dict = cls.get_list_fields_advDataExt(status, exclude=exclude, onlyKeys=onlyKeys)
            
        return tmp_dict


class spr_param_proj(models.Model):  
    val_param = models.CharField(max_length=150)
    str_param = models.CharField(max_length=150)
    key_param = models.CharField(max_length=50, unique=True, null=True)
    path_proj = models.CharField(max_length=50, null=True)

    @classmethod
    def get_param_spr(cls, str_param):
        if cls.objects.filter(key_param=str_param).exists():
            spr_param = cls.objects.filter(key_param=str_param).first()
            return spr_param
        else: return None


class log_acivity_user(models.Model):
    from django.contrib.auth.models import User

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    date_rec = models.DateField(verbose_name='НачДатаЛогина', auto_now_add=True )
    date_last = models.DateField(verbose_name='ПослДатаПосещ', auto_now=True)
    mm = models.SmallIntegerField(verbose_name='месяц')
    yy = models.SmallIntegerField(verbose_name='Год')
    id_record = models.SmallIntegerField(verbose_name='Индикатор', default=1)   # 1 Текущая запись 2 Сумма посещеня сайта за месяц  3 сумма посещений за год
    counter_login = models.IntegerField(verbose_name='Кол-во', default=1)

    class Meta:
        verbose_name_plural = 'Журнал активности'
        verbose_name = 'Активность пользователя'

    # Регистрация активности пользователя
    def register_login_user(user):

        try:
            if not user: return

            if not isinstance(user, User):
                user = getUser(user)
                if not user: return

            date_now = datetime.date.today()
            log = log_acivity_user.objects.filter(user=user, date_last=date_now)
            if not log.exists():


                log_activty = log_acivity_user()
                log_activty.user = user
                log_activty.mm = date_now.month
                log_activty.yy = date_now.year

                log_activty.save()

            else:            
                log_activty = log.first()
                log_activty.counter_login +=1

                log_activty.save()

        except:
            return 


# Буфер данных по advData перед обновлением пароля гостВхода
class templ_buffer(models.Model):

    # допустимо создавать любое кол-во копий одник и тех данных

    group       = models.CharField(max_length=20)       # идентификатор группы пакета 
                                                        # -> AnyMixin.any_mixin. getEMTPY_id(15)
    id_parent   = models.BooleanField(default=False)    # идентификатор parentuser    
    username    = models.CharField(max_length=50)       # идентификтор пользователя username
    date_modf   = models.DateField(auto_now=True )      # дата создания буфера
    s_info      = models.CharField(max_length=150)      # описатель содержимого в буфере 
    val_copy    = models.CharField(max_length=1500)     # поле копии данных


"""
Журнал обновления пароля гостВхода
------------------------------------
Testing prtesting.tests.app.test_app
file:  prtesting/tests/app/test__log_modf_models.json
"""
class log_modf_models(models.Model):
    id_log      = models.CharField(max_length=100)      # идентификатор операции в БД -> username##Quest_username
                                                        # для parentRow only username
    row_parent  = models.CharField(max_length=100)      # ссылка на parentRow
    id_parent   = models.BooleanField(default=False )   # True -> идентификатор ParentRow
    date_modf   = models.DateField(auto_now=True )      # дата обновления 
    id_end      = models.BooleanField(default=False )   # идентификатор окончания обновления 
    inf_modf    = models.CharField(max_length=150)       # инфСтрока процедуры обновления
    arg_modf    = models.CharField(max_length=100, default='', blank=True, null=True)


"""
Начальное заполнение из tests.app.test_app.py
    procedure: test_load_data_into_spr_pswcl
    скрипт сохр. AnyMixin/any_templ/any_data/load_data_into_spr_pswcl.txt
------------------------------------------
Справочник паролей клиентского входа
    meaning перевод или значение pswcl
    for_use empty:запись свободна для использования
            else: username логин руководителя группы
"""
class spr_pswcl(models.Model):
    
    pswcl = models.CharField(max_length=10, verbose_name='Логин гостВхода', unique=True)
    date_add = models.DateField(verbose_name='Дата создЗаписи', auto_now=True)
    meaning = models.CharField(max_length=50, verbose_name='Смысл/значение pswcl',  blank=True, null=True)
    for_use = models.CharField(max_length=20, verbose_name='Владелец записи', default='empty' )

    # Выборка случайной не занятой записи
    """
        Возвращает кортеж (pswcl, meaning)        
    """
    @classmethod
    def get_rand_pswcl(cls):
        import random

        res_proc = Res_proc()

        try:
            rows = cls.objects.all()
            lst_row = None
            if rows.exists():
                lst_row = list(( (row.pswcl, row.meaning)  for row in rows ))

            if lst_row:
                res_proc.res = True
                res_proc.res_obj = random.choice(lst_row)

        except Exception as ex:
            res_proc.error = ex

        return res_proc
