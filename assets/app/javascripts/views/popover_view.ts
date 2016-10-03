import {VNode, h} from 'virtual-dom';


export class PopoverView {
    childNode: VNode;
    targetElement: Element;

    constructor(targetElement: Element, childNode: VNode) {
        this.targetElement = targetElement;
        this.childNode = childNode;
    }

    render(): VNode {
        let pos = this.computePosition();
        return h('div', {className: 'js-popover'}, [
            h('div', {
                className: 'js-popover-inner',
                style: {
                    position: 'absolute',
                    top: `${pos.posX}px`,
                    left: `${pos.posY}px`,
                }
            }, [this.childNode])
        ]);
    }

    private computePosition(): {posX: number, posY: number} {
        let bodyRect = document.body.getBoundingClientRect();
        let elemRect = this.targetElement.getBoundingClientRect();
        let yRefRect = elemRect;

        // Indent relative to container rather than element if there is
        // container in element ancestor.
        let containerElement = this.targetElement.closest('.container');
        if (containerElement) {
            yRefRect = containerElement.getBoundingClientRect();
        }

        return {
            posX: (elemRect.bottom + 5) - bodyRect.top,
            posY: yRefRect.left - bodyRect.left,
        }
    }
}
