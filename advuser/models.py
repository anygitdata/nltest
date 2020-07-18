
import datetime
import json 
from django.db import models


class Templ_buf(models.Model):
    from django.contrib.auth.models import User

    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    parentuser = models.CharField(max_length=150) 
    advData = models.TextField(max_length=500)
    js_struct  = models.CharField(max_length=300, default='{}')


class SprStatus(models.Model):
    status = models.CharField( primary_key=True, max_length=9, verbose_name='Статус' )
    strIdent = models.CharField( max_length=50, verbose_name='СтрокИдентификатор')
    levelperm = models.SmallIntegerField(verbose_name='Уровень доступа', null=True, default=10)    
    exp_param = models.CharField( max_length=500, verbose_name='Конвертор status fot strFor_progr', null=True)
    any_option = models.CharField(max_length=1500, verbose_name='Опции правСоздания профиля', null=True)


    @property
    def PR_strStatus(self):
        s_res = '{0}:{1} levelperm:{2}'.format(self.pk, self.strIdent, self.levelperm)

        return s_res


    def __str__(self):
        return self.strIdent
        

class AdvUser(models.Model):
    from django.contrib.auth.models import User

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    advData = models.TextField(max_length=500, verbose_name='ДопДанные')
    phone = models.CharField(max_length=15, verbose_name='Телефон', blank=True, null=True)
    status = models.ForeignKey('SprStatus', on_delete=models.CASCADE, verbose_name='Статус')
    sendMes = models.BooleanField(verbose_name='ПолучатьСообщ', blank=True,  null=True)
    dateBeginLogin = models.DateField(verbose_name='НачДатаЛогина', auto_now_add=True )
    dateEndLogin = models.DateField(verbose_name='КонДатаЛогина', default='2100-01-01')
    ageGroup = models.IntegerField(verbose_name='Возраст', null=True, blank=True)    
    parentuser = models.ForeignKey(User, related_name='parentuser', to_field='username', on_delete=models.PROTECT, db_column='parentuser')
    post       = models.IntegerField( verbose_name='ПочтИндекс', null=True, blank=True)
    pol        = models.CharField(verbose_name='Пол', max_length=1, null=True, blank=True, default='-' )
    js_struct  = models.CharField(max_length=300, default='{}')

    class Meta:
        verbose_name_plural = 'РасшДанныеПользователей'
        verbose_name = 'РасшДанные'


# Модель темы сообщений
class MesSubject(models.Model):
    strSubject = models.CharField( max_length=50, verbose_name='Тема сообщения' )

    def __str__(self):        
        return self.strSubject

    class Meta:
        verbose_name_plural = 'Темы сообщений'
        verbose_name = 'Тема'

