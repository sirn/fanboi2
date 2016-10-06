import {CollectionComponent} from './base';


export class StateTracker extends CollectionComponent {
    public targetSelector = '[data-state-tracker]';

    protected bindOne(element: Element): void {
        if (element.nodeName == 'INPUT') {
            let inputElement = <HTMLInputElement>element;

            if (inputElement.type == 'checkbox') {
                this.bindCheckbox(inputElement);
            }
        }
    }

    private bindCheckbox(element: HTMLInputElement): void {
        let trackerName = this.getTrackerName(element);
        let lastState = StateTracker.getState(trackerName);

        if (lastState != null) {
            element.checked = lastState == 'true';
            element.defaultChecked = element.checked;
        }

        element.addEventListener('change', function(e: Event): void {
            StateTracker.storeState(trackerName, element.checked);
            element.defaultChecked = element.checked;
        });
    }

    private getTrackerName(element: Element): string {
        return element.getAttribute('data-state-tracker');
    }

    static storeState(trackerName: string, state: any): void {
        localStorage.setItem(trackerName, state);
    }

    static getState(trackerName: string): any | null {
        return localStorage.getItem(trackerName);
    }
}
