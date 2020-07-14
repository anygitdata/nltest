# Generated by Django 2.2.12 on 2020-06-17 09:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='MesSubject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('strSubject', models.CharField(max_length=50, verbose_name='Тема сообщения')),
            ],
            options={
                'verbose_name': 'Тема',
                'verbose_name_plural': 'Темы сообщений',
            },
        ),
        migrations.CreateModel(
            name='SprStatus',
            fields=[
                ('status', models.CharField(max_length=9, primary_key=True, serialize=False, verbose_name='Статус')),
                ('strIdent', models.CharField(max_length=50, verbose_name='СтрокИдентификатор')),
                ('levelperm', models.SmallIntegerField(default=10, null=True, verbose_name='Уровень доступа')),
                ('exp_param', models.CharField(max_length=500, null=True, verbose_name='Конвертор status fot strFor_progr')),
                ('any_option', models.CharField(max_length=1500, null=True, verbose_name='Опции правСоздания профиля')),
            ],
        ),
        migrations.CreateModel(
            name='AdvUser',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('advData', models.TextField(max_length=500, verbose_name='ДопДанные')),
                ('phone', models.CharField(blank=True, max_length=15, null=True, verbose_name='Телефон')),
                ('sendMes', models.BooleanField(blank=True, null=True, verbose_name='ПолучатьСообщ')),
                ('dateBeginLogin', models.DateField(auto_now_add=True, verbose_name='НачДатаЛогина')),
                ('dateEndLogin', models.DateField(default='2100-01-01', verbose_name='КонДатаЛогина')),
                ('ageGroup', models.IntegerField(blank=True, null=True, verbose_name='Возраст')),
                ('post', models.IntegerField(blank=True, null=True, verbose_name='ПочтИндекс')),
                ('pol', models.CharField(blank=True, default='-', max_length=1, null=True, verbose_name='Пол')),
                ('js_struct', models.CharField(default='{}', max_length=300)),
                ('parentuser', models.ForeignKey(db_column='parentuser', on_delete=django.db.models.deletion.PROTECT, related_name='parentuser', to=settings.AUTH_USER_MODEL, to_field='username')),
                ('status', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='advuser.SprStatus', verbose_name='Статус')),
            ],
            options={
                'verbose_name': 'РасшДанные',
                'verbose_name_plural': 'РасшДанныеПользователей',
            },
        ),
    ]
