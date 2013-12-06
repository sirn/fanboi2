# Form helpers
# Miscellaneous helpers for generic form.


# Remove form errors from specific $form element.
exports.clearFormErrors = ($form) ->
    $form.find('div.errors').removeClass('errors')
    $form.find('span.error').remove()


# Clone form errors from $sourceForm into $form. Intended to be used with
# errors from AJAX pages.
exports.cloneFormErrors = ($form, $sourceForm) ->
    $formErrors = $sourceForm.find('div.errors')
    for error in $formErrors
        $error = $(error)
        $errorMessage = $error.find('span.error').clone()

        if $errorMessage.length
            fieldName = $error.find('label').prop('for')
            $fieldWrapper = $form.find("div.field-#{fieldName}")
            $fieldWrapper.addClass('errors')
            $fieldWrapper.find('div').append($errorMessage)


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
