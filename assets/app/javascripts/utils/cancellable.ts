import {Error} from './errors';


export interface CancellableToken {
    cancel: (() => void);
}


export class Cancelled implements Error {
    public name = 'Cancelled';

    constructor(public message?: string) {
        this.message = message;
        if (!this.message) {
            this.message = 'Promise was explicitly aborted by user.';
        }
    }
}


export class CancelToken implements CancellableToken {
    cancel(): void {}
};
