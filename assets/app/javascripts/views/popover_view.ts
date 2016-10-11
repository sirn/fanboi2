import {VNode, h} from 'virtual-dom';


export class PopoverView {
    constructor(
        public targetElement: Element,
        public childNode: VNode,
        public title?: string,
        public dismissFn?: (() => void),
    ) {
    }

    render(args?: any): VNode {
        let self = this;
        let pos = this.computePosition();
        let titleNode: VNode;

        if (this.title != null) {
            let dismissNode: VNode;

            if (this.dismissFn != null) {
                dismissNode = h('a', {
                    onclick: function(): void { self.dismissFn(); },
                    className: 'js-popover-inner-title-dismiss',
                    href: '#',
                }, [String('Close')]);
            }

            titleNode = h('div', {
                className: 'js-popover-inner-title',
            }, [
                h('span', {
                    className: 'js-popover-inner-title-label'
                }, [this.title]),
                dismissNode,
            ]);
        }

        return h('div', PopoverView.getViewClassName(args), [
            h('div', {
                className: 'js-popover-inner',
                style: {
                    position: 'absolute',
                    top: `${pos.posX}px`,
                    left: `${pos.posY}px`,
                }
            }, [titleNode, this.childNode])
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

    private static getViewClassName(args?: any): any {
        let className = 'js-popover';

        if (!args) {
            args = {};
        }

        if (args.className) {
            let classNames = args.className.split(' ');
            classNames.push(className);
            args.className = classNames.join(' ');
        } else {
            args.className = className;
        }

        return args;
    }
}
