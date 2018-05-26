export const addClass = (element: Element, newClasses: string[]): void => {
    let classNames = element.className.split(" ");

    for (let i = 0, len = newClasses.length; i < len; i++) {
        let newClass = newClasses[i];

        if (classNames.indexOf(newClass) == -1) {
            classNames.push(newClass);
        }
    }

    element.className = classNames.join(" ");
};

export const removeClass = (element: Element, removeClasses: string[]): void => {
    let classNames = element.className.split(" ");

    for (let i = 0, len = removeClasses.length; i < len; i++) {
        let removeClass = removeClasses[i];
        let removeClassIdx = classNames.indexOf(removeClass);

        if (removeClassIdx != -1) {
            classNames.splice(removeClassIdx, 1);
        }
    }

    element.className = classNames.join(" ");
};

export const dispatchCustomEvent = (
    element: Element,
    eventName: string,
    opts: any = {},
): void => {
    element.dispatchEvent(
        new CustomEvent(eventName, {
            bubbles: true,
            detail: opts,
        }),
    );
};
