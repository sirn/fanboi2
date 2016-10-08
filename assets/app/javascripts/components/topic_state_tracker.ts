import {CollectionComponent} from './base';
import {dispatchCustomEvent} from '../utils/elements';


export class TopicStateTracker extends CollectionComponent {
    public targetSelector = '[data-topic-state-tracker]';

    trackerName: string;

    protected bindOne(element: Element): void {
        this.trackerName = element.getAttribute('data-topic-state-tracker');

        if (element instanceof HTMLInputElement) {
            switch (element.type) {
            case 'checkbox':
                this.bindCheckbox(element);
                break;
            }
        }
    }

    private bindCheckbox(element: HTMLInputElement): void {
        dispatchCustomEvent(element, 'readState', {
            name: 'bump',
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
                name: 'bump',
                value: element.checked
            });
        });
    }
}
