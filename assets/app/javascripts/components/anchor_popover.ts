import { VNode, create, diff, patch, h } from "virtual-dom";

import { DelegationComponent } from "./base";
import { TopicManager } from "./topic_manager";
import { Board } from "../models/board";
import { Post } from "../models/post";
import { Topic } from "../models/topic";
import { BoardView } from "../views/board_view";
import { PopoverView } from "../views/popover_view";
import { PostCollectionView } from "../views/post_collection_view";
import { TopicView } from "../views/topic_view";
import { CancellableToken, CancelToken } from "../utils/cancellable";

export class AnchorPopover extends DelegationComponent {
    public targetSelector = "[data-anchor]";

    protected bindGlobal(): void {
        document.body.addEventListener("mouseover", (e: Event): void => {
            if (e.target instanceof Element) {
                if (e.target.matches(this.targetSelector)) {
                    e.preventDefault();
                    AnchorPopover.attach(e.target);
                }
            }
        });
    }

    private static attach($target: Element): void {
        let $parent = $target.closest(".js-popover");

        if (!$parent) {
            $parent = $target.closest("[data-topic]");
        }

        if ($parent) {
            let cancelToken = new CancelToken();
            let boardSlug = $target.getAttribute("data-anchor-board") || "";
            let postNumber = $target.getAttribute("data-anchor") || "";
            let anchorAttr = $target.getAttribute("data-anchor-topic");
            let topicId: number = 0;

            if (anchorAttr) {
                topicId = parseInt(anchorAttr, 10);
            }

            let _render = () => {
                if (topicId && postNumber) {
                    return Post.queryAll(topicId, postNumber, cancelToken).then(
                        (posts: Post[]): VNode => {
                            return new PostCollectionView(posts).render();
                        },
                    );
                } else if (topicId && !postNumber) {
                    return Topic.queryId(topicId, cancelToken).then(
                        (topic: Topic): VNode => {
                            return new TopicView(topic).render();
                        },
                    );
                } else {
                    return Board.querySlug(boardSlug, cancelToken).then(
                        (board: Board): VNode => {
                            return new BoardView(board).render();
                        },
                    );
                }
            };

            let _finalizeRequest = () => {
                cancelToken.cancel();
                $target.removeEventListener("mouseout", _finalizeRequest);
            };

            $target.addEventListener("mouseout", _finalizeRequest);

            _render().then(node => {
                let $popover: Element;
                let popoverView = new PopoverView(node);
                let popoverNode = popoverView.render($target);
                let rebindTopic: boolean = false;
                let dismissTimer: number = 0;

                let _detach = (): void => {
                    if ($parent && $popover && $popover.parentNode) {
                        $parent.removeChild($popover);
                        $target.removeEventListener("mouseout", _detachOnTarget);
                        document.body.removeEventListener(
                            "mouseover",
                            _detachOnPopover,
                        );
                    }
                };

                let _switchDetachMode = (e: Event): void => {
                    e.preventDefault();
                    clearTimeout(dismissTimer);

                    $popover.removeEventListener("mouseover", _switchDetachMode);
                    document.body.addEventListener("mouseover", _detachOnPopover);
                };

                let _detachOnPopover = (e: Event): void => {
                    e.preventDefault();

                    let _n = e.target;
                    while (_n && _n instanceof Node && _n != $popover) {
                        _n = _n.parentNode;
                    }

                    if (_n != $popover) {
                        _detach();
                    }
                };

                let _detachOnTarget = (e: Event): void => {
                    e.preventDefault();

                    // If $popover is already rendered then wait and
                    // see if user will move mouse into the quote; otherwise
                    // immediately detach.
                    if ($popover.parentNode) {
                        dismissTimer = window.setTimeout((): void => {
                            _detach();
                        }, 100);
                    } else {
                        _detach();
                    }
                };

                _finalizeRequest();

                // Rebind [data-topic] when anchor is pointing to post from
                // another topic so that quick reply and etc. binds to the
                // correct context.
                if (topicId && postNumber) {
                    let $localTopic = $target.closest("[data-topic]");
                    let localTopicId: number = 0;

                    if ($localTopic) {
                        let topicAttr = $localTopic.getAttribute("data-topic");
                        if (topicAttr) {
                            localTopicId = parseInt(topicAttr, 10);
                        }
                    }

                    if (topicId != localTopicId) {
                        rebindTopic = true;
                        popoverNode = popoverView.render($target, {
                            dataset: {
                                topic: topicId,
                            },
                        });
                    }
                }

                if ($parent) {
                    $popover = create(popoverNode);
                    $parent.appendChild($popover);

                    if (rebindTopic) {
                        new TopicManager($parent);
                    }

                    $target.addEventListener("mouseout", _detachOnTarget);
                    $popover.addEventListener("mouseover", _switchDetachMode);
                }
            });
        }
    }
}
