import { h, VNode } from "virtual-dom";
import { mergeClasses, mergeDatasets } from "../utils/template";

export class ModalView {
    childNode: VNode;
    title: string | undefined;
    dismissFn: (() => void) | undefined;

    constructor(childNode: VNode, title?: string, dismissFn?: () => void) {
        this.childNode = childNode;
        this.title = title;
        this.dismissFn = dismissFn;
    }

    render(targetElement: Element, args: any = {}): VNode {
        let wrapperArgs = args.wrapper || {};
        let modalArgs = args.modal || {};

        let xMargin = args.xMargin || 5;
        let clampWidth = args.clampWidth || 640;
        let pos = ModalView.computePosition(targetElement, xMargin, clampWidth);

        if (!modalArgs.style) {
            modalArgs.style = {};
        }

        modalArgs.style.position = "absolute";
        modalArgs.style.top = `${pos.posX}px`;
        modalArgs.style.left = `${pos.posY}px`;

        return h("div", mergeDatasets(wrapperArgs, { modal: true }), [
            h("div", mergeClasses(modalArgs, ["modal"]), [
                h(
                    "div",
                    {
                        className: [
                            "panel",
                            "panel--horizontal",
                            "panel--gray2",
                            "flex",
                            "flex--row",
                            "flex--items-center",
                        ].join(" "),
                    },
                    [
                        ...(this.title
                            ? [
                                  h(
                                      "h3",
                                      {
                                          className: [
                                              "flex__item",
                                              "flex__item--grow-2",
                                              "flex__item--order-1",
                                              "u-txt-gray4",
                                              "u-mg-reset",
                                              "u-pd-horizontal-s",
                                          ].join(" "),
                                      },
                                      [this.title]
                                  ),
                                  ...(this.dismissFn
                                      ? [
                                            h(
                                                "a",
                                                {
                                                    className: [
                                                        "flex__item",
                                                        "flex__item--order-2",
                                                        "icon",
                                                        "icon--tappable",
                                                        "icon--cross-blue",
                                                        "u-pull-right",
                                                    ].join(" "),
                                                    href: "#",
                                                    onclick: (e: Event): void => {
                                                        e.preventDefault();
                                                        if (this.dismissFn) {
                                                            this.dismissFn();
                                                        }
                                                    },
                                                },
                                                ["Close"]
                                            ),
                                        ]
                                      : []),
                              ]
                            : []),
                    ]
                ),
                h("div", { className: "modal__item" }, [this.childNode]),
            ]),
        ]);
    }

    private static computePosition(
        targetElement: Element,
        xMargin: number,
        clampWidth: number
    ): {
        posX: number;
        posY: number;
    } {
        let bodyRect = document.body.getBoundingClientRect();
        let elemRect = targetElement.getBoundingClientRect();
        let yRefRect = elemRect;

        return {
            posX: elemRect.bottom + xMargin - bodyRect.top,
            posY: Math.min(
                yRefRect.left - bodyRect.left,
                Math.max(0, bodyRect.right - clampWidth)
            ),
        };
    }
}
