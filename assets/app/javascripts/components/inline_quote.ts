import vdom = require('virtual-dom');
import dateFormatter = require('../utils/date_formatter');
import cancellable = require('../utils/cancellable');

import board = require('../models/board');
import topic = require('../models/topic');
import post = require('../models/post');


class InlineBoardView {
    board: board.Board;

    constructor(board: board.Board) {
        this.board = board;
    }

    render(): vdom.VNode {
        return vdom.h('div',
            {className: 'js-inline-board'},
            [
                vdom.h('div', {className: 'cascade'}, [
                    vdom.h('div', {className: 'container'}, [
                        InlineBoardView.renderTitle(this.board),
                        InlineBoardView.renderDescription(this.board),
                    ])
                ])
            ]
        );
    }

    private static renderTitle(board: board.Board): vdom.VNode {
        return vdom.h('div', {className: 'cascade-header'}, [
            vdom.h('a', {
                className: 'cascade-header-link',
                href: `/${board.slug}/`
            }, String(board.title))
        ]);
    }

    private static renderDescription(board: board.Board): vdom.VNode {
        return vdom.h('div', {className: 'cascade-body'}, [
            String(board.description)
        ]);
    }
}


class InlineTopicView {
    topic: topic.Topic;

    constructor(topic: topic.Topic) {
        this.topic = topic;
    }

    render(): vdom.VNode {
        return vdom.h('div',
            {className: 'js-inline-topic'},
            [
                vdom.h('div', {className: 'topic-header'}, [
                    vdom.h('div', {className: 'container'}, [
                        InlineTopicView.renderTitle(this.topic),
                        InlineTopicView.renderDate(this.topic),
                        InlineTopicView.renderCount(this.topic),
                    ])
                ])
            ]
        );
    }

    private static renderTitle(topic: topic.Topic): vdom.VNode {
        return vdom.h('h3', {className: 'topic-header-title'}, [
            String(topic.title)
        ]);
    }

    private static renderDate(topic: topic.Topic): vdom.VNode {
        let postedAt = new Date(topic.postedAt);
        let formatter = dateFormatter.formatDate(postedAt);
        return vdom.h('p', {className: 'topic-header-item'}, [
            String('Last posted '),
            vdom.h('strong', {}, [String(formatter)]),
        ]);
    }

    private static renderCount(topic: topic.Topic): vdom.VNode {
        return vdom.h('p', {className: 'topic-header-item'}, [
            String('Total of '),
            vdom.h('strong', {}, [String(`${topic.postCount} posts`)]),
        ]);
    }
}


class InlinePostsView {
    posts: post.Post[];

    constructor(posts: post.Post[]) {
        this.posts = posts;
    }

    render(): vdom.VNode {
        return vdom.h('div',
            {className: 'js-inline-post'},
            this.posts.map(function(post: post.Post): vdom.VNode {
                return InlinePostsView.renderPost(post);
            })
        );
    }

    private static renderPost(post: post.Post): vdom.VNode {
        return vdom.h('div', {className: 'post'}, [
            vdom.h('div', {className: 'container'}, [
                InlinePostsView.renderHeader(post),
                InlinePostsView.renderBody(post),
            ])
        ]);
    }

    private static renderHeader(post: post.Post): vdom.VNode {
        return vdom.h('div', {className: 'post-header'}, [
            InlinePostsView.renderHeaderNumber(post),
            InlinePostsView.renderHeaderName(post),
            InlinePostsView.renderHeaderDate(post),
            InlinePostsView.renderHeaderIdent(post),
        ]);
    }

    private static renderHeaderNumber(post: post.Post): vdom.VNode {
        let classList = ['post-header-item', 'number'];
        if (post.bumped) { classList.push('bumped'); }
        return vdom.h('span', {
            className: classList.join(' '),
        }, [String(post.number)]);
    }

    private static renderHeaderName(post: post.Post): vdom.VNode {
        return vdom.h('span', {
            className: 'post-header-item name'
        }, [String(post.name)]);
    }

    private static renderHeaderDate(post: post.Post): vdom.VNode {
        let createdAt = new Date(post.createdAt);
        let formatter = dateFormatter.formatDate(createdAt);
        return vdom.h('span', {
            className: 'post-header-item date'
        }, [String(`Posted ${formatter}`)]);
    }

    private static renderHeaderIdent(post: post.Post): vdom.VNode | string {
        if (post.ident) {
            return vdom.h('span', {
                className: 'post-header-item ident'
            }, [String(`ID:${post.ident}`)]);
        } else {
            return String(null);
        }
    }

    private static renderBody(post: post.Post): vdom.VNode {
        return vdom.h('div', {
            className: 'post-body',
            innerHTML: post.bodyFormatted,
        }, []);
    }
}


class InlineQuoteView {
    childNode: vdom.VNode;
    targetElement: Element;

    constructor(targetElement: Element, childNode: vdom.VNode) {
        this.targetElement = targetElement;
        this.childNode = childNode;
    }

    render(): vdom.VNode {
        let pos = this.computePosition();
        return vdom.h('div', {className: 'js-inline'}, [
            vdom.h('div', {
                className: 'js-inline-inner',
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


class InlineQuoteHandler {
    targetElement: Element;
    quoteElement: Element;
    parentElement: Element;
    cancellableToken: cancellable.CancellableToken;

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
        return this.render().then(function(node: vdom.VNode | void) {
            if (node) {
                let quoteNode = new InlineQuoteView(
                    self.targetElement,
                    <vdom.VNode>node
                ).render();

                self.quoteElement = vdom.create(quoteNode);
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

    private render(): Promise<vdom.VNode | void> {
        let targetElement = this.targetElement;
        let boardSlug = targetElement.getAttribute('data-board');
        let topicId = parseInt(targetElement.getAttribute('data-topic'), 10);
        let number = targetElement.getAttribute('data-number');

        this.cancellableToken = new cancellable.CancelToken();

        if (boardSlug && !topicId && !number) {
            return board.Board.querySlug(
                boardSlug,
                this.cancellableToken
            ).then(function(board: board.Board): vdom.VNode {
                if (board) {
                    return new InlineBoardView(board).render();
                }
            });
        } else if (topicId && !number) {
            return topic.Topic.queryId(
                topicId,
                this.cancellableToken
            ).then(function(topic: topic.Topic): vdom.VNode {
                if (topic) {
                    return new InlineTopicView(topic).render();
                }
            });
        } else if (topicId && number) {
            return post.Post.queryAll(
                topicId,
                number,
                this.cancellableToken
            ).then(function(posts: Array<post.Post>) {
                    if (posts && posts.length) {
                        return new InlinePostsView(posts).render();
                    }
                }
            );
        }
    }
}


export class InlineQuote {
    targetSelector: string;
    dismissTimer: number;

    constructor(targetSelector: string) {
        this.targetSelector = targetSelector;
        this.dismissTimer = null;
        this.bindGlobal();
    }

    private bindGlobal(): void {
        let self = this;
        document.addEventListener('mouseover', function(e: Event): void {
            let target = <Element>e.target;
            if (target.matches(self.targetSelector)) {
                e.preventDefault();

                let parent = target.closest('.js-inline');
                let handler = new InlineQuoteHandler(target, parent);

                handler.attach().then(function(): void {
                    let quoteElement = handler.quoteElement;
                    self.bindQuoteElement(handler, handler.quoteElement);
                });

                target.addEventListener('mouseout',
                    function(e: Event): void {
                        e.preventDefault();

                        self.dismissTimer = setTimeout(function(): void {
                            handler.detach();
                        }, 100);
                    }
                );
            }
        });
    }

    private bindQuoteElement(
        handler: InlineQuoteHandler,
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
        handler: InlineQuoteHandler,
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
