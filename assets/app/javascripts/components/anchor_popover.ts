import {VNode, create, diff, patch} from 'virtual-dom';
import {DelegationComponent} from './base';
import {CancellableToken, CancelToken} from '../utils/cancellable';

import {BoardView} from '../views/board_view';
import {TopicView} from '../views/topic_view';
import {PostCollectionView} from '../views/post_collection_view';
import {PopoverView} from '../views/popover_view';

import {Board} from '../models/board';
import {Topic} from '../models/topic';
import {Post} from '../models/post';


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
            this.parentElement = document.body;
        }
    }

    attach(): Promise<void> {
        let self = this;
        return this.render().then(function(node: VNode | void) {
            if (node) {
                let quoteNode = new PopoverView(
                    self.targetElement,
                    <VNode>node
                ).render();

                self.quoteElement = create(quoteNode);
                self.parentElement.insertBefore(self.quoteElement, null);
            }
        });
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

    private render(): Promise<VNode | void> {
        let target = this.targetElement;
        let boardSlug = target.getAttribute('data-anchor-board');
        let topicId = parseInt(target.getAttribute('data-anchor-topic'), 10);
        let postNumber = target.getAttribute('data-anchor');

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
    dismissTimer: number;

    protected bindGlobal(): void {
        let self = this;
        document.addEventListener('mouseover', function(e: Event): void {
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
        document.addEventListener('mouseover',
            function _bindQuoteDocument(e: Event): void {
                e.preventDefault();

                let _n = <Node>e.target;
                while (_n && _n != quoteElement) {
                    _n = _n.parentNode;
                }

                if (_n != quoteElement) {
                    handler.detach();
                    document.removeEventListener(
                        'mouseover',
                        <EventListener>_bindQuoteDocument
                    );
                }
            }
        );
    }
}
