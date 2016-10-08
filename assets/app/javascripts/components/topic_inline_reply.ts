import {create, h} from 'virtual-dom';

import {SingletonComponent} from './base';
import {ResourceError} from '../utils/errors';
import {dispatchCustomEvent} from '../utils/elements';
import {attachErrors, detachErrors, serializeForm} from '../utils/forms';
import {LoadingState} from '../utils/loading';


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
                        detachErrors(self.formElement);
                        self.formElement.reset();
                        resolve();
                    },
                    errorCallback: function(error: ResourceError) {
                        detachErrors(self.formElement);
                        attachErrors(self.formElement, error);
                        resolve();
                    }
                });
            });
        });
    }
}
