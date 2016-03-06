import {VNode, create, diff, patch, h} from 'virtual-dom';
import {DelegationComponent} from './base';
import {formatDate} from '../utils/date_formatter';
import {CancellableToken, CancelToken} from '../utils/cancellable';

import {Board} from '../models/board';
import {Topic} from '../models/topic';
import {Post} from '../models/post';


class BoardPopoverView {
    board: Board;

    constructor(board: Board) {
        this.board = board;
    }

    render(): VNode {
        return h('div',
            {className: 'js-anchor-popover-board'},
            [
                h('div', {className: 'cascade'}, [
                    h('div', {className: 'container'}, [
                        BoardPopoverView.renderTitle(this.board),
                        BoardPopoverView.renderDescription(this.board),
                    ])
                ])
            ]
        );
    }

    private static renderTitle(board: Board): VNode {
        return h('div', {className: 'cascade-header'}, [
            h('a', {
                className: 'cascade-header-link',
                href: `/${board.slug}/`
            }, String(board.title))
        ]);
    }

    private static renderDescription(board: Board): VNode {
        return h('div', {className: 'cascade-body'}, [
            String(board.description)
        ]);
    }
}


class TopicPopoverView {
    topic: Topic;

    constructor(topic: Topic) {
        this.topic = topic;
    }

    render(): VNode {
        return h('div',
            {className: 'js-anchor-popover-topic'},
            [
                h('div', {className: 'topic-header'}, [
                    h('div', {className: 'container'}, [
                        TopicPopoverView.renderTitle(this.topic),
                        TopicPopoverView.renderDate(this.topic),
                        TopicPopoverView.renderCount(this.topic),
                    ])
                ])
            ]
        );
    }

    private static renderTitle(topic: Topic): VNode {
        return h('h3', {className: 'topic-header-title'}, [
            String(topic.title)
        ]);
    }

    private static renderDate(topic: Topic): VNode {
        let postedAt = new Date(topic.postedAt);
        let formatter = formatDate(postedAt);
        return h('p', {className: 'topic-header-item'}, [
            String('Last posted '),
            h('strong', {}, [String(formatter)]),
        ]);
    }

    private static renderCount(topic: Topic): VNode {
        return h('p', {className: 'topic-header-item'}, [
            String('Total of '),
            h('strong', {}, [String(`${topic.postCount} posts`)]),
        ]);
    }
}


class PostPopoverView {
    posts: Post[];

    constructor(posts: Post[]) {
        this.posts = posts;
    }

    render(): VNode {
        return h('div',
            {className: 'js-anchor-popover-post'},
            this.posts.map(function(post: Post): VNode {
                return PostPopoverView.renderPost(post);
            })
        );
    }

    private static renderPost(post: Post): VNode {
        return h('div', {className: 'post'}, [
            h('div', {className: 'container'}, [
                PostPopoverView.renderHeader(post),
                PostPopoverView.renderBody(post),
            ])
        ]);
    }

    private static renderHeader(post: Post): VNode {
        return h('div', {className: 'post-header'}, [
            PostPopoverView.renderHeaderNumber(post),
            PostPopoverView.renderHeaderName(post),
            PostPopoverView.renderHeaderDate(post),
            PostPopoverView.renderHeaderIdent(post),
        ]);
    }

    private static renderHeaderNumber(post: Post): VNode {
        let classList = ['post-header-item', 'number'];
        if (post.bumped) { classList.push('bumped'); }
        return h('span', {
            className: classList.join(' '),
        }, [String(post.number)]);
    }

    private static renderHeaderName(post: Post): VNode {
        return h('span', {
            className: 'post-header-item name'
        }, [String(post.name)]);
    }

    private static renderHeaderDate(post: Post): VNode {
        let createdAt = new Date(post.createdAt);
        let formatter = formatDate(createdAt);
        return h('span', {
            className: 'post-header-item date'
        }, [String(`Posted ${formatter}`)]);
    }

    private static renderHeaderIdent(post: Post): VNode | string {
        if (post.ident) {
            return h('span', {
                className: 'post-header-item ident'
            }, [String(`ID:${post.ident}`)]);
        } else {
            return String(null);
        }
    }

    private static renderBody(post: Post): VNode {
        return h('div', {
            className: 'post-body',
            innerHTML: post.bodyFormatted,
        }, []);
    }
}


class AnchorPopoverView {
    childNode: VNode;
    targetElement: Element;

    constructor(targetElement: Element, childNode: VNode) {
        this.targetElement = targetElement;
        this.childNode = childNode;
    }

    render(): VNode {
        let pos = this.computePosition();
        return h('div', {className: 'js-anchor-popover'}, [
            h('div', {
                className: 'js-anchor-popover-inner',
                style: {
                    position: 'absolute',
                    top: `${pos.posX}px`,
                    left: `${pos.posY}px`,
                }
            }, [this.childNode])
        ]);
    }

    private computePosition(): {posX: number, posY: number} {
        let bodyRect = document.body.getBoundingClientRect();
        let elemRect = this.targetElement.getBoundingClientRect();
        let yRefRect = elemRect;

        // Indent relative to container rather than element if there is
        // container in element ancestor.
        let containerElement = this.targetElement.closest('.container');
        if (containerElement) {
            yRefRect = containerElement.getBoundingClientRect();
        }

        return {
            posX: (elemRect.bottom + 5) - bodyRect.top,
            posY: yRefRect.left - bodyRect.left,
        }
    }
}


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
                let quoteNode = new AnchorPopoverView(
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
                    return new BoardPopoverView(board).render();
                }
            });
        } else if (topicId && !postNumber) {
            return Topic.queryId(
                topicId,
                this.cancellableToken
            ).then(function(topic: Topic): VNode {
                if (topic) {
                    return new TopicPopoverView(topic).render();
                }
            });
        } else if (topicId && postNumber) {
            return Post.queryAll(
                topicId,
                postNumber,
                this.cancellableToken
            ).then(function(posts: Array<Post>) {
                    if (posts && posts.length) {
                        return new PostPopoverView(posts).render();
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

                let parent = target.closest('.js-anchor-popover');
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
        quoteElement.addEventListener('mouseover', function(e: Event): void {
            e.preventDefault();

            if (self.dismissTimer) {
                clearTimeout(self.dismissTimer);
                self.dismissTimer = null;
                self.bindQuoteElementDocument(handler, quoteElement);
                quoteElement.removeEventListener(
                    'mouseover',
                    <EventListener>arguments.callee
                );
            }
        });
    }

    private bindQuoteElementDocument(
        handler: AnchorPopoverHandler,
        quoteElement: Element
    ): void {
        let self = this;
        document.addEventListener('mouseover', function(e: Event): void {
            e.preventDefault();

            let _n = <Node>e.target;
            while (_n && _n != quoteElement) {
                _n = _n.parentNode;
            }

            if (_n != quoteElement) {
                handler.detach();
                document.removeEventListener(
                    'mouseover',
                    <EventListener>arguments.callee
                );
            }
        });
    }
}
