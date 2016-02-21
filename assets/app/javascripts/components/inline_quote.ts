import vdom = require('virtual-dom');
import dateFormatter = require('../utils/date_formatter');
import elementId = require('../utils/element_id');

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
            String(board.title)
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
        return vdom.h('div', {className: 'container'}, [
            InlinePostsView.renderHeader(post),
            InlinePostsView.renderBody(post),
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
        return vdom.h('div', {
            className: 'js-inline',
            style: {
                position: 'absolute',
                top: `${pos.posX}px`,
                left: `${pos.posY}px`,
            }
        }, [this.childNode]);
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

    constructor(element: Element) {
        this.targetElement = element;
        this.parentElement = document.body;
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

        if (boardSlug && !topicId && !number) {
            return board.Board.querySlug(boardSlug).then(function(
                board: board.Board
            ): vdom.VNode {
                if (board) {
                    return new InlineBoardView(board).render();
                }
            });
        } else if (topicId && !number) {
            return topic.Topic.queryId(topicId).then(function(
                topic: topic.Topic
            ): vdom.VNode {
                if (topic) {
                    return new InlineTopicView(topic).render();
                }
            });
        } else if (topicId && number) {
            return post.Post.queryAll(topicId, number).then(
                function(posts: Array<post.Post>) {
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
    store: {[key: string]: InlineQuoteHandler}

    constructor(targetSelector: string) {
        this.targetSelector = targetSelector;
        this.store = {};
        this.attachSelf();
    }

    private attachSelf(): void {
        let self = this;

        document.addEventListener('mouseover', function(e: Event): void {
            if ((<Element>e.target).matches(self.targetSelector)) {
                e.preventDefault();
                let eid = elementId.getElementId(<Element>e.target);
                if (!self.store[eid]) {
                    let handler = new InlineQuoteHandler(<Element>e.target);
                    handler.attach().then(function(): void {
                        self.store[eid] = handler;
                    });
                }
            }
        });

        document.addEventListener('mouseout', function(e: Event): void {
            if ((<Element>e.target).matches(self.targetSelector)) {
                e.preventDefault();
                let eid = elementId.getElementId(<Element>e.target);
                if (self.store[eid]) {
                    self.store[eid].detach();
                    delete self.store[eid];
                }
            }
        });
    }
}
