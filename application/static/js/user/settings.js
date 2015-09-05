$("input[type='checkbox']").change(function () {
    var key = $(this).data('key');

    $.ajax({
        url: urlFor('user.toggle_setting', {key: key}),
        method: 'post',
        dataType: 'json'
    }).done(function (response) {
        if (response.result) {
            $(this).prop("checked", response.settings_result);
        } else {
            $(this).prop("checked", !$(this).prop("checked"));
        }
    });
});
