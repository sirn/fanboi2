/// <reference path="../typings/dom4/dom4.d.ts" />

import Board from '../models/board';
import Topic from '../models/topic';
import Post from '../models/post';

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
            this.renderTopicPost(topicId, number);
        }
    }

    private renderBoard(boardSlug: string): void {
        Board.querySlug(boardSlug).then(function(board: Board) {
            console.log(board);
        });
    }

    private renderTopic(topicId: number): void {
        Topic.queryId(topicId).then(function(topic: Topic) {
            console.log(topic);
        });
    }

    private renderTopicPost(topicId: number, query: string): void {
        Post.queryAll(topicId, query).then(function(posts: Iterable<Post>) {
            console.log(Array.from(posts));
        });
    }
}