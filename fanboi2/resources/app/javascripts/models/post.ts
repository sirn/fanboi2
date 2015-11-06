/// <reference path="../../../vendor/javascripts/fetch.d.ts" />

export default class Post {
    type: string;
    id: number;
    body: string;
    bodyFormatted: string;
    bumped: boolean;
    createdAt: string;
    ident: string;
    name: string;
    number: number;
    topicId: number;
    path: string;

    constructor(data: any) {
        this.type = data.type;
        this.id = data.id;
        this.body = data.body;
        this.bodyFormatted = data.body_formatted;
        this.bumped = data.bumped;
        this.createdAt = data.created_at;
        this.ident = data.ident;
        this.name = data.name;
        this.number = data.number;
        this.topicId = data.topic_id;
        this.path = data.path;
    }

    static queryAll(
        topicId: number,
        query?: string
    ): Promise<Iterable<Post>> {
        var entryPoint: string;

        if (query) {
            entryPoint = `/api/1.0/topics/${topicId}/posts/${query}/`
        } else {
            entryPoint = `/api/1.0/topics/${topicId}/posts/`;
        }

        return window.fetch(entryPoint).
            then(function(resp: Response): any { return resp.json(); }).
            then(function*(posts: any[]): Iterable<Post> {
                for (var post of posts) {
                    yield new Post(post);
                }
            });
    }
}