/// <reference path="../typings/dom4/dom4.d.ts" />

import * as VirtualDOM from 'virtual-dom';

import DateFormatter from '../utils/date_formatter';
import Board from '../models/board';
import Topic from '../models/topic';
import Post from '../models/post';


class InlineBoardView {
    board: Board;

    constructor(board: Board) {
        this.board = board;
    }

    render(): VirtualDOM.VNode {
        return VirtualDOM.h('div',
            {className: 'js-inline-board'},
            [
                VirtualDOM.h('div', {className: 'cascade'}, [
                    VirtualDOM.h('div', {className: 'container'}, [
                        InlineBoardView.renderTitle(this.board),
                        InlineBoardView.renderDescription(this.board),
                    ])
                ])
            ]
        )
    }

    private static renderTitle(board: Board): VirtualDOM.VNode {
        return VirtualDOM.h('div', {className: 'cascade-header'}, [
            String(board.title)
        ])
    }

    private static renderDescription(board: Board): VirtualDOM.VNode {
        return VirtualDOM.h('div', {className: 'cascade-body'}, [
            String(board.description)
        ])
    }
}


class InlineTopicView {
    topic: Topic;

    constructor(topic: Topic) {
        this.topic = topic;
    }

    render(): VirtualDOM.VNode {
        return VirtualDOM.h('div',
            {className: 'js-inline-topic'},
            [
                VirtualDOM.h('div', {className: 'topic-header'}, [
                    VirtualDOM.h('div', {className: 'container'}, [
                        InlineTopicView.renderTitle(this.topic),
                        InlineTopicView.renderDate(this.topic),
                        InlineTopicView.renderCount(this.topic),
                    ])
                ])
            ]
        )
    }

    private static renderTitle(topic: Topic): VirtualDOM.VNode {
        return VirtualDOM.h('h3', {className: 'topic-header-title'}, [
            String(topic.title)
        ]);
    }

    private static renderDate(topic: Topic): VirtualDOM.VNode {
        let postedAt = new Date(topic.postedAt);
        let dateFormatter = new DateFormatter(postedAt);
        return VirtualDOM.h('p', {className: 'topic-header-item'}, [
            String('Last posted '),
            VirtualDOM.h('strong', {}, [String(dateFormatter)]),
        ]);
    }

    private static renderCount(topic: Topic): VirtualDOM.VNode {
        return VirtualDOM.h('p', {className: 'topic-header-item'}, [
            String('Total of '),
            VirtualDOM.h('strong', {}, [String(`${topic.postCount} posts`)]),
        ]);
    }
}


class InlinePostsView {
    posts: Post[];

    constructor(posts: Post[]) {
        this.posts = posts;
    }

    render(): VirtualDOM.VNode {
        return VirtualDOM.h('div',
            {className: 'js-inline-post'},
            this.posts.map(function(post: Post): VirtualDOM.VNode {
                return InlinePostsView.renderPost(post);
            })
        )
    }

    private static renderPost(post: Post): VirtualDOM.VNode {
        return VirtualDOM.h('div', {className: 'container'}, [
            InlinePostsView.renderHeader(post),
            InlinePostsView.renderBody(post),
        ]);
    }

    private static renderHeader(post: Post): VirtualDOM.VNode {
        return VirtualDOM.h('div', {className: 'post-header'}, [
            InlinePostsView.renderHeaderNumber(post),
            InlinePostsView.renderHeaderName(post),
            InlinePostsView.renderHeaderDate(post),
            InlinePostsView.renderHeaderIdent(post),
        ]);
    }

    private static renderHeaderNumber(post: Post): VirtualDOM.VNode {
        let classList = ['post-header-item', 'number'];
        if (post.bumped) { classList.push('bumped'); }
        return VirtualDOM.h('span', {
            className: classList.join(' '),
        }, [String(post.number)]);
    }

    private static renderHeaderName(post: Post): VirtualDOM.VNode {
        return VirtualDOM.h('span', {
            className: 'post-header-item name'
        }, [String(post.name)]);
    }

    private static renderHeaderDate(post: Post): VirtualDOM.VNode {
        let createdAt = new Date(post.createdAt);
        let dateFormatter = new DateFormatter(createdAt);
        return VirtualDOM.h('span', {
            className: 'post-header-item date'
        }, [String(`Posted ${dateFormatter}`)]);
    }

    private static renderHeaderIdent(post: Post): (VirtualDOM.VNode | string) {
        if (post.ident) {
            return VirtualDOM.h('span', {
                className: 'post-header-item ident'
            }, [String(`ID:${post.ident}`)]);
        } else {
            return String(null);
        }
    }

    private static renderBody(post: Post): VirtualDOM.VNode {
        return VirtualDOM.h('div', {
            className: 'post-body',
            innerHTML: post.bodyFormatted,
        }, []);
    }
}


export default class InlineQuote {
    targetSelector: string;

    constructor(targetSelector: string) {
        this.targetSelector = targetSelector;
        this.attachSelf();
    }

    private attachSelf(): void {
        let self = this;

        document.addEventListener('mouseover', function(e: Event): void {
            if ((<Element>e.target).matches(self.targetSelector)) {
                e.preventDefault();
                self.eventQuoteMouseOver(<Element>e.target);
            }
        });
    }

    private eventQuoteMouseOver(element: Element): void {
        let boardSlug = element.getAttribute('data-board');
        let topicId = parseInt(element.getAttribute('data-topic'), 10);
        let number = element.getAttribute('data-number');

        if (boardSlug && !topicId && !number) {
            this.renderBoard(boardSlug);
        } else if (topicId && !number) {
            this.renderTopic(topicId);
        } else if (topicId && number) {
            this.renderTopicPosts(topicId, number);
        }
    }

    private renderBoard(boardSlug: string): void {
        Board.querySlug(boardSlug).then(function(board: Board) {
            let view = new InlineBoardView(board);
            let node = view.render();
            let element = VirtualDOM.create(node);
            console.log(node);
            console.log(element);
        });
    }

    private renderTopic(topicId: number): void {
        Topic.queryId(topicId).then(function(topic: Topic) {
            let view = new InlineTopicView(topic);
            let node = view.render();
            let element = VirtualDOM.create(node);
            console.log(node);
            console.log(element);
        });
    }

    private renderTopicPosts(topicId: number, query: string): void {
        Post.queryAll(topicId, query).then(function(posts: Iterable<Post>) {
            let view = new InlinePostsView(Array.from(posts));
            let node = view.render();
            let element = VirtualDOM.create(node);
            console.log(node);
            console.log(element);
        });
    }
}