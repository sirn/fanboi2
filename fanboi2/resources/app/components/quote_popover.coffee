# Quote Popover
# Inline popover for linked quote. If such element exists in the same
# page, it is simply cloned and displayed. Otherwise it is loaded from
# AJAX.
#
# TODO:
# - Caching queried results.
# - Add spinner.

rangeQueryRe = /(\d+)\-(\d+)/
dismissTimer = undefined
xhr = undefined


removeQuotePopover = ($elem) ->
    $parent = $elem.parent()
    $elem = $parent if $parent.length
    $elem.find('div.popover').remove()


renderQuotePopover = ($elem, $nodeList) ->
    removeQuotePopover $elem

    # Reset timer so that when user switch between multiple anchor in the
    # same post, dismissTimer won't clear the new popover. We already done
    # cleanup with `removeQuotePopover` already.
    if dismissTimer
        clearTimeout dismissTimer
        dismissTimer = undefined

    $container = $('<div class="popover"></div>')
    $container.append $nodeList
    $container.on 'mouseleave', () -> removeQuotePopover $elem
    $container.on 'mouseover', () ->
        if dismissTimer
            clearTimeout dismissTimer
            dismissTimer = undefined

    $elem.after $container


$(document).on 'mouseover', '[data-number]', (e) ->
    $anchor = $(e.target)
    $parent = $anchor.parents('div.posts')

    # Always build a post range regardless of the quote is ranged posted or
    # not to simplify retrieving process. These number will be used in range
    # loop for cloning DOM.
    attrs = $anchor.data('number')
    range = rangeQueryRe.exec(attrs)
    unless range
        beginNumber = parseInt(attrs)
        endNumber = beginNumber
    else
        beginNumber = parseInt(range[1])
        endNumber = parseInt(range[2])

    # Build node list by cloning DOM if post do exists on the web page. In
    # real world situation, it is very likely to have lasts of range posts
    # exists in the page (e.g. in recent view) but since we will need to
    # wait for XHR anyway, it is much simpler to retrieve the whole range
    # ("the rest") from AJAX. Thus the immediate break.
    nodeList = []
    for n in [beginNumber..endNumber]
        node = $parent[0].getElementsByClassName("post-#{n}")[0]
        if node
            $cloned = $ node.cloneNode(true)
            removeQuotePopover $cloned
            nodeList.push $cloned[0]
        else
            xhrNumber = n
            break

    # Since XHR callback is asynchronous, `renderQuotePopover` need to be
    # called in a callback otherwise nodeList would be incomplete. In
    # situation we don't need XHR (all nodes exists in page DOM) we could
    # just render it right away.
    unless xhrNumber
        renderQuotePopover $anchor, $(nodeList)
    else
        xhr = $.get $anchor.prop('href')
        xhr.then (data) ->
            $dom = $ $.parseHTML(data)
            for n in [xhrNumber..endNumber]
                node = $dom.find(".post-#{n}")[0]
                nodeList.push node if node
            renderQuotePopover $anchor, $(nodeList) if nodeList.length


$(document).on 'mouseleave', '[data-number]', (e) ->
    xhr.abort() if xhr
    _removeFn = () ->
        removeQuotePopover $(e.target)
        dismissTimer = undefined
    dismissTimer = setTimeout _removeFn, 100
