import { ITopicEventHandler } from "./base";
import { Post } from "../../models/post";
import { dispatchCustomEvent } from "../../utils/elements";
import { ResourceError } from "../../utils/errors";
import { LoadingState } from "../../utils/loading";

export class TopicNewPost implements ITopicEventHandler {
    loadingState: LoadingState;

    constructor(public topicId: number, public element: Element) {
        this.loadingState = new LoadingState();
    }

    bind(e: CustomEvent): void {
        let params: any = e.detail.params;
        let callback: ((lastPostNumber: number) => void) = e.detail.callback;
        let errCb: ((error: ResourceError) => void) = e.detail.errorCallback;

        if (!params) {
            throw new Error("newPost require a params");
        }

        this.loadingState.bind(() => {
            return Post.createOne(this.topicId, params)
                .then(() => {
                    dispatchCustomEvent(this.element, "postCreated");
                    dispatchCustomEvent(this.element, "loadPosts", {
                        callback: (lastPostNumber: number) => {
                            if (callback) {
                                callback(lastPostNumber);
                            }
                        },
                    });
                })
                .catch((error: ResourceError) => {
                    if (errCb) {
                        errCb(error);
                        dispatchCustomEvent(this.element, "postCreateError", {
                            error: error,
                        });
                    }
                });
        });
    }
}
