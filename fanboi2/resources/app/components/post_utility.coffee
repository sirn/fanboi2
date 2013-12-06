# Post Utilities
# Initialize post utilities.

postHelper = require 'helpers/post'


$form = $('form#reply')
if $form.length
    postHelper.updateBumpState $form
    postHelper.enableAjaxPosting $form


refreshXHR = null

$(document).on 'click', 'article.topic a.reload', (e) ->
    e.preventDefault()

    $elem = $(e.target)
    $wrapper = $elem.parents('article.topic')

    # Don't request again if there is already active refresh XHR.
    unless refreshXHR?
        $elem.data 'orig-text', $elem.html()
        $elem.text $elem.data 'loading'
        $elem.addClass 'active'

        # Fetch new posts and append it to current wrapper.
        refreshXHR = $.get $elem.prop('href')
        refreshXHR.done (data, status, jqXHR) ->
            $dom = $ $.parseHTML(data)
            postHelper.appendNewPosts $dom, $wrapper

            $elem.removeClass 'active'
            $elem.html $elem.data 'orig-text'

            # Update current HREF to the latest.
            $elem.prop 'href', $dom.find('article.topic a.reload').prop 'href'

            # Allow another reload.
            refreshXHR = null
