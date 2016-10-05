export interface Error {
    name: string;
    message?: string;
    object?: any;
}


export class NotImplementedError implements Error {
    public name = 'NotImplementedError';

    constructor(public message?: string, public object?: any) {
        if (!this.message) {
            this.message = 'The method was called but not implemented.';
        }
    }
}


export class ResourceError implements Error {
    public name = 'ResourceError';

    constructor(public message?: string, public object?: any) {
        if (!this.message) {
            this.message = 'The resource could not be retrieved from the API.';
        }
    }
}
