export function addClass(
    element: Element,
    newClasses: string | string[]
): void {
    if (typeof(newClasses) == 'string') {
        newClasses = newClasses.split(' ');
    }

    let classNames = element.className.split(' ');
    for (let i = 0, len = newClasses.length; i < len; i++) {
        let newClass = newClasses[i];
        if (classNames.indexOf(newClass) == -1) {
            classNames.push(newClass);
        }
    }

    element.className = classNames.join(' ');
}


export function removeClass(
    element: Element,
    removeClasses: string | string[]
): void {
    if (typeof(removeClasses) == 'string') {
        removeClasses = removeClasses.split(' ');
    }

    let classNames = element.className.split(' ');
    for (let i = 0, len = removeClasses.length; i < len; i++) {
        let removeClass = removeClasses[i];
        let removeClassIdx = classNames.indexOf(removeClass);
        if (removeClassIdx != -1) {
            classNames.splice(removeClassIdx, 1);
        }
    }

    element.className = classNames.join(' ');
}


export function dispatchCustomEvent(
    element: Element,
    eventName: string,
    opts?: any,
): void {
    if (opts == null) { opts = {}; }
    element.dispatchEvent(new CustomEvent(eventName, {
        bubbles: true,
        detail: opts
    }))
}


export function serializeForm(form: HTMLFormElement): any {
    let formData: {[key: string]: any} = {};

    function insertField(name: string, value: any) {
        if (name) {
            formData[name] = value;
        }
    }

    for (let i = 0, len = form.elements.length; i < len; i++) {
        switch (form.elements[i].nodeName) {
        case 'INPUT':
            let inputField = <HTMLInputElement>form.elements[i];
            switch (inputField.type) {
            case 'file':
            case 'button':
                break;
            case 'checkbox':
            case 'radio':
                if (inputField.checked) {
                    insertField(inputField.name, inputField.value);
                }
                break;
            default:
                insertField(inputField.name, inputField.value);
                break;
            }
            break;
        case 'SELECT':
            let selectField = <HTMLSelectElement>form.elements[i];
            switch (selectField.type) {
            case 'select-multiple':
                let fieldData: string[] = [];
                for (let n = 0, l = selectField.options.length; n < l; n++) {
                    if (selectField.options[n].selected) {
                        fieldData.push(selectField.options[0].value);
                    }
                }
                insertField(selectField.name, fieldData);
                break;
            default:
                fieldData.push(selectField.name, selectField.value);
                break;
            }
            break;
        case 'TEXTAREA':
            let textAreaField = <HTMLTextAreaElement>form.elements[i];
            insertField(textAreaField.name, textAreaField.value);
            break;
        default:
            break;
        }
    }

    return formData;
}
