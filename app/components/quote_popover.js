/* Quote Popover
 *
 * Inline popover for linked quote. If such element exists in the same
 * display, it is simply cloned and displayed. Otherwise it is loaded from
 * AJAX.
 *
 * TODO:
 * - Caching queried results.
 * - Add spinner.
 * */

var xhr;
var eventEnabled = 'addEventListener' in document;
var rangeQueryRe = /(\d+)\-(\d+)/;
var dismissTimer;


/* Remove popover associated with target. */
function _removePopover(target) {
    var node = target.parentNode || target;
    var nodes = node.getElementsByClassName('popover');
    for (var i = nodes.length - 1; i >= 0; i--) {
        nodes[i].parentNode.removeChild(nodes[i]);
    }
}

/* Render popover and setup its floating styles. */
function _renderPopover(target, nodeList) {
    _removePopover(target);
    var container = document.createElement('DIV');
    for (var i = 0, len = nodeList.length; i < len; i++) {
        container.appendChild(nodeList[i]);
    }

    /* If dismissTimer is still active and user move the mouse into popover
     * a dismiss is cancelled to make popover persist and one-off event is
     * added so that when mouse leave the popover, the popover is gone.
     *
     * mouseleave is not available in WebKit browsers. Sigh. */
    container.className = 'popover';
    container.addEventListener('mouseover', function() {
        if (dismissTimer) {
            clearTimeout(dismissTimer);
            dismissTimer = undefined;

            container.removeEventListener('mouseover', arguments.callee);
            document.addEventListener('mouseover', function(e) {
                var _n = e.target;
                while (_n && _n !== container) { _n = _n.parentNode; }
                if (_n !== container) {
                    _removePopover(target);
                    document.removeEventListener(
                        'mouseover',
                        arguments.callee
                    );
                }
            });
        }
    });

    target.parentNode.insertBefore(container, target.nextSibling);
}


/* Event delegation
 *
 * mouseover a.anchor    display popover
 * mouseout  a.anchor    dismiss popover
 */

eventEnabled && document.addEventListener('mouseout', function(e) {
    if (e.target.nodeName === 'A' && e.target.className === 'anchor') {
        if (xhr) { xhr.abort(); }
        dismissTimer = setTimeout(function(){
            _removePopover(e.target);
            dismissTimer = undefined;
        }, 100);
    }
});

eventEnabled && document.addEventListener('mouseover', function(e) {
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
                var cloned = node.cloneNode(true);
                _removePopover(cloned);
                nodeList.push(cloned);
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
            xhr.onload = function _getExternalPost() {
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

