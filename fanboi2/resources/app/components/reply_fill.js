/* Reply Fill
 *
 * Fill reply box with anchor from content in span.number.
 *
 * TODO:
 * - Cross page reply filling (e.g. index -> show page).
 */


var eventEnabled = 'addEventListener' in document;
var replyBoxVisible = document.getElementsByClassName('field-body');

eventEnabled && !!replyBoxVisible.length && document.addEventListener('click',
function(e) {
    if (e.target.nodeName === 'SPAN' && e.target.className === 'number') {
        e.preventDefault();

        var replyBox = document.getElementById('body');
        var number = e.target.textContent;

        if (replyBox.selectionStart || replyBox.selectionStart === 0) {
            var startPos = replyBox.selectionStart;
            var endPos = replyBox.selectionEnd;
            var text = ">>" + number + " ";
            replyBox.value = replyBox.value.substring(0, startPos) +
                text +
                replyBox.value.substring(endPos, replyBox.value.length);
            replyBox.focus();
            replyBox.selectionStart = startPos + text.length;
        }
    }
});
