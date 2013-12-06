# Post Form
# Initialize post form utilities.

postHelper = require 'helpers/post'


$form = $('form#reply')
if $form.length
    postHelper.updateBumpState $form
    postHelper.enableAjaxPosting $form