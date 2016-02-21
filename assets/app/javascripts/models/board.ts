import request = require('../utils/request');
import cancellable = require('../utils/cancellable');
import topic = require('./topic');

export class Board {
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

    static queryAll(
        token?: cancellable.CancellableToken
    ): Promise<Array<Board>> {
        return request.request('GET', '/api/1.0/boards/', token).
            then(function(resp: string): Array<Board> {
                return JSON.parse(resp).map(function(data: Object) {
                    return new Board(data);
                });
            });
    }

    static querySlug(
        slug: string,
        token?: cancellable.CancellableToken
    ): Promise<Board> {
        return request.request('GET', `/api/1.0/boards/${slug}/`, token).
            then(function(resp: string): Board {
                return new Board(JSON.parse(resp));
            });
    }

    getTopics(
        token?: cancellable.CancellableToken
    ): Promise<Array<topic.Topic>> {
        return topic.Topic.queryAll(this.slug, token);
    }
}
