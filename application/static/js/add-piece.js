var $addPieceWap = $('.add-piece-wap');
var $btnAddPiece = $('.btn-add-piece');
var $btnCancelAddPiece = $('.btn-cancel-add-piece');

var $addPieceWapFirstStep = $addPieceWap.find('.first-step');
var $wordInput = $addPieceWapFirstStep.find('input');
var $btnGoToSecondStep = $('.btn-go-to-second-step');

var $addPieceWapSecondStep = $addPieceWap.find('.second-step');
var $btnSubmitPiece = $addPieceWapSecondStep.find('.btn-submit-piece');
var $btnAddSentence = $addPieceWapSecondStep.find('.btn-add-sentence');
var $explanationTextarea = $addPieceWapSecondStep.find('.explanation-textarea');
var $sentenceTextarea = $addPieceWapSecondStep.find('.sentence-textarea');

// 打开添加词条wap
$btnAddPiece.click(function () {
    openAddPieceWap();
});

// 关闭添加词条wap
$btnCancelAddPiece.click(function () {
    closeAddPieceWap();
});

// 按下Esc，关闭backdrop
$(document).keydown(function (e) {
    if (e.keyCode == 27) {
        closeAddPieceWap();
    }
});

// 进入第二步
$btnGoToSecondStep.click(function () {
    $addPieceWap.removeClass('first').addClass('second');
});

// 提交
$btnSubmitPiece.click(function () {
    closeAddPieceWap();
});

// 添加例句
$btnAddSentence.click(function () {
    $addPieceWapSecondStep.addClass('add-sentence');
});

/**
 * 打开 add piece wap
 */
function openAddPieceWap() {
    resetAddPieceWapContent();

    $addPieceWap.show();

    $wordInput.focus();

    adjustAddPieceWapContentPosition();

    $addPieceWap.animate({
        'opacity': '1',
        'left': '0',
        'right': '0',
        'top': '0',
        'bottom': '0'
    }, 100, function () {

    });
}

/**
 * 重置 add piece wap
 */
function resetAddPieceWapContent() {
    $wordInput.val('');
    $addPieceWap.addClass('first').removeClass('second');
    $addPieceWapSecondStep.removeClass('add-sentence');
    $explanationTextarea.val('');
    $sentenceTextarea.val('');
}

/**
 * 调整 add piece wap 内容
 */
function adjustAddPieceWapContentPosition() {
    var windowHeight = $(window).height();
    var firstStepHeight = $addPieceWapFirstStep.height();
    var secondStepHeight = $addPieceWapSecondStep.height();

    $addPieceWapFirstStep.css('marginTop', (windowHeight - firstStepHeight) * 0.4);
    $addPieceWapSecondStep.css('marginTop', (windowHeight - secondStepHeight) * 0.4);
}

/**
 * 关闭 add piece wap
 */
function closeAddPieceWap() {
    $addPieceWap.animate({
        'opacity': '0.5',
        'left': '40px',
        'right': '40px',
        'top': '40px',
        'bottom': '40px'
    }, 100, function () {
        $(this).hide();
    });
}
