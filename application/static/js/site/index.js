(function () {
    var word = '';
    var content = '';
    var sentence = '';

    var windowHeight = $(window).outerHeight();
    var $firstScreen = $('.first-screen');
    var $secondScreen = $('.second-screen');
    var $firstStep = $('.first-step');
    var $secondStep = $('.second-step');
    var $footer = $secondScreen.find('.footer');

    // 尺寸调整
    $firstScreen.css('minHeight', windowHeight);
    $secondScreen.css('height', windowHeight);
    $firstStep.css('paddingTop', (windowHeight - $firstStep.outerHeight()) * 0.4).show();
    $footer.show();

    // 按需弹出登录框
    if (url('?signin')) {
        setTimeout(function () {
            $accountModal.modal();
            switchToSignin();
        }, 0);
    }

    /**
     * 注册与登录
     */

    var $btnOpenAccountModal = $('.btn-open-account-modal');

    var $accountModal = $('#account-modal');
    var $btnSubmitSignupForm = $('.btn-submit-signup-form');
    var $btnSubmitSigninForm = $('.btn-submit-signin-form');

    var $signinSignupWap = $('.signin-signup-wap');

    var $signupForm = $('.form-signup');
    var $nameInputInSignupForm = $signupForm.find("input[name='name']");
    var $passwordInputInSignupForm = $signupForm.find("input[name='password']");
    var $emailInputInSignupForm = $signupForm.find("input[name='email']");

    var $signinForm = $('.form-signin');
    var $emailInputInSigninForm = $signinForm.find("input[name='email']");
    var $passwordInputInSigninForm = $signinForm.find("input[name='password']");

    $btnOpenAccountModal.click(function () {
        $accountModal.modal();
    });

    // 弹出登录框
    $(document).on('click', '.btn-vote', function () {
        $accountModal.modal();
    });

    // 切换下一条
    $(document).on('click', '.btn-downvote', function () {
        $.ajax({
            url: urlFor('site.load_piece'),
            method: 'post'
        }).done(function (response) {
            if (response.result) {
                $('.piece-wap').html(response.piece_html);
                $('.piece-creator-info-wap').html(response.piece_creator_html);
            }
        });
    });

    // 注册
    $btnSubmitSignupForm.click(function () {
        var email = $.trim($emailInputInSignupForm.val());
        var password = $.trim($passwordInputInSignupForm.val());
        var name = $.trim($nameInputInSignupForm.val());

        $.ajax({
            url: urlFor('account.do_signup'),
            method: 'post',
            dataType: 'json',
            data: {
                name: name,
                email: email,
                password: password,
                word: word,
                content: content,
                sentence: sentence,
                'geetest_challenge': $('.geetest_challenge').val(),
                'geetest_validate': $('.geetest_validate').val(),
                'geetest_seccode': $('.geetest_seccode').val()
            }
        }).done(function (response) {
            if (response.result) {
                if (response.piece_id) {
                    window.location = urlFor('site.index', {piece_id: response.piece_id});
                } else {
                    window.location = urlFor('site.index');
                }

            } else {
                if (response.name !== "") {
                    showTip($nameInputInSignupForm, response.name);
                } else {
                    hideTip($nameInputInSignupForm);
                }

                if (response.email !== "") {
                    showTip($emailInputInSignupForm, response.email);
                } else {
                    hideTip($emailInputInSignupForm);
                }

                if (response.password !== "") {
                    showTip($passwordInputInSignupForm, response.password);
                } else {
                    hideTip($passwordInputInSignupForm);
                }
            }
        });
    });

    // 登录
    $btnSubmitSigninForm.click(function () {
        submitSigninForm();
    });

    $signupForm.find('input').keyup(function (event) {
        hideTip($(this));

        if ($.trim($emailInputInSignupForm.val()) !== ''
            && $.trim($nameInputInSignupForm.val()) !== ''
            && $.trim($passwordInputInSignupForm.val()) !== '') {
            $btnSubmitSignupForm.prop('disabled', false);
        } else {
            $btnSubmitSignupForm.attr('disabled', true);
        }
    });

    $signinForm.find('input').keyup(function () {
        hideTip($(this));

        if ($.trim($emailInputInSigninForm.val()) !== ''
            && $.trim($passwordInputInSigninForm.val()) !== '') {
            $btnSubmitSigninForm.prop('disabled', false);
        } else {
            $btnSubmitSigninForm.attr('disabled', true);
        }

        if (event.keyCode === 13) {
            submitSigninForm();
        }
    });

    $('.nav-tabs li a').click(function () {
        hideTip($signupForm.find('input'));
        hideTip($signinForm.find('input'));
    });

    function submitSigninForm() {
        var email = $.trim($emailInputInSigninForm.val());
        var password = $.trim($passwordInputInSigninForm.val());

        $.ajax({
            url: urlFor('account.do_signin'),
            method: 'post',
            dataType: 'json',
            data: {
                email: email,
                password: password,
                word: word,
                content: content,
                sentence: sentence
            }
        }).done(function (response) {
            if (response.result) {
                if (response.piece_id) {
                    window.location = urlFor('site.index', {piece_id: response.piece_id});
                } else {
                    window.location = urlFor('site.index');
                }
            } else {
                if (response.email !== "") {
                    showTip($emailInputInSigninForm, response.email);
                } else {
                    hideTip($emailInputInSigninForm);

                    if (response.password !== "") {
                        showTip($passwordInputInSigninForm, response.password);
                    } else {
                        hideTip($passwordInputInSigninForm);
                    }
                }
            }
        });
    }

    /**
     * 忘记密码
     */

    var $btnGoToForgotPassword = $signinForm.find('.btn-go-to-forgot-password');
    var $formForgotPassword = $('.form-forgot-password');
    var $emailInForgotPassword = $formForgotPassword.find('input');
    var $btnSendResetPasswordEmail = $formForgotPassword.find('.btn-send-reset-password-email');
    var $sendResetPasswordCallbackWap = $('.send-reset-password-email-callback-wap');

    $('.btn-back-to-signin').click(function () {
        $formForgotPassword.hide();
        switchToSignin();
    });

    // 跳转忘记密码
    $btnGoToForgotPassword.click(function () {
        $signinSignupWap.hide();
        $formForgotPassword.show();
    });

    // 发送重置链接
    $btnSendResetPasswordEmail.click(function () {
        var email = $.trim($emailInForgotPassword.val());

        $.ajax({
            url: urlFor('account.forgot_password'),
            method: 'post',
            data: {
                email: email
            }
        }).done(function (response) {
            var title, message;

            if (!response.result && response.email) {
                showTip($emailInForgotPassword, response.email);
            } else {
                hideTip($emailInForgotPassword);
                if (response.result) {
                    title = '邮件已发送';
                    message = '请登录邮箱完成密码重置';
                } else {
                    if (response.unactive) {
                        title = '账户尚未激活';
                        message = '请先登录邮箱激活账户';
                    } else {
                        title = '邮件发送失败';
                        message = '请稍后再试';
                    }
                }

                $formForgotPassword.hide();
                $sendResetPasswordCallbackWap.find('.title').text('邮件已发送');
                $sendResetPasswordCallbackWap.find('.message').text('请登录邮箱完成密码重置');
                $sendResetPasswordCallbackWap.show();
            }
        });
    });

    $emailInForgotPassword.keyup(function () {
        hideTip($(this));

        if ($.trim($(this).val()) !== '') {
            $btnSendResetPasswordEmail.prop('disabled', false);
        } else {
            $btnSendResetPasswordEmail.attr('disabled', true);
        }
    });

    /**
     * 重置密码
     */

    var $formResetPassword = $('.form-reset-password');
    var $btnResetPassword = $formResetPassword.find('.btn-reset-password');
    var $passwordInReset = $formResetPassword.find('input');

    var $resetPasswordCallbackWap = $('.reset-password-callback-wap');
    var $btnGoToSigninFromResetPassword = $resetPasswordCallbackWap.find('.btn-go-to-signin-from-reset-password');

    if (url('?reset') && url('?token')) {
        setTimeout(function () {
            $signinSignupWap.hide();
            $formResetPassword.show();
            $accountModal.modal();
        }, 0);
    }

    $btnResetPassword.click(function () {
        var password = $.trim($passwordInReset.val());

        $.ajax({
            url: urlFor('account.reset_password'),
            method: 'post',
            data: {
                password: password,
                token: url('?token')
            }
        }).done(function (response) {
            if (!response.result && response.password) {
                showTip($passwordInReset, response.password);
            } else {
                hideTip($passwordInReset);

                if (!response.result) {
                    $resetPasswordCallbackWap.find('.title').text('密码重置失败');
                    $resetPasswordCallbackWap.find('.message').text('请稍后尝试');
                }

                $formResetPassword.hide();
                $resetPasswordCallbackWap.show();
            }
        });
    });

    $passwordInReset.keyup(function () {
        hideTip($(this));

        if ($.trim($(this).val()) !== '') {
            $btnResetPassword.prop('disabled', false);
        } else {
            $btnResetPassword.attr('disabled', true);
        }
    });

    $btnGoToSigninFromResetPassword.click(function () {
        $resetPasswordCallbackWap.hide();
        switchToSignin();
    });

    // modal隐藏时重置界面
    $accountModal.on('hidden.bs.modal', function () {
        $(this).find('input').val();
        hideTip($(this).find('input'));
        $formForgotPassword.hide();
        $sendResetPasswordCallbackWap.hide();
        $formResetPassword.hide();
        $resetPasswordCallbackWap.hide();
        switchToSignup();
    });


    function switchToSignup() {
        $signinSignupWap.show();
        $('.nav-tabs li:nth-child(1) a').first().click();
    }

    function switchToSignin() {
        $signinSignupWap.show();
        $('.nav-tabs li:nth-child(2) a').first().click();
    }

    /**
     * 发布条目
     */

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
        $(window).scrollTo($secondScreen, 200);
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
            $firstStep.hide();
            $secondStep.show();
            $wordInSecondStep.text(word);
            $explanationTextarea.focus();
            $secondStep.css('paddingTop', (windowHeight - $secondStep.outerHeight()) * 0.4);
        }
    });

    // 提交
    $btnSubmitPiece.click(function () {
        content = $.trim($explanationTextarea.val());
        sentence = $.trim($sentenceTextarea.val());

        if (word !== '' && content !== '') {
            $accountModal.modal();
        }
    });

    // 添加例句
    $btnAddSentence.click(function () {
        $addPieceWapSecondStep.addClass('add-sentence');
        $sentenceTextarea.focus();
    });
})();
