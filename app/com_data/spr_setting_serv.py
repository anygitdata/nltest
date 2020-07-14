



"""
сервис обработки сценариев, связанных с логированием

связан с spr_setting
"""
class serv_loggin:
    import os
    from os import path
    from nltest import settings
    from collections import namedtuple
    import datetime


    _arg_param_loggin = 'loggin'
    _logginFile_asDefault = 'loggin_default.log'

    
    """
    12.05.2020 testing:
        file: tests/app/models/spr_setting/test_serv_loggin.json
        modul: test_serv_loggin
        procedure: read_logginParam
    ------------------------------------------------------------------
    return res_path_log         #Строковый идентификатор файла loggin.log

    """
    @classmethod
    def read_logginParam(cls):
        Nm_paramPath = cls.namedtuple('Nm_paramPath', 'count_files, max_size, base_dir, path')

        paramPath = None      # namedtuple основных параметров из settings
        dict_param_log = {} # dict с параметрами по последнимФайлам и начальнымФайлам
        res_path_log = ''   # результирующий path *.log для использования 
        num_count = 0       # общее кол-во файлов

        # ----------- Процедурный блок обработки данных *.log файлов --------------
        # иницилизация основных параметров
        def _init_paramParh():

            nonlocal paramPath

            count_files_loggin = cls.settings.VALUE_COUNT_FILES_LOGGIN
            size_loggin_file   = cls.settings.MAX_NUMBER_SIZE_FILE_LOGGIN

            base_dir = cls.settings.BASE_DIR        
            s_path = cls.path.normcase('app/loggin')
            s_dir = cls.path.join(base_dir, s_path)

            # инициализация данных path размещения файлов логгирования
            paramPath = Nm_paramPath(count_files_loggin, size_loggin_file, base_dir, s_dir)

        # инициализация списка файлов *.log
        def _proc_lstFiles():
            import sys

            nonlocal num_count, dict_param_log, paramPath

            s_dir = paramPath.path
            lst_files = cls.os.listdir(paramPath.path)
            
            secdMax = 0
            secdMin = sys.maxsize
            _num = 0    # счетчик кол-ва файлов
            for s_file in lst_files:  # s_file стрИдентификатор файла
                spl_text = cls.path.splitext(s_file)    # тип файла
                if spl_text[1] != '.log': continue      # выборка файлов типа *.log
                
                path_file = cls.path.join(s_dir, s_file)    # полный path файла *.log
                secd = int(cls.path.getmtime(path_file))    # время в сек с начала расчетногоПериода (2020 года)

                sizeFile = cls.path.getsize(path_file)
                if secdMax < secd: 
                    dict_param_log.update(
                        dict(
                            secdMax     = secd,     # время последнего обновления                            
                            sizeMax     = sizeFile,
                            pathMax     = path_file
                            )
                        )
                    secdMax = secd

                
                if secdMin > secd:
                    dict_param_log.update(
                        dict(
                                secdMin     = secd,     # время последнего обновления                                
                                sizeMin     = sizeFile,
                                pathMin     = path_file
                                )
                            )
                    secdMin = secd
                
                _num +=1

            num_count = _num

        # получение файла   res_path_log =*.log   завершающая процедура 
        def _init_path_log():

            nonlocal dict_param_log, res_path_log, paramPath

            if dict_param_log.get('sizeMax') < paramPath.max_size:
                res_path_log = dict_param_log['pathMax']

            else:

                dt = cls.datetime.datetime.now()
                s_path_remove = dict_param_log['pathMin']
                file_path = 'log_{0}-{1}-{2}_{3}{4}{5}.log'.format(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)

                file_path = cls.path.join(paramPath.path, file_path)
                # вставить новый файл *.log
                with open(file_path,'w', encoding='utf-8') as file:
                    file.write('')
                    
                    if num_count >= paramPath.count_files:
                        cls.os.remove(s_path_remove)
                
                res_path_log = file_path

        #------------ Конец процедурного блока -------------
        

        _init_paramParh()   # инищиализация основных параметров
        _proc_lstFiles()    # обработка списка файлов *.log
        _init_path_log()    # получение path файла *.log


        return res_path_log


    """
    12.05.2020 testing:
        file: tests/app/models/spr_setting/test_serv_loggin.json
        modul: test_serv_loggin
        procedure: get_actual_logginFile
    ----------------------------------------------------------------
    Логика определения файла логгирования
    изменена:
        поиск и обработка ведется через файловую систему
        условия отбора заложены в процедуре cls.read_logginParam()
            - поиск последенего log
            - определение размера
            - создание нового файла или использование последнего
            - удаление самого раннего, если кол-во файлов превышает допустимое
              cls.settings.VALUE_COUNT_FILES_LOGGIN

    Процедура оставлена для совместимости с раннее введенной обработкой
    """
    @classmethod
    def get_actual_logginFile(cls):

        s_file = None
        try:
            s_file = cls.read_logginParam()

        except :
            s_file = cls._logginFile_asDefault

        return s_file  


    

