(function () {
    var word;

    var timerForTypeahead = null;
    var $addPieceWap = $('.add-piece-wap');
    var $btnAddPiece = $('.btn-add-piece');
    var $btnCancelAddPiece = $('.btn-cancel-add-piece');

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
    $btnSubmitPiece.click(function () {
        var explanation = $.trim($explanationTextarea.val());
        var sentence = $.trim($sentenceTextarea.val());

        $.ajax({
            url: urlFor('piece.add'),
            method: 'post',
            dataType: 'json',
            data: {
                word: word,
                content: explanation,
                sentence: sentence
            }
        }).done(function (response) {
            if (response.result) {
                window.location = urlFor('site.pieces', {piece_id: response.piece_id});
            }
        });
    });

    // 添加例句
    $btnAddSentence.click(function () {
        $addPieceWapSecondStep.addClass('add-sentence');
        $sentenceTextarea.focus();
    });

    /**
     * 打开 add piece wap
     */
    function openAddPieceWap(word, callback) {
        resetAddPieceWapContent();

        $addPieceWap.show();

        if (typeof word !== 'undefined') {
            $wordInput.typeahead('val', word);
            $titleInFirstStep.text('给老词添加一条解释');
        }

        $('.twitter-typeahead').css({
            'display': 'block',
            'height': $wordInput.outerHeight()
        });

        $wordInput.focus();

        adjustAddPieceWapContentPosition();

        $addPieceWap.animate({
            'opacity': '1',
            'left': '0',
            'right': '0',
            'top': '0',
            'bottom': '0'
        }, 100, function () {
            if (typeof callback !== 'undefined') {
                callback();
            }
        });
    }

    /**
     * 重置 add piece wap
     */
    function resetAddPieceWapContent() {
        $wordInput.val('');
        $wordInSecondStep.empty();
        $titleInFirstStep.text('创建新词条');
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

    window.openAddPieceWap = openAddPieceWap;
})();
