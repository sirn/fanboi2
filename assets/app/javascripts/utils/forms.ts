import {create, h} from 'virtual-dom';
import {ResourceError} from './errors';
import {addClass, removeClass} from './elements';


export let serializeForm = (form: HTMLFormElement): any => {
    let formData: {[key: string]: any} = {};

    let _insertField = (name: string, value: any) => {
        if (name) {
            formData[name] = value;
        }
    }

    for (let i = 0, len = form.elements.length; i < len; i++) {
        let field = form.elements[i];

        if (field instanceof HTMLInputElement) {
            switch (field.type) {
            case 'file':
            case 'button':
                break;
            case 'checkbox':
            case 'radio':
                if (field.checked) {
                    _insertField(field.name, field.value);
                }
                break;
            default:
                _insertField(field.name, field.value);
                break;
            }
        } else if (field instanceof HTMLSelectElement) {
            switch (field.type) {
            case 'select-multiple':
                let fieldData: string[] = [];
                for (let n = 0, l = field.options.length; n < l; n++) {
                    if (field.options[n].selected) {
                        fieldData.push(field.options[0].value);
                    }
                }
                _insertField(field.name, fieldData);
                break;
            default:
                _insertField(field.name, field.value);
                break;
            }
        } else if (field instanceof HTMLTextAreaElement) {
            _insertField(field.name, field.value);
        }
    }

    return formData;
}


export let attachErrors = (form: HTMLFormElement, error: ResourceError) => {
    let data = error.object;

    let _attachError = (fieldElement: Element, message: string): void => {
        let formItemElement = fieldElement.closest('.form-item');

        if (!!formItemElement) {
          let err = h('span', {className: 'form-item-error'}, [message]);

          addClass(formItemElement, ['error']);
          fieldElement.parentElement.insertBefore(
              create(err),
              fieldElement.nextSibling
          );
        }
    }

    if (data.status == 'params_invalid') {
        for (let field in <{[key: string]: string[]}>data.message) {
            if (data.message.hasOwnProperty(field)) {
                _attachError(
                    form[field],
                    data.message[field]
                );
            }
        }
    } else {
        _attachError(
            form.querySelector('[data-form-anchor]'),
            data.message
        );
    }
}


export let detachErrors = (form: HTMLFormElement) => {
    let errorElements = form.querySelectorAll('.error');
    let msgElements = form.querySelectorAll('.form-item-error');

    for (let i = 0, len = errorElements.length; i < len; i++) {
        removeClass(
            errorElements[0],
            ['error']
        );
    }

    for (let i = 0, len = msgElements.length; i < len; i++) {
        msgElements[0].parentElement.removeChild(msgElements[0]);
    }
}
