from django.urls import path

from .views import (Index, AddProf_member, AddProf_quest, UpdProf_quest, Success_register_user, 
                    AdvPanel_prof, List_profils, Redir_upd_prof_listProf, Modf_prof_byheader, 
                    Redir_updprof, Modf_prof_byuser, UpdPassword_user, UpdPsw_byUser,
                    Filter_data_profil, UpdStatus_user)

urlpatterns = [

    # -------- path администрирования ----------------
    # Административная панель #  header_panel.html;  AdvPanel_profForm
    # redirect  updprofiluser, updpswuser, updpermuser, 
    path('modpanelprof/', AdvPanel_prof, name='modpanelprof'),


    # перенаправление на обновление профиля из списка менеджеров 
    # redirect  updprofiluser
    path('updmesdata<str:mes>', Redir_upd_prof_listProf, name='updmesdata'),


    # Изменение пароля рукГрупп
    # изменение пароля участника проекта  # upd_password_user.html; UpdPassword_byHeadForm
    path('updpswuser', UpdPassword_user, name='updpswuser'),


    # Изменение пароля самими пользователями # upd_password_by_user.html; UpdPsw_byUserForm
    path('updpswbyUser', UpdPsw_byUser, name='updpswbyUser'),

    # Изменений привилегий status_id. Только для рукГрупп #upd_status_user.html; UpdStatus_userForm
    path('updpermuser', UpdStatus_user, name='updpermuser'),

    
    # Создание профиля участника проекта    
    # regUser_ext.html;  AddProf_memberForm
    path('addprof_member/', AddProf_member, name='addprof_member'),


    # path с использование cache
    # Для рукГрупп -> изменение профиля участников проекта # regUser_ext.ntml; Modf_prof_byHeaderForm
    path('updprofiluser/', Modf_prof_byheader, name='updprofiluser' ),


    #  regUser_ext.html; Modf_prof_byuserForm
    path('modf_prof_byuser/', Modf_prof_byuser, name='modf_prof_byuser'),


    # Создание профиля клиентов   # regUser_ext.html;  Base_profForm
    path('addprofquest/', AddProf_quest, name='addprofquest'),


    # Изменение профиля клиентов  # regUser_ext.html; Base_profForm
    path('updprofquest/', UpdProf_quest, name='updprofquest'),
    

    # Перенаправление для изменения профиля:  addprofquest/updprofquest or modf_prof_byuser
    path('redirupdprof/',Redir_updprof, name='redirupdprof' ), 

    # отображение результатов регистрации клиента на сайте
    #     prof_conf_modf.html; 
    path('ver_profil/', Success_register_user, name='ver_profil'),


    # prof_table_format.html; ->  отображение списка структуры менеджеров
    #path('listprofils/', List_profils, name='listprofils'),
    path('listprofils/<str:page>/<str:filter>', List_profils, name='listprofils'),


    path('filterlvlperm/', Filter_data_profil, name='filterlvlperm'),

    path('', Index, name='index'),


    ]