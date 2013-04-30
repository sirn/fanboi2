/* Quote Popover
 *
 * Inline popover for linked quote. If such element exists in the same
 * display, it is simply cloned and displayed. Otherwise it is loaded from
 * AJAX.
 *
 * TODO:
 * - Support range query (i.e. >>1-3).
 * - Caching queried results.
 * - Add spinner.
 * - Prevent dismiss if user mouse enter the popover area.
 * */

var xhr;

window.addEventListener && document.addEventListener('mouseover', function(e){
    if (e.target.nodeName === 'A' && e.target.className === 'anchor') {
        var number = parseInt(e.target.getAttribute('data-number'));
        var parent = e.target.parentNode;
        while (parent.nodeName !== 'DIV' || parent.className !== 'posts') {
            parent = parent.parentNode;
        }

        /* If post do exists on the page, we simply clone and redisplay it
         * otherwise the post is retrieved via AJAX. Since we need to support
         * older browser, we're using DOMParser instead of simply set
         * xhr.responseType = document. */
        var node = parent.getElementsByClassName('post-' + number)[0];
        if (node) {
            _renderPopover(e.target, node.cloneNode(true));
        } else {
            xhr = new XMLHttpRequest();
            xhr.open('GET', e.target.getAttribute('href'));
            xhr.onload = function _get_external_post() {
                var dom = new DOMParser();
                var doc = dom.parseFromString(xhr.responseText, 'text/html');
                node = doc.getElementsByClassName('post-' + number)[0];
                if (node) {
                    _renderPopover(e.target, node);
                }
            };
            xhr.send(null);
        }
    }
});

/* Remove popover associated with target. */
function _removePopover(target) {
    var nodes = target.parentNode.getElementsByClassName('popover');
    for (var i = nodes.length - 1; i >= 0; i--) {
        target.parentNode.removeChild(nodes[i]);
    }
}

/* Render popover and setup its floating styles. */
function _renderPopover(target, node) {
    _removePopover(target);
    node.className = node.className + ' popover';
    target.parentNode.insertBefore(node, target.nextSibling);
}

/* Dismiss popover if user no longer hover the anchor link. */
window.addEventListener && document.addEventListener('mouseout', function(e){
    if (e.target.nodeName === 'A' && e.target.className === 'anchor') {
        if (xhr) { xhr.abort(); }
        _removePopover(e.target);
    }
});
