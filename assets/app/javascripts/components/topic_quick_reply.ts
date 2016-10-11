import {VNode, create, diff, patch} from 'virtual-dom';

import {DelegationComponent} from './base';
import {TopicInlineReply} from './topic_inline_reply';
import {TopicStateTracker} from './topic_state_tracker';

import {PopoverView} from '../views/popover_view';
import {PostForm} from '../views/post_form';
import {dispatchCustomEvent} from '../utils/elements';


export class TopicQuickReply extends DelegationComponent {
    public targetSelector = '[data-topic-quick-reply]';

    protected bindGlobal(): void {
        let self = this;

        document.body.addEventListener('click', function(e: Event): void {
            let element = <Element>e.target;
            if (element.matches(self.targetSelector)) {
                e.preventDefault();

                let anchor = element.getAttribute('data-topic-quick-reply');
                let topicElement = element.closest('[data-topic]');
                let inputElement = topicElement.querySelector(
                    '[data-topic-quick-reply-input]'
                );

                if (inputElement) {
                    self.insertTextAtCursor(
                        <HTMLTextAreaElement>inputElement,
                        anchor
                    );
                } else {
                    self.attachForm(
                        element,
                        topicElement,
                        anchor
                    );
                }
            }
        });
    }

    private insertTextAtCursor(
        element: HTMLTextAreaElement,
        anchor: string
    ): void {
        let anchorText = `>>${anchor} `;
        let startPos = element.selectionStart;
        let endPos = element.selectionEnd;
        let currentValue = element.value;

        element.value =
            currentValue.substring(0, startPos) +
            anchorText +
            currentValue.substring(endPos, currentValue.length);

        element.focus();
        element.dispatchEvent(new Event('change'));
        element.selectionStart = startPos + anchorText.length;
    }

    private attachForm(
        element: Element,
        topicElement: Element,
        anchor: string
    ): void {
        let throttleTimer: number;
        let parentElement = element.closest('.js-popover');
        let title = "Quick Reply";

        if (!parentElement) {
            parentElement = topicElement;
        }

        let postFormView = new PostForm().render();
        let popoverView = new PopoverView(
            element,
            postFormView,
            title,
            _removePopover
        ).render();

        let popoverElement = create(popoverView);
        parentElement.insertBefore(popoverElement, null);

        new TopicInlineReply(popoverElement);
        new TopicStateTracker(popoverElement);

        let textareaElement = popoverElement.querySelector('textarea');
        this.insertTextAtCursor(textareaElement, anchor);

        function _repositionPopover() {
            clearTimeout(throttleTimer);
            throttleTimer = setTimeout(function(){
                if (popoverElement) {
                    let newPopoverView = new PopoverView(
                        element,
                        postFormView,
                        title,
                        _removePopover
                    ).render();

                    let patches = diff(popoverView, newPopoverView);
                    popoverElement = patch(popoverElement, patches);
                    popoverView = newPopoverView;
                }
            }, 100);
        }

        function _clickRemovePopover(e: Event) {
            let _n = <Node>e.target;
            while (_n && _n != popoverElement) { _n = _n.parentNode; }
            if (_n != popoverElement) { _removePopover(); }
        }

        function _removePopover() {
            topicElement.removeEventListener('postCreated', _removePopover);
            document.body.removeEventListener('click', _clickRemovePopover);
            window.removeEventListener('resize', _repositionPopover);
            parentElement.removeChild(popoverElement);
        }

        document.body.addEventListener('click', _clickRemovePopover);
        topicElement.addEventListener('postCreated', _removePopover);
        window.addEventListener('resize', _repositionPopover);
    }
}
