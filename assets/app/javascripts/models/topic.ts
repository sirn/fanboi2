/// <reference path="../typings/whatwg-fetch/whatwg-fetch.d.ts" />
/// <reference path="../typings/es6-promise/es6-promise.d.ts" />

import post = require('./post');


enum Statuses {
    Open,
    Locked,
    Archived,
}

export class Topic {
    type: string;
    id: number;
    boardId: number;
    bumpedAt: string;
    createdAt: string;
    postCount: number;
    postedAt: string;
    status: Statuses;
    title: string;
    path: string;

    constructor(data: any) {
        this.type = data.type;
        this.id = data.id;
        this.boardId = data.board_id;
        this.bumpedAt = data.bumped_at;
        this.createdAt = data.created_at;
        this.postCount = data.post_count;
        this.postedAt = data.posted_at;
        this.title = data.title;
        this.path = data.path;

        switch (data.status) {
            case "open" : this.status = Statuses.Open; break;
            case "locked" : this.status = Statuses.Locked; break;
            case "archived" : this.status = Statuses.Archived; break;
        }
    }

    static queryAll(slug: string): Promise<Array<Topic>> {
        return window.fetch(`/api/1.0/boards/${slug}/topics/`).
            then(function(resp: Response): any { return resp.json(); }).
            then(function(topics: any[]): Array<Topic> {
                return topics.map(function(topic: Object) {
                    return new Topic(topic);
                });
            });
    }

    static queryId(id: number): Promise<Topic> {
        return window.fetch(`/api/1.0/topics/${id}/`).
            then(function(resp: Response): any { return resp.json(); }).
            then(function(topic: any) {
                return new Topic(topic);
            });
    }

    getPosts(query?: string): Promise<Array<post.Post>> {
        return post.Post.queryAll(this.id, query);
    }
}
