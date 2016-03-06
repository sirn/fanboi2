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


export class ResourceError extends Error {
    name: string;

    constructor(public message?: string) {
        super();
        this.name = 'ResourceError';
        if (!this.message) {
            this.message = 'The resource could not be retrieved from the API.';
        }
    }
}
