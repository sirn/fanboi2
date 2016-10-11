import {CollectionComponent} from './base';
import {dispatchCustomEvent} from '../utils/elements';


export class TopicStateTracker extends CollectionComponent {
    public targetSelector = '[data-topic-state-tracker]';

    protected bindOne(element: Element): void {
        let trackerName = element.getAttribute('data-topic-state-tracker');

        if (element instanceof HTMLInputElement) {
            switch (element.type) {
            case 'checkbox':
                this.bindCheckbox(trackerName, element);
                break;
            }
        } else if (element instanceof HTMLTextAreaElement) {
            this.bindTextarea(trackerName, element);
        }
    }

    private bindCheckbox(
        trackerName: string,
        element: HTMLInputElement
    ): void {
        let self = this;

        dispatchCustomEvent(element, 'readState', {
            name: trackerName,
            callback: function(name: string, value: boolean | null) {
                if (value != null) {
                    element.checked = value;
                    element.defaultChecked = element.checked;
                }
            }
        });

        element.addEventListener('change', function(e: Event): void {
            element.defaultChecked = element.checked;
            dispatchCustomEvent(element, 'updateState', {
                name: trackerName,
                value: element.checked
            });
        });
    }

    private bindTextarea(
        trackerName: string,
        element: HTMLTextAreaElement
    ): void {
        let self = this;
        let throttleTimer: number;

        dispatchCustomEvent(element, 'readState', {
            name: trackerName,
            callback: function(name: string, value: string | null) {
                if (value != null) {
                    element.value = value;
                }
            }
        });

        element.addEventListener('change', function(e: Event): void {
            clearTimeout(throttleTimer);
            throttleTimer = setTimeout(function(){
                dispatchCustomEvent(element, 'updateState', {
                    name: trackerName,
                    value: element.value
                });
            }, 500);
        });
    }
}
