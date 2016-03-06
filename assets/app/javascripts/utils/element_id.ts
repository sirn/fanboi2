import {generateUuid} from './uuid';


export function getElementId(element: Element): string {
    let elementId = element.getAttribute('data-element-id');

    if (!elementId) {
        elementId = `js-${generateUuid()}`;
        element.setAttribute(
            'data-element-id',
            elementId
        )
    }

    return elementId;
}
