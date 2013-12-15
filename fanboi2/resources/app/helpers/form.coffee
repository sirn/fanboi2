# Form helpers
# Miscellaneous helpers for generic form.


# Handles periodic fetching of task status and return if task is success.
exports.fetchStatus = (xhr, callback) ->
    xhr.done (data, status, jqXHR) ->
        $dom = $ $.parseHTML(data)
        $task = $dom.find('[data-task]')
        if $task.length
            statusUrl = $task.data 'task'
            retryFunc = -> exports.fetchStatus $.get(statusUrl), callback
            setTimeout retryFunc, 300
        else
            callback data, status, jqXHR


# Remove form errors from specific $form element.
exports.clearFormErrors = ($form) ->
    $form.find('div.errors').removeClass('errors')
    $form.find('span.error').remove()


# Add form error to specific form field.
exports.addFormErrors = ($form, fieldName, message) ->
    $errorMessage = $('<span class="error"></span>')
    $fieldWrapper = $form.find "div.field-#{fieldName}"
    $fieldWrapper.addClass 'errors'
    $fieldWrapper.find('div').append $errorMessage.text message


# Clone form errors from $sourceForm into $form. Intended to be used with
# errors from AJAX pages.
exports.cloneFormErrors = ($form, $sourceForm) ->
    $formErrors = $sourceForm.find('div.errors')
    for error in $formErrors
        $error = $(error)
        message = $error.find('span.error').text()

        if message
            fieldName = $error.find('label').prop('for')
            exports.addFormErrors $form, fieldName, message


# Transition effect when form is submitting.
exports.waitForForm = ($form) ->
    $submitButton = $form.find('button:submit')
    $submitButton.data 'orig-text', $submitButton.text()
    $submitButton.prop 'disabled', true
    $submitButton.text $submitButton.data 'loading'


# Remove the transition effect when form is submitting.
exports.unwaitForForm = ($form) ->
    $submitButton = $form.find('button:submit')
    $submitButton.text $submitButton.data 'orig-text'
    $submitButton.prop 'disabled', false
