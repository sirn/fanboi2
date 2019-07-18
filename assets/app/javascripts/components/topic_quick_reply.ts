import { VNode, create, diff, patch } from "virtual-dom";

import { DelegationComponent } from "./base";
import { TopicInlineReply } from "./topic_inline_reply";
import { TopicStateTracker } from "./topic_state_tracker";

import { PopoverView } from "../views/popover_view";
import { PostForm } from "../views/post_form";
import { dispatchCustomEvent } from "../utils/elements";

export class TopicQuickReply extends DelegationComponent {
    public targetSelector = "[data-topic-quick-reply]";

    protected bindGlobal(): void {
        document.body.addEventListener("click", (e: Event): void => {
            let $target = e.target;

            if ($target instanceof Element && $target.matches(this.targetSelector)) {
                let anchor = $target.getAttribute("data-topic-quick-reply");
                let $topic = $target.closest("[data-topic]");
                e.preventDefault();

                if (!anchor) {
                    throw new Error("Reply anchor is empty when it should not.");
                }

                if ($topic) {
                    let $input = $topic.querySelector("[data-topic-quick-reply-input]");

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
        let $parent = $target.closest(".js-popover");
        let $popover: Element;
        let popoverView: PopoverView;
        let popoverNode: VNode;
        let throttleTimer: number;

        if (!$parent) {
            $parent = $topic;
        }

        let _removePopover = () => {
            $topic.removeEventListener("postCreated", _removePopover);
            document.body.removeEventListener("click", _clickRemovePopover);
            window.removeEventListener("resize", _repositionPopover);

            if ($parent) {
                $parent.removeChild($popover);
            }
        };

        popoverView = new PopoverView(
            new PostForm().render(),
            "Quick Reply",
            _removePopover,
        );

        let _repositionPopover = () => {
            clearTimeout(throttleTimer);
            throttleTimer = window.setTimeout(() => {
                if ($popover) {
                    let newPopoverNode = popoverView.render($target);
                    let patches = diff(popoverNode, newPopoverNode);

                    $popover = patch($popover, patches);
                    popoverNode = newPopoverNode;
                }
            }, 100);
        };

        let _clickRemovePopover = (e: Event) => {
            let _n = e.target;

            while (_n instanceof Node && _n != $popover) {
                _n = _n.parentNode;
            }

            if (_n != $popover) {
                _removePopover();
            }
        };

        popoverNode = popoverView.render($target);
        $popover = create(popoverNode);
        $parent.appendChild($popover);

        new TopicInlineReply($popover);
        new TopicStateTracker($popover);

        let $textarea = $popover.querySelector("textarea");
        if ($textarea instanceof HTMLTextAreaElement) {
            this.insertTextAtCursor($textarea, anchor);
        }

        document.body.addEventListener("click", _clickRemovePopover);
        $topic.addEventListener("postCreated", _removePopover);
        window.addEventListener("resize", _repositionPopover);
    }
}
