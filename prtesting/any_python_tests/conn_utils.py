

# Функция возвращает connection.
def getConnection():
    import pymysql.cursors 

    DATABASES = {
       'default': {
            'ENGINE': 'django.db.backends.mysql',
            'HOST': '127.0.0.1',
            'USER': 'u0895627_suadm',
            'PASSWORD': 'ljdelfgjl!',
            'NAME': 'u0895627_nlproj'
            }
    }

    default_db = DATABASES['default'] 

    dict_con = dict(
        host=default_db['HOST'],
        user=default_db['USER'],
        passwd= default_db['PASSWORD'],
        database=default_db['NAME']
        )

    dict_con.update(dict(charset='utf8mb4',
                    cursorclass=pymysql.cursors.DictCursor))    

     
    # Вы можете изменить параметры соединения.
    connection = pymysql.connect(**dict_con)

    return connection
