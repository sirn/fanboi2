import { VNode, h } from "virtual-dom";

export class PopoverView {
    popoverChildNodes: VNode[];

    constructor(childNode: VNode, title?: string, dismissFn?: (() => void)) {
        this.popoverChildNodes = PopoverView.renderChild(childNode, title, dismissFn);
    }

    render(targetElement: Element, args: any = {}): VNode {
        let pos = PopoverView.computePosition(targetElement);

        return h("div", PopoverView.getViewClassName(args), [
            h(
                "div",
                {
                    className: "js-popover-inner",
                    style: {
                        position: "absolute",
                        top: `${pos.posX}px`,
                        left: `${pos.posY}px`,
                    },
                },
                this.popoverChildNodes,
            ),
        ]);
    }

    private static renderChild(
        childNode: VNode,
        title?: string,
        dismissFn?: (() => void),
    ): VNode[] {
        let popoverChildNodes: VNode[] = [];

        if (title) {
            let titleChildNodes = [
                h(
                    "span",
                    {
                        className: "js-popover-inner-title-label",
                    },
                    [title],
                ),
            ];

            if (dismissFn) {
                titleChildNodes.push(
                    h(
                        "a",
                        {
                            className: "js-popover-inner-title-dismiss",
                            href: "#",
                            onclick: (e: Event): void => {
                                e.preventDefault();
                                if (dismissFn) {
                                    dismissFn();
                                }
                            },
                        },
                        ["Close"],
                    ),
                );
            }

            popoverChildNodes.push(
                h(
                    "div",
                    {
                        className: "js-popover-inner-title",
                    },
                    titleChildNodes,
                ),
            );
        }

        popoverChildNodes.push(childNode);
        return popoverChildNodes;
    }

    private static computePosition(
        targetElement: Element,
    ): {
        posX: number;
        posY: number;
    } {
        let bodyRect = document.body.getBoundingClientRect();
        let elemRect = targetElement.getBoundingClientRect();
        let yRefRect = elemRect;

        // Indent relative to container rather than element if there is
        // container in element ancestor.
        let containerElement = targetElement.closest(".container");
        if (containerElement) {
            yRefRect = containerElement.getBoundingClientRect();
        }

        return {
            posX: elemRect.bottom + 5 - bodyRect.top,
            posY: yRefRect.left - bodyRect.left,
        };
    }

    private static getViewClassName(args: any): any {
        const className = "js-popover";

        if (args.className) {
            let classNames = args.className.split(" ");
            classNames.push(className);
            args.className = classNames.join(" ");
        } else {
            args.className = className;
        }

        return args;
    }
}
