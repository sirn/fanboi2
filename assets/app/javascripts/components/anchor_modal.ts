import { create, VNode } from "virtual-dom";
import { Board } from "../models/board";
import { Post } from "../models/post";
import { Topic } from "../models/topic";
import { CancelToken } from "../utils/cancellable";
import { BoardView } from "../views/board_view";
import { ModalView } from "../views/modal_view";
import { PostCollectionView } from "../views/post_collection_view";
import { TopicView } from "../views/topic_view";
import { DelegationComponent } from "./base";
import { TopicManager } from "./topic_manager";

export class AnchorModal extends DelegationComponent {
    public targetSelector = "[data-anchor]";

    protected bindGlobal(): void {
        document.body.addEventListener("pointerover", (e: PointerEvent): void => {
            if (e.target instanceof Element) {
                if (e.target.matches(this.targetSelector)) {
                    e.preventDefault();
                    AnchorModal.attach(e.target);
                }
            }
        });
    }

    private static attach($target: Element): void {
        let $parent = $target.closest("[data-modal]");

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

            let render = async (): Promise<VNode | undefined> => {
                if (topicId && postNumber) {
                    let posts = await Post.queryAll(topicId, postNumber, cancelToken);
                    if (!posts.length) {
                        return undefined;
                    }

                    return new PostCollectionView(posts).render({
                        post: {
                            container: {
                                className: "u-mg-horizontal-s-desktop",
                            },
                        },
                    });
                } else if (topicId && !postNumber) {
                    let topic = await Topic.queryId(topicId, cancelToken);
                    if (!topic) {
                        return undefined;
                    }

                    return new TopicView(topic).render({
                        container: {
                            className: [
                                "u-mg-horizontal-s-desktop",
                                "u-pd-vertical-s",
                            ].join(" "),
                        },
                        panel: {
                            className: "panel--shade2",
                        },
                        title: {
                            className: "u-txt-gray4",
                        },
                    });
                } else {
                    let board = await Board.querySlug(boardSlug, cancelToken);
                    if (!board) {
                        return undefined;
                    }

                    return new BoardView(board).render({
                        container: {
                            className: [
                                "u-mg-horizontal-s-desktop",
                                "u-pd-vertical-s",
                            ].join(" "),
                        },
                        panel: {
                            className: "panel--shade2",
                        },
                    });
                }
            };

            let finalizeRequest = () => {
                cancelToken.cancel();
                $target.removeEventListener("pointerleave", finalizeRequest);
            };

            $target.addEventListener("pointerleave", finalizeRequest);

            render().then((node: VNode | undefined): void => {
                if (!node) {
                    return;
                }

                let $modal: Element;
                /* Clamp to 640px for post collection; 320px otherwise */
                let modalClampWidth = postNumber ? 640 : 320;
                let modalView = new ModalView(node);
                let modalArgs = {
                    clampWidth: modalClampWidth,
                    modal: {
                        className: "modal--shadowed modal--bordered",
                        style: {
                            /* Minimum viewport size since post width may fit
                             * 320px in mobile view. */
                            minWidth: "320px",
                        },
                    },
                };

                let modalNode = modalView.render($target, modalArgs);
                let rebindTopic: boolean = false;
                let dismissTimer: number = 0;

                let detach = (): void => {
                    if ($parent && $modal && $modal.parentNode) {
                        $parent.removeChild($modal);
                        $target.removeEventListener("pointerleave", detachOnTarget);
                        document.body.removeEventListener("pointerover", detachOnModal);
                    }
                };

                let switchDetachMode = (e: PointerEvent): void => {
                    e.preventDefault();
                    clearTimeout(dismissTimer);

                    $modal.removeEventListener("pointerover", switchDetachMode);
                    document.body.addEventListener("pointerover", detachOnModal);
                };

                let detachOnModal = (e: PointerEvent): void => {
                    e.preventDefault();

                    let n = e.target;
                    while (n && n instanceof Node && n != $modal) {
                        n = n.parentNode;
                    }

                    if (n != $modal) {
                        detach();
                    }
                };

                let detachOnTarget = (e: PointerEvent): void => {
                    e.preventDefault();

                    // If $modal is already rendered then wait and
                    // see if user will move mouse into the quote; otherwise
                    // immediately detach.
                    if ($modal.parentNode) {
                        dismissTimer = window.setTimeout((): void => {
                            detach();
                        }, 100);
                    } else {
                        detach();
                    }
                };

                finalizeRequest();

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

                    // Wrong context; re-render.
                    if (topicId != localTopicId) {
                        rebindTopic = true;
                        modalNode = modalView.render($target, {
                            ...modalArgs,
                            wrapper: {
                                dataset: {
                                    topic: topicId,
                                },
                            },
                        });
                    }
                }

                if ($parent) {
                    $modal = create(modalNode);
                    $parent.appendChild($modal);

                    if (rebindTopic) {
                        new TopicManager($parent);
                    }

                    $target.addEventListener("pointerleave", detachOnTarget);
                    $modal.addEventListener("pointerover", switchDetachMode);
                }
            });
        }
    }
}
