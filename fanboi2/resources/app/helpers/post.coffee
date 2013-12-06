# Post helpers
# Miscellaneous helpers for post item and post form.


# Local helpers
getTopicKey = (topicId, component) -> "topic:#{topicId}:#{component}"
getForm = ($form) -> if $form.is('form') then $form else $form.find('form')


# Update bump state for this post to last used state.
exports.updateBumpState = ($form) ->
    $form = getForm $form
    $bumpInput = $form.find('input#bumped')

    storageKey = getTopicKey $form.data('topic'), 'bumpState'
    bumpStatus = JSON.parse localStorage.getItem(storageKey)
    $bumpInput.prop 'checked', if bumpStatus? then bumpStatus else true

    $form.on 'submit.updateBumpStatus', () ->
        localStorage.setItem storageKey, $bumpInput.prop('checked')
