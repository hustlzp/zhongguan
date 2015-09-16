var $mainWap = $('#main-wap');
var $header = $mainWap.find('.header');
var $currentSelectorOuterWap = $mainWap.find('.current-selector-outer-wap');
var $currentSelectorWap = $currentSelectorOuterWap.find('.current-selector-wap');
var $selectorsOuterWap = $mainWap.find('.selectors-outer-wap');
var $selectorsWap = $selectorsOuterWap.find('.selectors-wap');

// 居中
$currentSelectorOuterWap.height($currentSelectorWap.outerHeight() - 1);
$currentSelectorWap.css({
    'left': ($currentSelectorOuterWap.outerWidth() - $currentSelectorWap.outerWidth()) * 0.5,
    'visibility': 'visible'
});
$selectorsWap.css('left', ($selectorsOuterWap.outerWidth() - $selectorsWap.outerWidth()) * 0.5);

// 交互
$currentSelectorWap.mouseenter(function () {
    $currentSelectorWap.addClass('on');
    $selectorsWap.css('display', 'inline-block');
});

$header.mouseleave(function () {
    $currentSelectorWap.removeClass('on');
    $selectorsWap.css('display', 'none');
});
