/// <reference path="../typings/whatwg-fetch/whatwg-fetch.d.ts" />

import 'whatwg-fetch'
import Post from "./post";

enum Statuses {
    Open,
    Locked,
    Archived,
}

export default class Topic {
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

    static queryAll(slug: string): Promise<Iterable<Topic>> {
        return window.fetch(`/api/1.0/boards/${slug}/topics/`).
            then(function(resp: Response): any { return resp.json(); }).
            then(function*(topics: any[]): Iterable<Topic> {
                for (var topic of topics) {
                    yield new Topic(topic);
                }
            });
    }

    static queryId(id: number): Promise<Topic> {
        return window.fetch(`/api/1.0/topics/${id}/`).
            then(function(resp: Response): any { return resp.json(); }).
            then(function(topic: any) {
                return new Topic(topic);
            });
    }

    getPosts(query?: string): Promise<Iterable<Post>> {
        return Post.queryAll(this.id, query);
    }
}