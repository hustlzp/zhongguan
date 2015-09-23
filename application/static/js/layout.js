// Add csrf token header for Ajax request
$.ajaxSetup({
    beforeSend: function (xhr, settings) {
        if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type)) {
            xhr.setRequestHeader("X-CSRFToken", g.csrfToken);
        }
    }
});

// Flash message
setTimeout(showFlash, 200);
setTimeout(hideFlash, 2000);

$('.notification-dropdown-toggle').click(function () {
    $(this).find('.notifications-count').text('0');

    $.ajax({
        url: urlFor('user.check_all_notifications'),
        method: 'post'
    });
});

$('.notifications-in-nav .noti').click(function () {
    var pieceId = $(this).data('piece-id');

    window.location = urlFor('site.pieces', {piece_id: pieceId});
});

// 顶句子
$(document).on('click', '.vote', function () {
    var pieceId = parseInt($(this).attr('data-piece-id')),
        url = "",
        voted = $(this).hasClass('voted'),
        _this = $(this);

    if (voted) {
        url = urlFor('piece.unvote', {uid: pieceId});
    } else {
        url = urlFor('piece.vote', {uid: pieceId});
    }

    // 点击后立即出发效果
    toggleVoteEffect(_this);

    $.ajax({
        url: url,
        method: 'post',
        dataType: 'json'
    }).done(function (response) {
        if (!response.result) {
            toggleVoteEffect(_this);
        }
    }).fail(function () {
        toggleVoteEffect(_this);
    });
});

// 若某操作需要登录，而用户尚未登录，则跳转登录页
$('.need-signed-in').click(function () {
    if (!g.signedIn) {
        window.location = urlFor('site.index', {signin: 1});
        return false;
    }
});

$(document).on('click', '.need-signed-in', function () {
    if (!g.signedIn) {
        window.location = urlFor('site.index', {signin: 1});
        return false;
    }
});

// 激活tooltip
$(document).tooltip({
    selector: '[data-toggle="tooltip"]'
});

// 调整modal高度
$('.modal-need-adjust-height').on('show.bs.modal', function () {
    var _this = $(this);

    setTimeout(function () {
        var $dialog = _this.find(".modal-dialog");
        var offset;

        _this.css('display', 'block');
        offset = ($(window).height() - $dialog.height()) * 0.4;

        if (offset > 0) {
            $dialog.css('margin-top', offset);
        }
    }, 50);
});

/**
 * Show flash message.
 */
function showFlash() {
    $('.flash-message').slideDown('fast');
}

/**
 * Hide flash message.
 */
function hideFlash() {
    $('.flash-message').slideUp('fast');
}

/**
 * 切换vote效果
 * @param $voteElement
 */
function toggleVoteEffect($voteElement) {
    var voted = $voteElement.hasClass('voted');
    var pieceId = parseInt($voteElement.attr('data-piece-id'));
    var currentVotesCount = parseInt($voteElement.find('.votes-count').text());
    var targetVotesCount = 0;

    if (voted) {
        targetVotesCount = (currentVotesCount > 0) ? currentVotesCount - 1 : 0;
        $(".vote[data-piece-id=" + pieceId + "]")
            .removeClass('voted')
            .find('.votes-count').text(targetVotesCount);
    } else {
        targetVotesCount = currentVotesCount + 1;
        $(".vote[data-piece-id=" + pieceId + "]")
            .addClass('voted')
            .find('.votes-count').text(targetVotesCount);
    }
}
