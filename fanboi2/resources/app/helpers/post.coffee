# Post helpers
# Miscellaneous helpers for post item and post form.

formHelper = require 'helpers/form'


# Local helpers
getTopicKey = (topicId, component) -> "topic:#{topicId}:#{component}"
getForm = ($form) -> if $form.is('form') then $form else $form.find('form')

# Extract post ID from post element (usually an article.post).
extractPostId = ($elem) ->
    parseInt $elem.prop('id').match(/post-(\d+)/)[1]


# Update bump state for this post to last used state.
exports.updateBumpState = ($form) ->
    $form = getForm $form
    $bumpInput = $form.find('input#bumped')

    storageKey = getTopicKey $form.data('topic'), 'bumpState'
    bumpStatus = JSON.parse localStorage.getItem(storageKey)
    $bumpInput.prop 'checked', if bumpStatus? then bumpStatus else true

    $form.on 'submit.updateBumpStatus', () ->
        localStorage.setItem storageKey, $bumpInput.prop('checked')


# Clone new posts from $dom and append to specific topic ID.
exports.appendNewPosts = ($dom, topicId) ->
    $wrapper = $ "article#topic-" + topicId
    $postContainer = $wrapper.find 'div.posts'
    lastPost = extractPostId $wrapper.find 'article.post:last'

    $domWrapper = $dom.find "article#topic-" + topicId
    $postContainer.append $domWrapper.find('article.post').filter ->
        lastPost < extractPostId $(this)


exports.enableAjaxPosting = ($form) ->
    $form = getForm $form
    topicId = $form.data 'topic'

    $form.on 'submit', (e) ->
        e.preventDefault()

        formHelper.clearFormErrors $form
        formHelper.waitForForm $form

        xhr = $.post $form.prop('action'), $form.serialize()
        xhr.done (data, status, jqXHR) ->
            $dom = $ $.parseHTML(data)
            formHelper.unwaitForForm $form

            # Form has at least one error. We simply clone those errors.
            if $dom.find('form#reply div.errors').length
                formHelper.cloneFormErrors $form, $dom.find 'form#reply'

            # Form is success. We clone the new post into DOM.
            else
                $form.find('textarea#body').val ''
                $form.trigger 'success'
                exports.appendNewPosts $dom, topicId
