import {create, h} from 'virtual-dom';
import {SingletonComponent} from './base';
import {ResourceError} from '../utils/errors';
import {serializeForm} from '../utils/forms';
import {Post} from '../models/post';


export class InlineReply extends SingletonComponent {
    public targetSelector = '[data-inline-reply]';

    topicId: number;
    formElement: HTMLFormElement;
    buttonElement: Element;
    loadingState: boolean;

    protected bindOne(element: Element) {
        let self = this;

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

        if (!this.loadingState) {
            let formData = serializeForm(this.formElement);

            this.detachErrors();
            this.updateLoadingState(true);

            Post.createOne(this.topicId, formData).then(function(post: Post) {
                self.updateLoadingState(false);
                self.formElement.reset();
                self.formElement.dispatchEvent(new CustomEvent('reloadTopic', {
                    bubbles: true,
                    detail: {
                        topicId: self.topicId,
                        caller: self
                    }
                }));
            }).catch(function(error: ResourceError) {
                self.updateLoadingState(false);
                self.attachErrors(error);
            });
        }
    }

    private updateLoadingState(loadingState: boolean): void {
        let loadingClass = 'js-button-loading';
        let btnClasses = this.buttonElement.className.split(' ');
        let loadingClassIdx = btnClasses.indexOf(loadingClass);

        if (loadingClassIdx > 0) { btnClasses.splice(loadingClassIdx, 1); }
        if (loadingState) { btnClasses.push(loadingClass); }

        this.buttonElement.className = btnClasses.join(' ');
        this.loadingState = loadingState;
    }

    private detachErrors(): void {
        let errorElements = this.formElement.querySelectorAll('.error');
        for (let i = 0, len = errorElements.length; i < len; i++) {
            let errorElement = errorElements[0];
            let className = errorElement.className.split(' ');
            let classErrorIdx = className.indexOf('error');

            if (classErrorIdx > 0) {
                className.splice(classErrorIdx, 1);
                errorElement.className = className.join(' ');
            }
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
        let formItemClass = formItemElement.className.split(' ');

        formItemClass.push('error');
        formItemElement.className = formItemClass.join(' ');

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
