import { CancellableToken, Cancelled } from "./cancellable";

export interface IRequestBody {
    [key: string]: any;
}

export const request = (
    method: string,
    url: string,
    params: IRequestBody = {},
    token?: CancellableToken,
): Promise<string> => {
    let xhr = new XMLHttpRequest();
    let body = JSON.stringify(params);

    xhr.open(method, url);
    xhr.setRequestHeader("Content-Type", "application/json");

    return new Promise((resolve, reject) => {
        xhr.onload = () => {
            resolve(xhr.responseText);
        };
        xhr.onerror = reject;

        if (token) {
            token.cancel = (): void => {
                xhr.abort();
                reject(new Cancelled());
            };
        }

        xhr.send(body);
    });
};
