import request = require('../utils/request');
import cancellable = require('../utils/cancellable');
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

    static queryAll(
        slug: string,
        token?: cancellable.CancellableToken
    ): Promise<Array<Topic>> {
        return request.request('GET', `/api/1.0/boards/${slug}/topics/`, token).
            then(function(resp: string): Array<Topic> {
                return JSON.parse(resp).map(function(data: Object) {
                    return new Topic(data);
                });
            });
    }

    static queryId(
        id: number,
        token?: cancellable.CancellableToken
    ): Promise<Topic> {
        return request.request('GET', `/api/1.0/topics/${id}/`, token).
            then(function(resp: string) {
                return new Topic(JSON.parse(resp));
            });
    }

    getPosts(
        query?: string,
        token?: cancellable.CancellableToken
    ): Promise<Array<post.Post>> {
        return post.Post.queryAll(this.id, query, token);
    }
}
