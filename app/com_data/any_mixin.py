
from .type_error import TypeError_system 
from .user_except import ErrorRun_impl

from random import choice
from string import ascii_lowercase, ascii_uppercase, digits


# Поиск и создание объекта User 
"""
Тестирование 17.05.2020
modul: tests.com_data.test_com_data
fule : tests/app/com_data/test_com_data.json
"""
def getUser(user):
    from django.contrib.auth.models import User

    sType = type(user).__name__

    try:
        if sType == 'int':  # доступ по id
            if User.objects.filter(pk=user).exists():
                return User.objects.get(pk=user)
            else: return None

        elif sType == 'str':
            if User.objects.filter(username=user).exists():
                return User.objects.get(username=user)
            else: return None        

        elif sType == 'User': 
               return user

        elif hasattr(user,'username'):
            _user = user.username
            return getUser(_user)

        else: return None

    except:
        return None


# Генерирования logincl  and  pswcl 
class Value_login_psw_cl:

    @classmethod
    def _verifyExistsUser(cls, username): 
        from django.contrib.auth.models import User
        if not isinstance(username, str):
            raise TypeError('_verifyExistsUser тип параметра д.быть строкой')

        res = User.objects.filter(username=username).exists()
        return res

    @classmethod
    def _getLogin_cl(cls):
        return ''.join(choice(ascii_uppercase) for i in range(4)) + '-'+ ''.join(choice(digits) for i in range(4))

    @classmethod
    def getLogin_cl(cls):    
        login = cls._getLogin_cl()
        while cls._verifyExistsUser(login):
            login = cls._getLogin_cl()
        
        return login

    def getPassword_cl():    
        from app.models import spr_pswcl

        try:
            res_pswcl = spr_pswcl.get_rand_pswcl()
            if not res_pswcl:
                return None

            _pswcl = res_pswcl.res_obj[0]

            return _pswcl

        except:
            return None
        

def getPassword_cl():    
    return Value_login_psw_cl.getPassword_cl()

# формирует случайное структуру логина по формату SSS-NNNN
def getLogin_cl():  
    return Value_login_psw_cl.getLogin_cl()


"""
Используется в качестве буфера, содеражащего данные из 
обрабатываемых процедур, методов класса
-----------------------------------------------
Тестирование 17.05.2020
modul: tests.app.test_com_data
file:  tests/app/com_data/test_com_data.json
"""
class Res_proc:

    def __init__(self, res=False, mes=None, title=None, 
                 error=None, res_dict=None, 
                 res_list=None, 
                 res_model=None, res_obj=None):

        self.res = res
        self.mes = None
        self.title = None
        self.res_model = None
        self.res_obj = None

        self._error     = None
        self._res_dict  = None 
        self._res_list  = None 
        self.username   = None
        self.any_str    = None

        if res_dict: self.res_dict = res_dict
        if res_list: self.res_list = res_list
        if error:    self.error = error


    def __str__(self):

        res = ' '
        dc = dict(res='true' if self.res else 'false' )
        if self.mes: dc['mes'] = self.mes
        if self.title : dc['title'] = self.title
        if self.error: dc['error']= self.error
        if self.res_dict: dc['res_dict']= 'object dict'
        if self.res_list: dc['res_list'] = 'object list'
        if self.res_model: dc['res_model'] = 'object model'
        if self.res_obj: dc['res_obj'] = 'object any_object'
        if self.any_str: dc['any_str'] = self.any_str

        for k,v in dc.items():
            res += '{0}:{1}; '.format(k,v)
        
        return res
    
    _const_empty = 'empty'
    _const_exist = 'exist'
    _const_notRecord = 'notRecord'
    _const_notData = 'NotData'


    # чтобы меньше было ошибок при написании
    # и чтобы везде было одинаково 
    if 1<2:  # для удобства сопровождения 
        @classmethod
        def FN_exist(cls):     
            return cls._const_exist

        @classmethod
        def FN_empty(cls):     
            return cls._const_empty

        @property
        def PR_exist(self): 
            return self.FN_exist()

        @property
        def PR_empty(self): 
            return self.FN_empty()

        # Для общей идентификации результата поиска данных в БД
        @property
        def PR_notRecord(self):
            return self._const_notRecord

        """
        val from dict
            если val == None or val==empty -> None
            иначе return val
        """
        @classmethod
        def FN_get_val_dict(cls, arg_dict, arg_key):
            """ Извлекает значение из dict if result None or empty return None else val_from_dict """

            s_err = 'AnyMixin.any_mixin.Proc_res.FN_val_dict'
            res = None
            _empty = cls.FN_empty()

            if not isinstance(arg_dict, dict):
                raise cls.ErrorRun_impl('TypeError##{0}'.format('arg_dict: не соответствие типа') )
            if not isinstance(arg_key,str):
                raise cls.ErrorRun_impl('TypeError##{0}'.format('arg_key: не соответствие типа') )

            val = arg_dict.get(arg_key)
            if val and val != _empty:
                res = val
            
            return res

    # ---------- конец блока полей удобства написания кода -------------


    # Для переноса сообщения error.
    # сообщения из вызываемого кода, без обработки через loggin (только присвоить self.error!!!)
    def copyError(self, arg_res):
        if isinstance(arg_res, Res_proc):
            self._error = arg_res.error
        else:
            self.error = ErrorRun_impl('verify##'+ str(arg_res))

    def __bool__(self):
        if self.error: return False
        else: return True

    @property
    def res_list(self):
        return self._res_list

    @res_list.setter
    def res_list(self, value):
        if isinstance(value, list):
            self._res_list = value
        else:
            self._res_list = None
            self.error = ErrorRun_impl('TypeError##Res_proc setter res_list value: не соответствие типа д\быть list')

    @property
    def res_dict(self):
        return self._res_dict

    @res_dict.setter
    def res_dict(self, value):
        if isinstance(value, dict):
            self._res_dict = value
        else:
            self._res_dict = None
            self.error = ErrorRun_impl('TypeError##Res_proc setter res_dict value: не соответствие типа д\быть dict')



    """
    Используется для создания форматированной строки для self.error
    """
    @classmethod
    def initStr_error(cls, arg_err:str):
        res = ''

        if isinstance(arg_err, str):            
            res = arg_err
        else:
            _class = arg_err.__class__.__name__
            s_err = str(arg_err)
            res = '{0}##{1}'.format(_class, s_err)

        return res


    @property
    def error(self):
        return self._error

    """
    testing:
        file: tests/anymixins/any_mixin/test__class_Result_procedure_setter.json
        modul: tests.anymixins.test_anymixin_ext
        procedure: test__class_Result_procedure_setter
    """
    @error.setter
    def error(self, value):                    

        _err_system = TypeError_system(value)
        self._error = _err_system.PR_error

        self.res = False


# процедура выборки данных из dict
def get_valFromDict(dcStrt, strFinde, strDefault=None):
    if not dcStrt: return strDefault

    return dcStrt[strFinde] if dcStrt.get(strFinde) else strDefault


# Проверка элПочты, исключая самого user
def verify_exists_email_ext(email, arg_user):

    if not isinstance(arg_user, User):
        arg_user = getUser(arg_user)
        if not arg_user: return None

    ar_user = User.objects.filter(email=email).exclude(pk=arg_user.pk)
    if ar_user.exists():    
        return True
    else: return False 


# Сквозная проверка уникальности элПочты
def verify_exists_email(email):
    return  User.objects.filter(email=email).exists()


class CreateUser_ext:
    """ Класс обработки структуры User """

    class _BaseUserManager():
        """ Встроенный класс дополнительных проверок """

        @classmethod
        def Normalize_email(cls, email):
            """
            Normalize the email address by lowercasing the domain part of it.
            """
            email = email or ''
            try:
                email_name, domain_part = email.strip().rsplit('@', 1)
            except ValueError:
                pass
            else:
                email = email_name + '@' + domain_part.lower()
            return email

        @classmethod
        def create_user(cls, username, email, password, **extra_fields):
                """
                Only Create a user with the given username, email, and password.
                """
                if not username:
                    raise ValueError('Нет данных для username')

                email = cls.Normalize_email(email)
                username = User.normalize_username(username)
                user = User(username=username, email=email, **extra_fields)

                user.set_password(password)

                return user

    @classmethod
    def create_user(cls, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)

        res = cls._BaseUserManager.create_user(username, email, password, **extra_fields)
        return res


def get_listKeys_user():
    res = ('username','first_name', 'last_name', 'email', 'is_active', 'user_id')
    return res


def getEMTPY_id(length=15):
    from django.utils.crypto import get_random_string

    allowed_chars=(
        'abcdefghjkmnpqrstuvwxyz'
        'ABCDEFGHJKLMNPQRSTUVWXYZ'
        '23456789')
    emptyMes = get_random_string(length, allowed_chars)

    return emptyMes
