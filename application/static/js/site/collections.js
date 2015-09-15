var $mainWap = $('#main-wap');
var $currentSelectorOuterWap = $mainWap.find('.current-selector-outer-wap');
var $currentSelectorWap = $currentSelectorOuterWap.find('.current-selector-wap');
var $selectorsOuterWap = $mainWap.find('.selectors-outer-wap');
var $selectorsWap = $selectorsOuterWap.find('.selectors-wap');

//console.log($currentSelectorWap.outerHeight());
$currentSelectorOuterWap.height($currentSelectorWap.outerHeight() - 1);
$currentSelectorWap.css({
    'left': ($currentSelectorOuterWap.outerWidth() - $currentSelectorWap.outerWidth()) * 0.5,
    'visibility': 'visible'
});
$selectorsWap.css('left', ($selectorsOuterWap.outerWidth() - $selectorsWap.outerWidth()) * 0.5);
