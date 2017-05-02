var exclude_div1 = $('#exclude-div1');
var exclude_manage1 = $('#exclude-manage1');
var exclude_button = $('#exclude-button');
var exclude_div2 = $('#exclude-div2');
var exclude_manage2 = $('#exclude-manage2');
var exclude_div3 = $('#exclude-div3');
var exclude_manage3 = $('#exclude-manage3');
var submit_button = $('#_submit');

exclude_button.click(function () {
    submit_button.click()
});

// 自定义时间差
var delta_ranks_slect = $('#delta-ranks-selected');
var delta_custom = $('#delta-custom1');
var cache = delta_ranks_slect.val(), count = 0;
// delta_ranks_slect.change(function () {
//     if (delta_ranks_slect.val() < 10) {
//         $('#submit_delta_tank').click();
//     } else {
//         alert(delta_ranks_slect.val());
//         alert(delta_custom.css('display'));
//         if (delta_custom.css('display') == 'none') {
//             delta_custom.css('display', 'block')
//         }
//     }
// });
delta_ranks_slect.click(function () {
    var $this = $(this), sel;
    // just for testing purpose
    // if a click has preceeded the current click, execute comparison function
    if (count === 1) {
        // store the textvalue of the current option
        sel = delta_ranks_slect.val();
        // if current value !== previous option's textvalue, do...
        if (delta_ranks_slect.val() < 10) {
            $('#submit_delta_tank').click();
        } else {
            if (delta_custom.css('display') == 'none') {
                delta_custom.css('display', 'block')
            }
        }
        // reset count
        count--;
    } else {
        cache = delta_ranks_slect.val();
        count++;
    }
});

$(document).click(function (event) {
    if (
        !delta_ranks_slect.is(event.target) && delta_ranks_slect.has(event.target).length === 0 && !delta_custom.is(event.target) && delta_custom.has(event.target).length === 0
    ) { // Mark 1
        if (delta_custom.css('display') == 'block') {
            delta_custom.hide(500);     //淡出消失
            delta_ranks_slect.val(cache);
            delta_ranks_slect.children('option').each(function () {
                // if($(this).val() == cache){
                //
                // }
            })
        }

    }
});


exclude_manage1.click(function () {
    if (exclude_div1.css('display') == 'none') {
        exclude_div1.css('display', 'block')
    } else {
        exclude_div1.css('display', 'none')
    }
});

$(document).click(function (event) {
    if (
        !exclude_manage1.is(event.target) && exclude_manage1.has(event.target).length === 0 && !exclude_div1.is(event.target) && exclude_div1.has(event.target).length === 0
    ) { // Mark 1
        exclude_div1.hide(500);     //淡出消失
    }
});

exclude_manage2.click(function () {
    if (exclude_div2.css('display') == 'none') {
        exclude_div2.css('display', 'block')
    } else {
        exclude_div2.css('display', 'none')
    }
});

$(document).click(function (event) {
    if (
        !exclude_manage2.is(event.target) && exclude_manage2.has(event.target).length === 0 && !exclude_div2.is(event.target) && exclude_div2.has(event.target).length === 0
    ) { // Mark 1
        exclude_div2.hide(500);     //淡出消失
    }
});

exclude_manage3.click(function () {
    if (exclude_div3.css('display') == 'none') {
        exclude_div3.css('display', 'block')
    } else {
        exclude_div3.css('display', 'none')
    }
});

$(document).click(function (event) {
    if (
        !exclude_manage3.is(event.target) && exclude_manage3.has(event.target).length === 0 && !exclude_div3.is(event.target) && exclude_div3.has(event.target).length === 0
    ) { // Mark 1
        exclude_div3.hide(500);     //淡出消失
    }
});

//恢复项目时的全选
$('.all-exclude').click(function () {
    var children_checkboxes = $(this).closest('.exclude-div').find('input[name="recover_check"]');
    if ($(children_checkboxes[0]).prop('checked') == false) {
        children_checkboxes.each(function () {
            $(this).prop("checked", "checked");
        })
    } else {
        children_checkboxes.each(function () {
            $(this).removeAttr('checked')
        })
    }
});


// 排除时的选择
$('input[name="all_check"]').click(function () {
    var children_checkboxes = $(this).closest('#check_table').find('input[name="exclude_check"]');
    if ($(this).prop('checked') == true) {
        $(this).attr("checked", true);
        children_checkboxes.each(function () {
            $(this).prop("checked", "checked");
        })
    } else {
        $(this).attr("checked", false);
        children_checkboxes.each(function () {
            $(this).removeAttr('checked')
        })
    }
});

$('input[name="exclude_check"]').click(function () {
    var parent_checkbox = $(this).closest('#check_table').find('input[name="all_check"]');
    var children_checkboxes = $(this).closest('#check_table').find('input[name="exclude_check"]');
    var checked_num = 0;
    children_checkboxes.each(function () {
        if ($(this).prop('checked') == true) {
            checked_num += 1
        }
    });
    if (checked_num == children_checkboxes.length) {
        parent_checkbox.prop("checked", "checked");
    } else {
        parent_checkbox.removeAttr('checked')
    }
});