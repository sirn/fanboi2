export interface CancellableToken {
    cancel: void|(() => void);
}

export class CancelToken implements CancellableToken {
    cancel: void
};
