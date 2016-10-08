import {create, h} from 'virtual-dom';

import {SingletonComponent} from './base';
import {ResourceError} from '../utils/errors';
import {LoadingState} from '../utils/loading';

import {
    addClass,
    removeClass,
    dispatchCustomEvent,
    serializeForm
} from '../utils/elements';


export class TopicInlineReply extends SingletonComponent {
    public targetSelector = '[data-topic-inline-reply]';

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
            this.formElement.getAttribute('data-topic-inline-reply'),
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
            return new Promise(function(resolve) {
                dispatchCustomEvent(self.formElement, 'newPost', {
                    params: serializeForm(self.formElement),
                    callback: function() {
                        self.detachErrors();
                        self.formElement.reset();
                        resolve();
                    },
                    errorCallback: function(error: ResourceError) {
                        self.detachErrors();
                        self.attachErrors(error);
                        resolve();
                    }
                });
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
            let anchorSelector = '[data-topic-inline-reply-anchor]';
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
