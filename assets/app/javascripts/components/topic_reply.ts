import { create, diff, patch, VNode } from "virtual-dom";
import { ModalView } from "../views/modal_view";
import { PostForm } from "../views/post_form";
import { DelegationComponent } from "./base";
import { TopicReplyForm } from "./topic_reply_form";
import { TopicStateTracker } from "./topic_state_tracker";

export class TopicReply extends DelegationComponent {
    public targetSelector = "[data-topic-reply]";

    protected bindGlobal(): void {
        document.body.addEventListener("click", (e: Event): void => {
            let $target = e.target;

            if ($target instanceof Element && $target.matches(this.targetSelector)) {
                let anchor = $target.getAttribute("data-topic-reply");
                let $topic = $target.closest("[data-topic]");
                e.preventDefault();

                if (!anchor) {
                    throw new Error("Reply anchor is empty when it should not.");
                }

                if ($topic) {
                    let $input = $topic.querySelector("[data-topic-reply-input]");

                    if ($input instanceof HTMLTextAreaElement) {
                        this.insertTextAtCursor($input, anchor);
                    } else {
                        this.attachForm($target, $topic, anchor);
                    }
                }
            }
        });
    }

    private insertTextAtCursor($input: HTMLTextAreaElement, anchor: string): void {
        let anchorText = `>>${anchor} `;
        let startPos = $input.selectionStart;
        let endPos = $input.selectionEnd;
        let currentValue = $input.value;

        $input.value =
            currentValue.substring(0, startPos) +
            anchorText +
            currentValue.substring(endPos, currentValue.length);

        $input.focus();
        $input.dispatchEvent(new Event("change"));
        $input.selectionStart = startPos + anchorText.length;
    }

    private attachForm($target: Element, $topic: Element, anchor: string): void {
        let $parent = $target.closest("[data-modal]");
        let $modal: Element;
        let modalView: ModalView;
        let modalNode: VNode;
        let throttleTimer: number;
        let modalArgs = {
            modal: {
                className: "modal--shadowed modal--bordered",
                style: {
                    minWidth: `${Math.min(
                        Math.max(320, window.visualViewport.width),
                        720
                    )}px`,
                },
            },
        };

        if (!$parent) {
            $parent = $topic;
        }

        let removeModal = () => {
            $topic.removeEventListener("postCreated", removeModal);
            document.body.removeEventListener("click", clickRemoveModal);
            window.removeEventListener("resize", repositionModal);

            if ($parent) {
                $parent.removeChild($modal);
            }
        };

        modalView = new ModalView(
            new PostForm().render({
                container: {
                    className: ["u-mg-horizontal-s-desktop", "u-pd-vertical-s"].join(
                        " "
                    ),
                },
            }),
            "Quick Reply",
            removeModal
        );

        let repositionModal = () => {
            clearTimeout(throttleTimer);
            throttleTimer = window.setTimeout(() => {
                if ($modal) {
                    let newModalNode = modalView.render($target, modalArgs);
                    let patches = diff(modalNode, newModalNode);

                    $modal = patch($modal, patches);
                    modalNode = newModalNode;
                }
            }, 100);
        };

        let clickRemoveModal = (e: Event) => {
            let _n = e.target;

            while (_n instanceof Node && _n != $modal) {
                _n = _n.parentNode;
            }

            if (_n != $modal) {
                removeModal();
            }
        };

        modalNode = modalView.render($target, modalArgs);
        $modal = create(modalNode);
        $parent.appendChild($modal);

        new TopicReplyForm($modal);
        new TopicStateTracker($modal);

        let $textarea = $modal.querySelector("textarea");
        if ($textarea instanceof HTMLTextAreaElement) {
            this.insertTextAtCursor($textarea, anchor);
        }

        document.body.addEventListener("click", clickRemoveModal);
        $topic.addEventListener("postCreated", removeModal);
        window.addEventListener("resize", repositionModal);
    }
}
