import {VNode, create, diff, patch, h} from 'virtual-dom';

import {DelegationComponent} from './base';
import {TopicManager} from './topic_manager';
import {Board} from '../models/board';
import {Post} from '../models/post';
import {Topic} from '../models/topic';
import {BoardView} from '../views/board_view';
import {PopoverView} from '../views/popover_view';
import {PostCollectionView} from '../views/post_collection_view';
import {TopicView} from '../views/topic_view';
import {CancellableToken, CancelToken} from '../utils/cancellable';


class AnchorPopoverHandler {
    targetElement: Element;
    quoteElement: Element;
    parentElement: Element;
    cancellableToken: CancellableToken;

    constructor(element: Element, parentElement?: Element) {
        this.targetElement = element;
        this.quoteElement = null;
        this.cancellableToken = null;
        this.parentElement = parentElement;
        if (!this.parentElement) {
            this.parentElement = element.closest('[data-topic]');
        }
    }

    attach(): Promise<void> {
        let self = this;

        let target = this.targetElement;
        let boardSlug = target.getAttribute('data-anchor-board');
        let topicId = parseInt(target.getAttribute('data-anchor-topic'), 10);
        let postNumber = target.getAttribute('data-anchor');

        return this.render(boardSlug, topicId, postNumber).then(
            function(node: VNode | void) {
                if (node) {
                    let rebindTopic: boolean;
                    let popoverNode: VNode;
                    let popoverView = new PopoverView(self.targetElement, node);

                    // Rebind [data-topic] when anchor is pointing to post from
                    // another topic so that quick reply binds to correct
                    // context.
                    if (topicId && postNumber) {
                        let localTopicElement = target.closest('[data-topic]');
                        let localTopicId = parseInt(
                            localTopicElement.getAttribute('data-topic'),
                            10
                        );

                        if (topicId != localTopicId) {
                            rebindTopic = true;
                            popoverNode = popoverView.render({
                                dataset: {
                                    topic: topicId,
                                }
                            });
                        }
                    }

                    if (!popoverNode) {
                        rebindTopic = false;
                        popoverNode = popoverView.render();
                    }

                    self.quoteElement = create(popoverNode);
                    self.parentElement.insertBefore(self.quoteElement, null);

                    if (rebindTopic) {
                        new TopicManager(self.parentElement);
                    }
                }
            }
        );
    }

    detach(): void {
        if (this.cancellableToken) {
            this.cancellableToken.cancel();
        }

        if (this.quoteElement) {
            this.parentElement.removeChild(this.quoteElement);
            this.quoteElement = null;
        }
    }

    private render(
        boardSlug: string,
        topicId?: number,
        postNumber?: string,
    ): Promise<VNode | void> {
        this.cancellableToken = new CancelToken();

        if (boardSlug && !topicId && !postNumber) {
            return Board.querySlug(
                boardSlug,
                this.cancellableToken
            ).then(function(board: Board): VNode {
                if (board) {
                    return new BoardView(board).render();
                }
            });
        } else if (topicId && !postNumber) {
            return Topic.queryId(
                topicId,
                this.cancellableToken
            ).then(function(topic: Topic): VNode {
                if (topic) {
                    return new TopicView(topic).render();
                }
            });
        } else if (topicId && postNumber) {
            return Post.queryAll(
                topicId,
                postNumber,
                this.cancellableToken
            ).then(function(posts: Array<Post>) {
                    if (posts && posts.length) {
                        return new PostCollectionView(posts).render();
                    }
                }
            );
        }
    }
}


export class AnchorPopover extends DelegationComponent {
    public targetSelector = '[data-anchor]';

    dismissTimer: number;

    protected bindGlobal(): void {
        let self = this;
        document.body.addEventListener('mouseover', function(e: Event): void {
            let target = <Element>e.target;
            if (target.matches(self.targetSelector)) {
                e.preventDefault();

                let parent = target.closest('.js-popover');
                let handler = new AnchorPopoverHandler(target, parent);

                handler.attach().then(function(): void {
                    let quoteElement = handler.quoteElement;
                    if (quoteElement) {
                        self.bindQuoteElement(handler, quoteElement);
                    }
                });

                target.addEventListener('mouseout',
                    function(e: Event): void {
                        e.preventDefault();

                        // If quoteElement is already rendered then wait and
                        // see if user will move mouse into the quote; otherwise
                        // immediately detach.
                        if (handler.quoteElement) {
                            self.dismissTimer = setTimeout(function(): void {
                                handler.detach();
                            }, 100);
                        } else {
                            handler.detach();
                        }
                    }
                );
            }
        });
    }

    private bindQuoteElement(
        handler: AnchorPopoverHandler,
        quoteElement: Element
    ): void {
        let self = this;
        quoteElement.addEventListener('mouseover',
            function _bindQuote(e: Event): void {
                e.preventDefault();

                if (self.dismissTimer) {
                    clearTimeout(self.dismissTimer);
                    self.dismissTimer = null;
                    self.bindQuoteElementDocument(handler, quoteElement);
                    quoteElement.removeEventListener(
                        'mouseover',
                        <EventListener>_bindQuote
                    );
                }
            }
        );
    }

    private bindQuoteElementDocument(
        handler: AnchorPopoverHandler,
        quoteElement: Element
    ): void {
        let self = this;
        document.body.addEventListener('mouseover',
            function _bindQuoteDocument(e: Event): void {
                e.preventDefault();

                let _n = <Node>e.target;
                while (_n && _n != quoteElement) {
                    _n = _n.parentNode;
                }

                if (_n != quoteElement) {
                    handler.detach();
                    document.body.removeEventListener(
                        'mouseover',
                        <EventListener>_bindQuoteDocument
                    );
                }
            }
        );
    }
}
