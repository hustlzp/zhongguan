(function () {
    var word;

    var $btnAddPieceFromIndex = $('.btn-add-piece-from-index');

    var timerForTypeahead = null;
    var $addPieceWap = $('.add-piece-wap-in-index-page');

    var $addPieceWapFirstStep = $addPieceWap.find('.first-step');
    var $wordInput = $addPieceWapFirstStep.find('input');
    var $btnGoToSecondStep = $('.btn-go-to-second-step');
    var $titleInFirstStep = $addPieceWapFirstStep.find('.title');

    var $addPieceWapSecondStep = $addPieceWap.find('.second-step');
    var $btnSubmitPiece = $addPieceWapSecondStep.find('.btn-submit-piece');
    var $btnAddSentence = $addPieceWapSecondStep.find('.btn-add-sentence');
    var $explanationTextarea = $addPieceWapSecondStep.find('.explanation-textarea');
    var $sentenceTextarea = $addPieceWapSecondStep.find('.sentence-textarea');
    var $wordInSecondStep = $addPieceWapSecondStep.find('.word');

    $btnAddPieceFromIndex.click(function () {
       $(window).scrollTo($addPieceWap, 200);
    });

    // 启动Typeahead自动完成
    $wordInput.typeahead({
        minLength: 1,
        highlight: true,
        hint: false
    }, {
        displayKey: 'value',
        source: function (q, cb) {
            if (timerForTypeahead) {
                clearTimeout(timerForTypeahead);
            }

            timerForTypeahead = setTimeout(function () {
                $.ajax({
                    url: urlFor('word.query'),
                    method: 'post',
                    dataType: 'json',
                    data: {
                        q: q
                    }
                }).done(function (matchs) {
                    cb(matchs);
                });
            }, 300);
        },
        templates: {
            'suggestion': function (data) {
                return '<span>' + data.value + '</span>';
            }
        }
    });

    $('.twitter-typeahead').css({
        'display': 'block',
        'height': $wordInput.outerHeight()
    });

    // 选择autocomplete菜单项完成添加
    $wordInput.on('typeahead:selected', function (e, collection) {
        $titleInFirstStep.text('给老词添加一条解释');
    });

    // 进入第二步
    $btnGoToSecondStep.click(function () {
        word = $.trim($wordInput.val());

        if (word) {
            $addPieceWap.removeClass('first').addClass('second');
            $wordInSecondStep.text(word);
            $explanationTextarea.focus();
        }
    });

    // 提交
    //$btnSubmitPiece.click(function () {
    //    var explanation = $.trim($explanationTextarea.val());
    //    var sentence = $.trim($sentenceTextarea.val());
    //
    //    $.ajax({
    //        url: urlFor('piece.add'),
    //        method: 'post',
    //        dataType: 'json',
    //        data: {
    //            word: word,
    //            content: explanation,
    //            sentence: sentence
    //        }
    //    }).done(function (response) {
    //        if (response.result) {
    //            window.location = urlFor('site.index', {piece_id: response.piece_id});
    //        }
    //    });
    //});

    // 添加例句
    $btnAddSentence.click(function () {
        $addPieceWapSecondStep.addClass('add-sentence');
        $sentenceTextarea.focus();
    });
})();
