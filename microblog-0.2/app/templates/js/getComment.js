/**
 * use by statusChange.html.
 */
var $SCRIPT_ROOT = {{request.script_root | tojson | safe}};
$(document).ready(function () {
    $("calculate").click(function() {
        $.ajax({url: $SCRIPT_ROOT + '/add',
                contentType: "application/json; charset=UTF-8",
                dataType: 'json',
                data:{
                    a: $('input[name="a"]').val(),
                    b: $('input[name="b"]').val(),
                    now: new Date().getTime()
                },
                error: function(xhr, err){ $('#result').text(err); },
                success: function(data, textStatus){ $('#result').text(data.comment); }
        });
    })
});