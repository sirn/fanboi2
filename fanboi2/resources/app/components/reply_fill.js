/* Reply Fill
 *
 * Fill reply box with anchor from content in span.number.
 *
 * TODO:
 * - Cross page reply filling (e.g. index -> show page).
 */


var eventEnabled = 'addEventListener' in document;
var replyBoxVisible = !!document.getElementById('reply');
var xhr;


/* Remove all reply popover. */
function _removePopover() {
    var replyNode = document.getElementById('reply');
    if (!!replyNode) {
        replyNode.parentNode.removeChild(replyNode);
    }
}

function _renderPopover(target, node, text) {
    _removePopover();
    node.className = "popover " + node.className;
    target.parentNode.insertBefore(node, target.nextSibling);

    var replyBox = node.getElementsByTagName('textarea')[0];
    replyBox.value = text;
    replyBox.selectionStart = text.length;

    /* Allow user to click anywhere in the page to dismiss. */
    document.addEventListener('click', function(e) {
        var _n = e.target;
        while (_n && _n !== node) { _n = _n.parentNode; }
        if (_n !== node) {
            _removePopover();
            document.removeEventListener('click', arguments.callee);
        }
    });
}

eventEnabled && document.addEventListener('click',
function(e) {
    if (e.target.nodeName === 'A' && e.target.className === 'number') {
        e.preventDefault();

        var number = e.target.textContent;
        var text = ">>" + number + " ";

        /* If reply box is visible in page (e.g. a reply page) we don't have
         * to render inline reply box. Instead, we just autofill the reply
         * box at cursor. */
        if (replyBoxVisible) {
            var replyBox = document.getElementById('body');
            if (replyBox.selectionStart || replyBox.selectionStart === 0) {
                var startPos = replyBox.selectionStart;
                var endPos = replyBox.selectionEnd;
                replyBox.value = replyBox.value.substring(0, startPos) +
                    text +
                    replyBox.value.substring(endPos, replyBox.value.length);
                replyBox.focus();
                replyBox.selectionStart = startPos + text.length;
            }

        /* Otherwise we render the reply popover inline. */
        } else {
            xhr = new XMLHttpRequest();
            xhr.open('GET', e.target.getAttribute('href'));

            /* IE9 don't support xhr.responseType = "document" :( */
            xhr.onload = function _getReplyForm() {
                var dom = new DOMParser();
                var doc = dom.parseFromString(xhr.responseText, 'text/html');
                _renderPopover(e.target, doc.getElementById('reply'), text);
            };

            xhr.send(null);
        }
    }
});
