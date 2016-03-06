export class NotImplementedError extends Error {
    name: string;

    constructor(public message?: string) {
        super();
        this.name = 'NotImplementedError';
        if (!this.message) {
            this.message = 'The method was called but not implemented.';
        }
    }
}
