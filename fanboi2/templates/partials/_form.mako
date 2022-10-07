<%def name="render_form(href)">
    <form class="form" action="${href}" method="post">
        <input type="hidden" name="csrf_token" value="${get_csrf_token()}">
        ${caller.body()}
    </form>
</%def>
<%def name="render_field(form, field, label=None, field_extra_classes=None, **kwargs)">
    <% field = getattr(form, field) %>
    <div class="form__item${' form__item--error' if field.errors else ''} u-mg-bottom-m">
        <label class="form__label u-mg-bottom-xs u-txt-s u-txt-gray4" for="${field.id}">${label if label else field.label.text}</label>
        ${field(class_="form__input form__input--shadowed" + (' ' + field_extra_classes if field_extra_classes else ''), **kwargs)}
        % if field.errors:
            <span class="form__error">${field.errors[0]}</span>
        % endif
    </div>
</%def>
<%def name="render_button(form, label, color=None, button_extra_classes=None, inline_fields=[])">
    <div class="form__item flex flex--row flex--gap-xs flex--items-center">
        <button class="flex__item--order-1 btn btn--shadowed btn--${color}${' ' + button_extra_classes if button_extra_classes else ''}" type="submit">${label}</button>
        % if hasattr(caller, "inline_fields"):
            ${caller.inline_fields()}
        % endif
    </div>
</%def>
<%def name="render_inline_field(form, field, label=None, **kwargs)">
    <% field = getattr(form, field) %>
    <span class="flex__item--order-2 u-txt-gray4">
        ${field(**kwargs)} <label for="${field.id}">${label if label else field.label.text}</label>
    </span>
</%def>
