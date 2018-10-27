import { create, h } from "virtual-dom";

import { SingletonComponent } from "./base";
import { ResourceError } from "../utils/errors";
import { dispatchCustomEvent } from "../utils/elements";
import { attachErrors, detachErrors, serializeForm } from "../utils/forms";
import { LoadingState } from "../utils/loading";

export class TopicInlineReply extends SingletonComponent {
    public targetSelector = "[data-topic-inline-reply]";

    protected bindOne($target: Element) {
        let $form = $target;

        if ($form instanceof HTMLFormElement) {
            let $button = $target.querySelector("button");
            let loadingState = new LoadingState();

            $form.addEventListener("submit", (e: Event): void => {
                if ($button) {
                    e.preventDefault();
                    loadingState.bind(() => {
                        return new Promise(resolve => {
                            if ($form instanceof HTMLFormElement) {
                                dispatchCustomEvent($form, "newPost", {
                                    params: serializeForm($form),
                                    callback: () => {
                                        if ($form instanceof HTMLFormElement) {
                                            detachErrors($form);
                                            $form.reset();
                                            resolve();
                                        }
                                    },
                                    errorCallback: (error: ResourceError) => {
                                        if ($form instanceof HTMLFormElement) {
                                            detachErrors($form);
                                            attachErrors($form, error);
                                            resolve();
                                        }
                                    },
                                });
                            }
                        });
                    }, $button);
                }
            });
        }
    }
}
