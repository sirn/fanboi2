import { h, VNode } from "virtual-dom";
import { mergeClasses, mergeDatasets } from "../utils/template";

export class PostForm {
    defaultText: string = "";

    constructor(defaultText: string = "") {
        this.defaultText = defaultText;
    }

    render(args: any = {}): VNode {
        let wrapperArgs = args.wrapper || {};
        let panelArgs = args.panel || {};
        let containerArgs = args.container || { className: "u-pd-vertical-l" };
        let formArgs = args.form || {};

        return h("div", mergeDatasets(wrapperArgs, { postForm: true }), [
            h("div", mergeClasses(panelArgs, ["panel"]), [
                h("div", mergeClasses(containerArgs, ["container"]), [
                    h(
                        "form",
                        mergeClasses(
                            mergeDatasets(formArgs, { topicInlineReply: true }),
                            ["form"]
                        ),
                        [
                            h("div", { className: "form__item u-mg-bottom-m" }, [
                                h(
                                    "label",
                                    {
                                        className:
                                            "form__label u-mg-bottom-xs u-txt-s u-txt-gray4",
                                        htmlFor: "body",
                                    },
                                    ["Reply"]
                                ),
                                h(
                                    "textarea",
                                    {
                                        id: "body",
                                        className:
                                            "form__input form__input--shadowed form__input--bordered",
                                        name: "body",
                                        rows: 4,
                                        dataset: {
                                            formAnchor: true,
                                        },
                                    },
                                    [this.defaultText]
                                ),
                            ]),
                            h("div", { className: "form__item" }, [
                                h(
                                    "button",
                                    {
                                        className: "btn btn--shadowed btn--primary",
                                        type: "submit",
                                    },
                                    ["Post Reply"]
                                ),
                                " ",
                                h("span", { className: "u-txt-gray4" }, [
                                    h(
                                        "input",
                                        {
                                            id: "bumped",
                                            type: "checkbox",
                                            name: "bumped",
                                            value: "y",
                                            checked: true,
                                            dataset: {
                                                topicStateTracker: "bump",
                                            },
                                        },
                                        []
                                    ),
                                    " ",
                                    h("label", { htmlFor: "bumped" }, [
                                        "Bump this topic",
                                    ]),
                                ]),
                            ]),
                        ]
                    ),
                ]),
            ]),
        ]);
    }
}
