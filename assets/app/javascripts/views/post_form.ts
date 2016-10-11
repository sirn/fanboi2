import {VNode, h} from 'virtual-dom';


export class PostForm {
    render(defaultText?: string): VNode {
        return h('div', {className: 'js-post-form'}, [
            h('form', {
                className: 'form',
                dataset: {
                    topicInlineReply: true
                }
            }, [
                h('div', {className: 'container'}, [
                    PostForm.renderBodyFormItem(defaultText),
                    PostForm.renderPostFormItem()
                ])
            ])
        ]);
    }

    private static renderBodyFormItem(defaultText?: string): VNode {
        return h('div', {className: 'form-item'}, [
            PostForm.renderBodyFormItemLabel(),
            PostForm.renderBodyFormItemInput(defaultText),
        ]);
    }

    private static renderBodyFormItemLabel(): VNode {
        return h('label', {
            className: 'form-item-label',
            htmlFor: 'js-body',
        }, [String('Reply')]);
    }

    private static renderBodyFormItemInput(defaultText?: string): VNode {
        return h('textarea', {
            id: 'js-body',
            className: 'input block content',
            name: 'body',
            rows: 4,
            dataset: {
                formAnchor: true,
            },
        }, [defaultText]);
    }

    private static renderPostFormItem(): VNode {
        return h('div', {className: 'form-item'}, [
            PostForm.renderPostFormItemButton(),
            String(' '),
            PostForm.renderPostFormItemBump(),
        ]);
    }

    private static renderPostFormItemButton(): VNode {
        return h('button', {
            className: 'button green',
            type: 'submit'
        }, [String('Post Reply')]);
    }

    private static renderPostFormItemBump(): VNode {
        return h('span', {className: 'form-item-inline'}, [
            PostForm.renderPostFormItemBumpInput(),
            String(' '),
            PostForm.renderPostFormItemBumpLabel(),
        ]);
    }

    private static renderPostFormItemBumpInput(): VNode {
        return h('input', {
            id: 'js-bumped',
            type: 'checkbox',
            name: 'bumped',
            value: 'y',
            checked: true,
            dataset: {
                topicStateTracker: 'bump',
            }
        }, []);
    }

    private static renderPostFormItemBumpLabel(): VNode {
        return h('label',
            {htmlFor: 'js-bumped'},
            [String('Bump this topic')
        ]);
    }
}
