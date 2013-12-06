# Quick Reply
# Fill reply box with anchor from content in span.number.
#
# TODO:
# - Cache user input and append number instead of clearing.
# - Allow moving of reply popover.
# - Performance improvements.

postHelper = require 'helpers/post'


removeReplyPopover = () ->
    $(document).off 'click.removeReplyPopover'
    $(document).off 'keydown.removeReplyPopover'
    $('form.popover').remove()


renderReplyPopover = ($elem, $node, text) ->
    removeReplyPopover()

    # Add explicit close button to popover form.
    $closeButton = $('<span class="close">×</span>')
    $closeButton.on 'click', removeReplyPopover
    $closeButton.appendTo $node

    # Insert the element to DOM.
    $elem.after $node
    $node.addClass 'popover'
    postHelper.updateBumpState $node

    # Pre-fill reply box with text.
    $textarea = $node.find('textarea#body')
    $textarea.val text
    $textarea.focus()
    $textarea[0].selectionStart = text.length

    # Allow user to click anywhere in the page to dismiss.
    $(document).on 'click.removeReplyPopover', (e) ->
        unless $(e.target).parents('form.popover').length
            removeReplyPopover()

    # Allow user to press ESC to dismiss. Keydown will return 229 when IME
    # is active, so ESC won't get caught if user is intended to dismiss
    # the IME suggestion.
    $(document).on 'keydown.removeReplyPopover', (e) ->
        if e.which == 27
            removeReplyPopover()


$(document).on 'click', 'a.number', (e) ->
    e.preventDefault()

    $anchor = $(e.target)
    text = ">>#{parseInt $anchor.text()} "

    # If reply box is visible in page (e.g. a reply page) we don't have to
    # render inline reply box. Instead, we just autofill the reply box at
    # cursor.
    $form = $('form#reply')
    if $form.length
        $replyBox = $form.find('textarea#body')
        if $replyBox[0].selectionStart or $replyBox[0].selectionStart == 0
            startPos = $replyBox[0].selectionStart
            endPos = $replyBox[0].selectionEnd

            # Fill in form text at cursor.
            replyValue = $replyBox.val()
            $replyBox.val \
                replyValue.substring(0, startPos) +
                text +
                replyValue.substring(endPos, replyValue.length)

            $replyBox.focus()
            $replyBox[0].selectionStart = startPos + text.length

    # Otherwise we render the reply popover inline.
    else
        xhr = $.get $anchor.prop('href')
        xhr.then (data) ->
            $dom = $ $.parseHTML(data)
            renderReplyPopover $anchor, $dom.find('form#reply'), text
