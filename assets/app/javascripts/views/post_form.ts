import { VNode, h } from "virtual-dom";

export class PostForm {
    postFormNode: VNode;

    constructor(defaultText: string = "") {
        this.postFormNode = PostForm.renderForm(defaultText);
    }

    render(): VNode {
        return this.postFormNode;
    }

    private static renderForm(defaultText: string): VNode {
        return h("div", { className: "js-post-form" }, [
            h(
                "form",
                {
                    className: "form",
                    dataset: {
                        topicInlineReply: true,
                    },
                },
                [
                    h("div", { className: "container" }, [
                        h("div", { className: "form-item" }, [
                            PostForm.renderBodyFormItemLabel(),
                            PostForm.renderBodyFormItemInput(defaultText),
                        ]),
                        h("div", { className: "form-item" }, [
                            PostForm.renderPostFormItemButton(),
                            " ",
                            PostForm.renderPostFormItemBump(),
                        ]),
                    ]),
                ],
            ),
        ]);
    }

    private static renderBodyFormItemLabel(): VNode {
        return h(
            "label",
            {
                className: "form-item-label",
                htmlFor: "js-body",
            },
            ["Reply"],
        );
    }

    private static renderBodyFormItemInput(defaultText: string): VNode {
        return h(
            "textarea",
            {
                id: "js-body",
                className: "input block content",
                name: "body",
                rows: 4,
                dataset: {
                    formAnchor: true,
                },
            },
            [defaultText],
        );
    }

    private static renderPostFormItemButton(): VNode {
        return h(
            "button",
            {
                className: "button green",
                type: "submit",
            },
            ["Post Reply"],
        );
    }

    private static renderPostFormItemBump(): VNode {
        return h("span", { className: "form-item-inline" }, [
            PostForm.renderPostFormItemBumpInput(),
            " ",
            PostForm.renderPostFormItemBumpLabel(),
        ]);
    }

    private static renderPostFormItemBumpInput(): VNode {
        return h(
            "input",
            {
                id: "js-bumped",
                type: "checkbox",
                name: "bumped",
                value: "y",
                checked: true,
                dataset: {
                    topicStateTracker: "bump",
                },
            },
            [],
        );
    }

    private static renderPostFormItemBumpLabel(): VNode {
        return h("label", { htmlFor: "js-bumped" }, ["Bump this topic"]);
    }
}
