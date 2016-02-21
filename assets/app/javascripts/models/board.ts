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

    static queryAll(): Promise<Array<Board>> {
        return window.fetch('/api/1.0/boards/').
            then(function(resp: Response): any { return resp.json(); }).
            then(function(boards: any[]): Array<Board> {
                return boards.map(function(board: Object) {
                    return new Board(board);
                });
            });
    }

    static querySlug(slug: string): Promise<Board> {
        return window.fetch(`/api/1.0/boards/${slug}/`).
            then(function(resp: Response): any { return resp.json(); }).
            then(function(board: any): Board {
                return new Board(board);
            });
    }

    getTopics(): Promise<Array<topic.Topic>> {
        return topic.Topic.queryAll(this.slug);
    }
}
