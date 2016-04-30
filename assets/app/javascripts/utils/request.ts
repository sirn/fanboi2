import {CancellableToken, Cancelled} from './cancellable';


export interface IRequestBody {
    [key: string]: any;
}


export function request(
    method: string,
    url: string,
    params?: IRequestBody,
    token?: CancellableToken
): Promise<string> {
    let xhr = new XMLHttpRequest();
    xhr.open(method, url);

    let body: string = null;
    if (params) {
        xhr.setRequestHeader('Content-Type', 'application/json');
        body = JSON.stringify(params);
    }

    return new Promise(function(resolve, reject) {
        xhr.onload = function() { resolve(xhr.responseText); }
        xhr.onerror = reject;
        if (token) {
            token.cancel = function(): void {
                xhr.abort();
                reject(new Cancelled);
            }
        }
        xhr.send(body);
    });
}
