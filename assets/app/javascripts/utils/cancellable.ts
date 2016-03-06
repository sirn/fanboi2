export interface CancellableToken {
    cancel: (() => void);
}


export class Cancelled extends Error {
    name: string;

    constructor(public message?: string) {
        super();
        this.name = 'Cancelled';
        if (!this.message) {
            this.message = 'Promise was explicitly aborted by user.';
        }
    }
}


export class CancelToken implements CancellableToken {
    cancel(): void {}
};
