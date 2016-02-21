export interface CancellableToken {
    cancel: (() => void);
}

export class CancelToken implements CancellableToken {
    cancel(): void {}
};
