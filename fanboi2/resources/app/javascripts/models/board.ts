/// <reference path="../../../vendor/javascripts/fetch.d.ts" />

import Topic from "./topic";

export default class Board {
    type: string;
    id: number;
    agreements: string;
    description: string;
    settings: {
        postDelay: number;
        useIdent: boolean;
        name: string;
        maxPosts: number;
    };
    slug: string;
    title: string;
    path: string;

    constructor(data: any) {
        this.type = data.type;
        this.id = data.id;
        this.agreements = data.agreements;
        this.description = data.description;
        this.slug = data.slug;
        this.title = data.title;
        this.path = data.path;

        this.settings = {
            postDelay: data.settings.post_delay,
            useIdent: data.settings.use_ident,
            name: data.settings.name,
            maxPosts: data.settings.max_posts,
        };
    }

    static queryAll(): Promise<Iterable<Board>> {
        return window.fetch('/api/1.0/boards/').
            then(function(resp: Response): any { return resp.json(); }).
            then(function*(boards: any[]): Iterable<Board> {
                for (var board of boards) {
                    yield new Board(board);
                }
            });
    }

    static querySlug(slug: string): Promise<Board> {
        return window.fetch(`/api/1.0/boards/${slug}/`).
            then(function(resp: Response): any { return resp.json(); }).
            then(function(board: any): Board {
                return new Board(board)
            });
    }

    getTopics(): Promise<Iterable<Topic>> {
        return Topic.queryAll(this.slug);
    }
}
