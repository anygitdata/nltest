
"""
 Модуль prtesting.views 
"""


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


from app import get_valFromDict

from .forms import TestingForm
from .any_mixin import Params_testing



"""
Контроллер проведения тестов
url prtest/
"""
@login_required
def PrTest(request):
    if not request.user.is_superuser:
        return redirect('notperm')

    par_testing = Params_testing()

    if request.method == 'POST':
        

        res_proc = TestingForm.SelectFilesTesting(par_testing)        
        form = TestingForm( initial=dict(script=par_testing.PR_base_directory))

        context = dict(res=res_proc.res, form=form, files=par_testing.PR_files)

        if res_proc.res < 0:
            context.update(error=res_proc.error)
        else:
            context.update(res_test=res_proc.res_list)

        return render(request, 'prtesting/index.html', context )


    else:

        form = TestingForm( initial=dict(script=par_testing.PR_base_directory))
        return render(request, 'prtesting/index.html', 
                      dict(
                          files=par_testing.PR_files , 
                          res=0, # код начальной загрузки формы тестирования
                          form=form
                          ))

    

