import { Error } from "./errors";

export interface CancellableToken {
    cancel: (() => void);
}

export class Cancelled implements Error {
    public name = "Cancelled";

    constructor(
        public message: string = "Promise was explicitly aborted by the user.",
    ) {}
}

export class CancelToken implements CancellableToken {
    cancel(): void {}
}
