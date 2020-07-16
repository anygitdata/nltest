
(function ($) {
    // *********** модуль обработки интерактивного интерфейса status_id ************

    /* { limitcon30: 10, limitcon: 50, limitcon40: 5, limitcon70: 1 lvperm: } */
    var limitcon = JSON.parse($('#s_limit').html());
    $('#s_limit').remove();  // удаление div  с исходными данными 


    // **************** Блок начальной инициализации  input object  ***************
    var id_limitcon30 = $('#id_limitcon30').val();  
    var id_limitcon   = $('#id_limitcon').val();  
    var id_limitcon40 = $('#id_limitcon40').val();
    var id_limitcon70 = $('#id_limitcon70').val();

    var id_status = $('#id_status').val();      // исходное значение select => status_id
    var lvperm_select = get_lvperm(id_status);  // исходное значение levelperm
    // ****************************************************************************
    

    // *************** присвоение начальных значений input object ******************
    if (id_limitcon30 == null || id_limitcon30 == 0) $('#id_limitcon30').val(limitcon.limitcon30); 

    if (id_limitcon == null || id_limitcon == 0)     $('#id_limitcon').val(limitcon.limitcon); 

    if (id_limitcon40 == null || id_limitcon40 == 0) $('#id_limitcon40').val(limitcon.limitcon40); 

    if (id_limitcon70 == null || id_limitcon70 == 0) $('#id_limitcon70').val(limitcon.limitcon70); 

    // ************************************************


    // определение levelperm, значений из select object 
    function get_lvperm(par) {

        var index, res, arr, data;
        arr = limitcon.lvperm;

        for (index = 0; index < arr.length; ++index) {
            data = arr[index];
            if (data.status === par) {
                res = data.lvperm;
                break;
            }
        }

        return res;
    }

    // Обработчик события измСтатуса
    $('#id_status').change(function (e) {           

        var sel = $(e.target).val();

        $('.limitcon30').hide();
        $('.limitcon').hide();
        $('.limitcon40').hide();
        $('.limitcon70').hide();

        switch (sel) {
            case 'subheader':
                $('.limitcon30').show();                
                break;
            case 'headerexp':                
                $('.limitcon').show();
                $('.limitcon40').show();
                $('.limitcon70').show();
                break;
        }

        //console.log('Изменение status: ' + $(e.target).val());
        e.stopPropagation();
    });

    $("#id_status").trigger("change");  // запуск триггера на обновление полей input limitcon


    // ***********************************************
    //console.log(lvperm_select);

    // обработка изменений в БД


}(jQuery));