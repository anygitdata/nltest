"""
AnyMixin

modul Type_value

class Type_value 

"""


# Идентификатор типа объекта 
class Type_value: 
    
    """
    class определяет дополнительные характеристики строки,
        используемой для обработки json
        обновления dict
    """
    class _optionStr:
        def __init__(self, arg_str=None):
            
            # -----------  JSON объекты ------------------
            self.jsn = False # Общий идентификатор для объектов JSON

            # Идентификатор JSON объекта, который используется отдельно по каждому элементу
            self.jdv = False 

            #--------- идентификаторы массивов -----------
            self.lke = False # строковый массив dict.keys - разделитель пробел
            self.lst = False # массив произвольных строк с разделителем пробел
            self.lnt = False # массив с целыми числами с разделителем пробел

            #--------- прочие идентификаторы -------------
            self.int = False # строка типа int
            self.emp = False # пустая строка
            self.any = False # произвольная строка
               
            # -------- процедурная инициализация --------
            # если строка==empty or None -> шаблон строки {%emp%} для инициализации
            if not arg_str or arg_str=='empty':
                _arg = '{0}{1}{2}'.format('{%','emp','%}')                  
                self._init_self(_arg)
            else:
                self._init_self(arg_str[:7])
            

        def __str__(self):
            res = ''

            if self.lke: res = 'Массив dict.keys()'
            elif self.jsn: res = 'optionStr:jsn объект JSON'
            elif self.jdv: res = 'optionStr:jdv объект JSON маркер: oneMulti'
            elif self.lst: res = 'optionStr:lst listStr: произ. строк'
            elif self.lnt: res = 'optionStr:lnt listInt: массив int'
            elif self.int: res = 'optionStr:int'
            elif self.emp: res = 'optionStr:emp'
            else: res = 'optionStr:any произвольная строка'

            return res

        @classmethod
        def verify_arg_jsn(cls, arg_str):
            if not isinstance(arg_str, str):
                raise ValueError('Ext_dict._get_dict_FromStr arg_str не соответствие типа аргумента')

            _type = Type_value.type_value(arg_str)

            if not _type.is_str:
                raise ValueError('Ext_dict._get_dict_FromStr arg_str не соответствие типа аргумента')


            _option = _type.optionStr
            if _option.jsn or _option.jdv:                
                return True
            else: 
                raise ValueError('Ext_dict._get_dict_FromStr arg_str не соответствие типа аргумента')
                

        @classmethod
        def get_str_asDefault(cls):
            return 'jsn'

        @classmethod
        def _get_list_par(cls): return ('lke','jsn','jdv','lst', 'lnt','int','emp','any')

        def _init_self(self, arg_par):

            if   arg_par == '{%lke%}': self.lke = True
            elif arg_par == '{%jsn%}': self.jsn = True
            elif arg_par == '{%jdv%}': self.jdv = True
            elif arg_par == '{%lst%}': self.lst = True
            elif arg_par == '{%lnt%}': self.lnt = True
            elif arg_par == '{%int%}': self.int = True
            elif arg_par == '{%emp%}': self.emp = True
            else:
                self.any = True

        @property
        def PR_strOption_Default(cls):            
            return 'jsn'

        @property
        def PR_notUpdate_dict(self):
            res = False
            if self.lke or self.lst or self.lnt or self.int or self.emp or self.any:
                res = True

            return res

        @property
        def PR_input_list(self):
            res = False
            if self.lke or self.lst or self.lnt:
                res = True

            return res

        @property
        def PR_input_dict(self):
            res = False
            if self.jsn or self.jdv:
                res = True

            return res
    # ----------- Конец контента _optionStr ---------- 

    """
     Дополнительная опция для характеристики типа is_dict
         {key:val}  oneSimple
         {key={par1:val1}} oneMulti
         {key:[anyData]}   oneList 
     
         {par1:val1, par2=val2} multiKeys
     """
    class _optionDict:
        def __init__(self, arg_oneSimple=False,  arg_oneMulti=False, arg_oneList=False, arg_multiKeys=False):
            self.empty = False
            self.oneMulti_as_one = True

            self.oneSimple = False  # Самый простой тип
            self.oneMulti = False   # Простой dict со значением val as dict
            self.oneList   = False  # Простой dict со значением val as list

            self.multiKeys = False  # Расширенный dict, содержащиц множество keys

            if arg_oneSimple:   self.oneSimple = True
            elif arg_oneMulti:  self.oneMulti = True
            elif arg_oneList:   self.oneList = True
            elif arg_multiKeys: self.multiKeys = True
            else:
                self.empty = True


        def __str__(self):
            s_res = ''

            if   self.oneSimple : s_res = 'oneSimple'
            elif self.oneMulti  : s_res = 'oneMulti'
            elif self.oneList   : s_res = 'oneList'
            elif self.multiKeys : s_res = 'multiKeys'
            else: s_res = 'empty'

            s_res = 'option: ' + s_res
            return s_res

        @property
        def PR_notUpdate_dict(self):
            res = False
            if self.empty:
                res = True

            return res

        @property
        def PR_input_dict(self):
            if self.oneMulti or self.oneSimple or self.multiKeys:
                return True
            else: return False
    # ------- Конец контента _optionDict -------------

    class Option_oneMulti:

        @classmethod
        def get_str_oneMulti(cls):
            return 'oneMulti'

        """
         Централизованное обновление внешнего dict
         Маркером, что dict содержит значения value as dict
         arg_dict м\быть multiKeys 
        """
        @classmethod
        def append_oneMulti(cls, arg_dict):
            if not isinstance(arg_dict, dict):
                raise ValueError('Type_value.append_oneMulti arg_dict not dict')

            key = cls.get_str_oneMulti()
            arg_dict.update({key:True})
    #------ Конец контента Option_oneMulti -----------


    # ************* Блок @classmethod ***************
    _str_error_type = ': не соответствие типа'
    _str_error_value = ': не задано значение'

    @classmethod
    def formatTempl(cls, arg_templ): 
        if not isinstance(arg_templ, str):
            raise TypeError('Type_value.formatTempl arg_templ'+cls._str_error_type)

        if arg_templ in cls._optionStr._get_list_par():
            return '{0}{1}{2}'.format('{%',arg_templ,'%}')
        else:
            raise ValueError('Type_value.formatTempl arg_templ: не соответствует допустимым значениям')

    @classmethod
    def init_formatTempl(cls, arg_str, arg_templ=None):

        if not arg_templ: arg_templ = cls._optionStr.get_str_asDefault()

        if isinstance(arg_str, str) and isinstance(arg_templ,str):            
            s_templ = cls.formatTempl(arg_templ)
            arg_str = s_templ + arg_str
        else:
            raise ValueError('Type_value.init_formatTempl arg_str or arg_templ'+ cls._str_error_type)   

        return arg_str

    # Строковый идентификатор Type_value
    @classmethod
    def get_str_type(cls, arg_cls):
        if arg_cls.is_empty:            return 'is_empty'
        elif arg_cls.is_empty_dict:     return 'is_empty_dict'
        elif arg_cls.is_empty_list:     return 'is_empty_list'
        elif arg_cls.is_empty_model:    return 'is_empty_model'

        elif arg_cls.is_dict       :    return 'is_dict %s' % str(arg_cls.optionDict)

        #elif arg_cls.is_simpl_dict:     return 'is_simpl_dict'
        #elif arg_cls.is_multi_dict:     return 'is_multi_dict'

        elif arg_cls.is_list:           return 'is_list'
        elif arg_cls.is_int:            return 'is_int'
        elif arg_cls.is_str:            return 'is_str ' + str(arg_cls.optionStr)
        elif arg_cls.is_model_user:     return 'is_model_user'
        elif arg_cls.is_model_advuser:  return 'is_model_advuser'
        
        else: return 'unknown_type'

    @classmethod
    def _proc_dict(cls, arg_dict):
        res = cls()
        res.is_dict = True

        _len = len(list(arg_dict.keys()))
        if not _len :
            res.optionDict = cls._optionDict(empty=True)
            return 

        _oneMulti =  arg_dict.get(cls.Option_oneMulti.get_str_oneMulti())

        if _len == 1: 
            if _oneMulti:
                res.optionDict = cls._optionDict(arg_oneMulti=True)
            else:
                key = list(arg_dict.keys())[0]
                if isinstance(arg_dict[key], list ):
                    res.optionDict = cls._optionDict(arg_oneList=True)
                else:
                    res.optionDict = cls._optionDict(arg_oneSimple=True)
        else:                
            res.optionDict = cls._optionDict(arg_multiKeys=True)
        
        if _oneMulti:
            res.optionDict.oneMulti_as_one = False

        return res

    @classmethod
    def _proc_str(cls, arg_str):
        res = cls()
        res.is_str = True
        res.optionStr = cls._optionStr(arg_str) # определение типа строки 

        return res

    @classmethod
    def _proc_ext_dict(cls):
        res = cls()
        res.is_Ext_dict = True
        return res

    @classmethod
    def optionStr_oneMulti(cls,arg_dict): return cls.Option_oneMulti.get_str_oneMulti()

    @classmethod
    def _proc_list(cls, arg_list):
        res = cls()
        if not arg_list:
            res.is_empty_list = True
        else:
            res.is_list = True

        return res


    @classmethod
    def _proc_int(cls, arg_int):
        res = cls()
        if not arg_int:
            res.is_empty = True
        else:
            res.is_int = True
        return res

    @classmethod
    def _proc_advuser(cls, arg_model):
        res = cls()
        res.is_model_advuser = True
        return res

    @classmethod
    def _proc_user(cls, arg_model):
        res = cls()
        res.is_model_user = True
        return res


    @classmethod
    def _proc_ext_set(cls, arg_set):
        res = cls()        
        res.is_set = True        
        return res

    @classmethod
    def type_value(cls, arg_value):
        from .Ext_dict import Ext_dict
        from advuser.models import AdvUser
        from django.contrib.auth.models import User

        if not arg_value: 
            res = cls()
            res.is_empty = True
            return res

        if isinstance(arg_value, dict):
            return cls._proc_dict(arg_value)
        elif isinstance(arg_value, set):
            return cls._proc_ext_set(arg_value)
        elif isinstance(arg_value, list):
            return cls._proc_list(arg_value)
        elif isinstance(arg_value, str):
            return cls._proc_str(arg_value)
        elif isinstance(arg_value, int):
            return cls._proc_int(arg_value)
        elif isinstance(arg_value, AdvUser):
            return cls._proc_advuser(arg_value)
        elif isinstance(arg_value, User):
            return cls._proc_user(arg_value)
        elif isinstance(arg_value, Ext_dict):
            return cls._proc_ext_dict()
        else:
            res = cls()
            res.unknown_type = True
            return res

    #---------- Конец блока @classmethod ----------

    def __init__(self):
        self.unknown_type = None
        self.optionDict   = None
        self.optionStr    = None

        self.is_empty = None
        self.is_empty_dict = None
        self.is_empty_list = None
        self.is_empty_model = None

        self.is_dict       = None
        #self.is_simpl_dict = None
        #self.is_multi_dict = None
        self.is_list = None
        self.is_set = None

        self.is_int  = None
        self.is_str  = None

        self.is_model_user = None
        self.is_model_advuser = None

        self.is_Ext_dict = None


