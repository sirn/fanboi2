export interface Error {
    name: string;
    message: string;
    object?: any;
}

export class NotImplementedError implements Error {
    public name = "NotImplementedError";

    constructor(
        public message: string = "The method was called but not implemented.",
        public object?: any,
    ) {}
}

export class ResourceError implements Error {
    public name = "ResourceError";

    constructor(
        public message: string = "The resource could not be retrieved.",
        public object?: any,
    ) {}
}
