/* Quote Popover
 *
 * Inline popover for linked quote. If such element exists in the same
 * display, it is simply cloned and displayed. Otherwise it is loaded from
 * AJAX.
 *
 * TODO:
 * - Caching queried results.
 * - Add spinner.
 * - Prevent dismiss if user mouse enter the popover area.
 * */

var xhr;
var rangeQueryRe = /(\d+)\-(\d+)/;

window.addEventListener && document.addEventListener('mouseover', function(e){
    if (e.target.nodeName === 'A' && e.target.className === 'anchor') {
        var attr = e.target.getAttribute('data-number');
        var parent = e.target.parentNode;
        while (parent.nodeName !== 'DIV' || parent.className !== 'posts') {
            parent = parent.parentNode;
        }

        /* Always build post range regardless of the quote is ranged post
         * or not to simplify retrieving process. These number will be used
         * in a range loop for cloning DOM. */
        var range = rangeQueryRe.exec(attr);
        var beginNumber, endNumber, xhrNumber;
        if (!range) {
            beginNumber = parseInt(attr);
            endNumber = beginNumber;
        } else {
            beginNumber = parseInt(range[1]);
            endNumber = parseInt(range[2]);
        }

        /* Build node list by cloning DOM if post do exists on the web page.
         * In real world situation, it is very likely to have lasts of range
         * posts exists in the page (e.g. in recent view) but since we will
         * need to wait for XHR anyway, it is much simpler to retrieve the
         * whole range ("the rest") from AJAX. Thus the immediate break. */
        var nodeList = [];
        for (var n = beginNumber; n <= endNumber; n++) {
            var node = parent.getElementsByClassName('post-' + n)[0];
            if (node) {
                nodeList.push(node.cloneNode(true));
            } else {
                xhrNumber = n;
                break;
            }
        }

        /* Since XHR callback is asynchronous, _renderPopover need to be
         * called in a callback otherwise nodeList would be incomplete.
         * In situation we don't need XHR (all nodes exists in page DOM)
         * we could just render it right away. */
        if (!xhrNumber) {
            _renderPopover(e.target, nodeList);
        } else {
            xhr = new XMLHttpRequest();
            xhr.open('GET', e.target.getAttribute('href'));

            /* IE9 don't support xhr.responseType = "document" :( */
            xhr.onload = function _get_external_post() {
                var dom = new DOMParser();
                var doc = dom.parseFromString(xhr.responseText, 'text/html');
                for (var n = xhrNumber; n <= endNumber; n++) {
                    var node = doc.getElementsByClassName('post-' + n)[0];
                    if (node) {
                        nodeList.push(node);
                    }
                }
                _renderPopover(e.target, nodeList);
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
function _renderPopover(target, nodeList) {
    _removePopover(target);
    var container = document.createElement('DIV');
    container.className = 'popover';
    for (var i = 0, len = nodeList.length; i < len; i++) {
        container.appendChild(nodeList[i]);
    }
    target.parentNode.insertBefore(container, target.nextSibling);
}

/* Dismiss popover if user no longer hover the anchor link. */
window.addEventListener && document.addEventListener('mouseout', function(e){
    if (e.target.nodeName === 'A' && e.target.className === 'anchor') {
        if (xhr) { xhr.abort(); }
        _removePopover(e.target);
    }
});
