import { VNode, create, diff, patch } from "virtual-dom";

import { ITopicEventHandler } from "./base";
import { Post } from "../../models/post";
import { PostCollectionView } from "../../views/post_collection_view";
import { dispatchCustomEvent } from "../../utils/elements";
import { LoadingState } from "../../utils/loading";

export class TopicLoadPosts implements ITopicEventHandler {
    lastPostNumber: number;

    loadedPosts: Post[];
    collectionElement: Element;
    collectionNode: VNode;
    loadingState: LoadingState;

    constructor(public topicId: number, public element: Element) {
        let postNumbers = element.querySelectorAll(".post-header-item.number");
        let lastPostNumber = postNumbers[postNumbers.length - 1];

        this.loadedPosts = [];
        this.lastPostNumber = parseInt(lastPostNumber.innerHTML, 10);
        this.loadingState = new LoadingState();
    }

    bind(e: CustomEvent): void {
        let callback: ((lastPostNumber: number) => void) = e.detail.callback;

        this.loadingState.bind(() => {
            return Post.queryAll(this.topicId, `${this.lastPostNumber + 1}-`).then(
                (posts: Post[]) => {
                    if (posts && posts.length) {
                        this.lastPostNumber = posts[posts.length - 1].number;
                        this.loadedPosts = this.loadedPosts.concat(posts);
                        this.appendPosts();
                        this.updateHistoryState();
                    }

                    if (callback) {
                        callback(this.lastPostNumber);
                    }

                    dispatchCustomEvent(this.element, "postsLoaded", {
                        lastPostNumber: this.lastPostNumber,
                    });
                },
            );
        });
    }

    private appendPosts(): void {
        let newCollectionNode = new PostCollectionView(this.loadedPosts).render();

        if (!this.collectionElement) {
            this.collectionElement = create(newCollectionNode);
            let postElements = this.element.querySelectorAll(".post");
            let lastElement = postElements[postElements.length - 1];
            if (lastElement && lastElement.parentElement) {
                lastElement.parentElement.insertBefore(
                    this.collectionElement,
                    lastElement.nextSibling,
                );
            }
        } else {
            let patches = diff(this.collectionNode, newCollectionNode);
            this.collectionElement = patch(this.collectionElement, patches);
        }

        this.collectionNode = newCollectionNode;
    }

    private updateHistoryState(): void {
        if (window.history.replaceState) {
            let path = window.location.pathname;
            let newPath: string = "";

            if (path.match(/\/\d+\/\d+\/?$/)) {
                newPath = path.replace(/\/(\d+)\/?$/, `/$1-${this.lastPostNumber}/`);
            } else if (path.match(/\-\d+\/?$/)) {
                newPath = path.replace(/(\d+)\/?$/, `${this.lastPostNumber}/`);
            }

            if (newPath) {
                window.history.replaceState(
                    undefined,
                    `Posts up to ${this.lastPostNumber}`,
                    newPath,
                );
            }
        }
    }
}
