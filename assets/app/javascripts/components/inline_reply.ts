import {create, h} from 'virtual-dom';

import {SingletonComponent} from './base';
import {Post} from '../models/post';
import {addClass, removeClass, serializeForm} from '../utils/elements';
import {ResourceError} from '../utils/errors';
import {LoadingState} from '../utils/loading';


export class InlineReply extends SingletonComponent {
    public targetSelector = '[data-inline-reply]';

    topicId: number;
    formElement: HTMLFormElement;
    buttonElement: Element;
    loadingState: LoadingState;

    protected bindOne(element: Element) {
        let self = this;

        this.loadingState = new LoadingState();
        this.formElement = <HTMLFormElement>element;
        this.buttonElement = element.querySelector('button');
        this.topicId = parseInt(
            this.formElement.getAttribute('data-inline-reply'),
            10
        );

        this.formElement.addEventListener('submit', function(e: Event): void {
            e.preventDefault();
            self.eventFormSubmitted();
        });
    }

    private eventFormSubmitted(): void {
        let self = this;

        this.loadingState.bind(this.buttonElement, function() {
            return Post.createOne(
                self.topicId,
                serializeForm(self.formElement)
            ).then(function(post: Post) {
                self.detachErrors();
                self.formElement.reset();
                self.formElement.dispatchEvent(new CustomEvent('reloadTopic', {
                    bubbles: true,
                    detail: {
                        topicId: self.topicId,
                        caller: self
                    }
                }));
            }).catch(function(error: ResourceError) {
                self.detachErrors();
                self.attachErrors(error);
            });
        });
    }

    private detachErrors(): void {
        let errorElements = this.formElement.querySelectorAll('.error');
        for (let i = 0, len = errorElements.length; i < len; i++) {
            let errorElement = errorElements[0];
            removeClass(errorElement, 'error');
        }

        let msgElements = this.formElement.querySelectorAll('.form-item-error');
        for (let i = 0, len = msgElements.length; i < len; i++) {
            let msgElement = msgElements[0];
            msgElement.parentElement.removeChild(msgElement);
        }
    }

    private attachErrors(error: ResourceError): void {
        let data = error.object;
        if (data.status == 'params_invalid') {
            for (let field in <{[key: string]: string[]}>data.message) {
                if (data.message.hasOwnProperty(field)) {
                    let fieldElement = this.formElement[field];
                    let messages = data.message[field];
                    this.attachError(fieldElement, messages[0]);
                }
            }
        } else {
            let anchorSelector = '[data-inline-reply-anchor]';
            let anchorElement = this.formElement.querySelector(anchorSelector);
            this.attachError(anchorElement, data.message);
        }
    }

    private attachError(fieldElement: Element, message: string): void {
        let formItemElement = fieldElement.closest('.form-item');
        addClass(formItemElement, 'error');

        let errorNode = h('span',
            {className: 'form-item-error'},
            [String(message)]
        );

        fieldElement.parentElement.insertBefore(
            create(errorNode),
            fieldElement.nextSibling
        );
    }
}
