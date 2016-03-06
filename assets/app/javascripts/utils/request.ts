import {CancellableToken, Cancelled} from './cancellable';


export function request(
    method: string,
    url: string,
    token?: CancellableToken
): Promise<string> {
    let xhr = new XMLHttpRequest();
    xhr.open(method, url);

    return new Promise(function(resolve, reject) {
        xhr.onload = function() { resolve(xhr.responseText); }
        xhr.onerror = reject;
        if (token) {
            token.cancel = function(): void {
                xhr.abort();
                reject(new Cancelled);
            }
        }
        xhr.send();
    });
}
