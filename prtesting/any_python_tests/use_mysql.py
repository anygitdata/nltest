"""
Использование возможности подключения к MySQL
"""



def con_db():
    
    from conn_utils import getConnection

    print('Подключение к локальной базе')
  
    try:
        con = getConnection()

        try:

            with con.cursor() as cur:

                # хранПРоцедура завершается оператором select * from TEMPORARY table
                cur.callproc('sp_row_advdata', (380,))

                for row in cur:  # вывод данных из хранПроцедуры
                    print( '{0:>3} {1:.<15} {2:<50}'.format(row['id_key'], row['js_key'], row['js_val']))

        except Exception as ex:
            print(str(ex))

        finally:
            con.close()

    except Exception as ex:
        print(str(ex))
        

if __name__ == '__main__':
    con_db()

