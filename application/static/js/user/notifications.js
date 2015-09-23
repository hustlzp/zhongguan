$('#main-wap .noti').click(function () {
    var pieceId = $(this).data('piece-id');

    window.location = urlFor('site.index', {piece_id: pieceId});
});
