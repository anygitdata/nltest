
from dataclasses import dataclass, field
from dataclasses import fields

@dataclass(frozen=True)
class D:
    s: str
    x: float = 10.0
    y: int = 5


class DD:

    _empty = 'empty'
    _fun=lambda : _empty


if __name__ == '__main__':

    #_s = DD._fun

    s = lambda: 'Строка из lambda'


    print(s())
    

    if 1>2:
        d = D('Значение поля s')
        print(d)


        n = D('Значение поля s')
        print('Сравнение двух объектов', d==n)

        for attr in fields(d):
            s_field = attr.name
            print(s_field )        

        print()
        try:
            d.x = 5
            print(d)
        except Exception as ex:
            print(str(ex))
