import {ITopicEventHandler} from './base';


export class TopicState implements ITopicEventHandler {
    stateName: string;
    state: any;

    constructor(public topicId: number, public element: Element) {
        this.stateName = `topic/${topicId}`;
        this.state = {};

        let stateString = localStorage.getItem(this.stateName);
        if (stateString) {
            this.state = JSON.parse(stateString);
        }
    }

    bind(event: CustomEvent): void {
        switch (event.type) {
        case 'readState':
            this.bindReadState(event);
            break;
        case 'updateState':
            this.bindUpdateState(event);
            break;
        }
    }

    private bindReadState(e: CustomEvent): void {
        let name: string = e.detail.name;
        let callback: ((name: string, value: any) => void) = e.detail.callback;

        if (!name) { throw new Error('readState require a name'); }
        if (!callback) { throw new Error('readState require a callback'); }

        callback(name, this.state[name]);
    }

    private bindUpdateState(e: CustomEvent): void {
        let name: string = e.detail.name;
        let value: any = e.detail.value;
        let callback: ((name: string, value: any) => void) = e.detail.callback;

        if (!name) { throw new Error('updateState require a name'); }

        this.state[name] = value;
        localStorage.setItem(this.stateName, JSON.stringify(this.state));

        if (callback) {
            callback(name, value);
        }
    }
}
