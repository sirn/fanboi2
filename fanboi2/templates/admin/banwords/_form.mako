<%namespace name="formtpl" file="../../partials/_form.mako" />
<%def name="render_form(form, href, button_label, button_color)">
    <%formtpl:render_form href="${href}">
        <%formtpl:render_field form="${form}" field="expr" field_extra_classes="form__input--bordered" />
        <%formtpl:render_field form="${form}" field="description" field_extra_classes="form__input--bordered" />
        <%formtpl:render_field form="${form}" field="scope" field_extra_classes="form__input--bordered" />
        <%formtpl:render_button form="${form}" label="${button_label}" color="${button_color}">
            <%def name="inline_fields()">
                <%formtpl:render_inline_field form="${form}" field="active" />
            </%def>
        </%formtpl:render_button>
    </%formtpl:render_form>
</%def>
