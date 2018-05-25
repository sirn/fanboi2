import { Model, IModelData } from "./base";
import { Topic } from "./topic";
import { CancellableToken } from "../utils/cancellable";
import { request } from "../utils/request";

export class Board extends Model {
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

    protected serialize(data: IModelData) {
        Model.assertType(data, "board");

        this.type = data["type"];
        this.id = data["id"];
        this.agreements = data["agreements"];
        this.description = data["description"];
        this.slug = data["slug"];
        this.title = data["title"];
        this.path = data["path"];

        this.settings = {
            postDelay: data["settings"]["post_delay"],
            useIdent: data["settings"]["use_ident"],
            name: data["settings"]["name"],
            maxPosts: data["settings"]["max_posts"],
        };
    }

    static queryAll(token?: CancellableToken): Promise<Board[]> {
        return request("GET", "/api/1.0/boards/", {}, token).then(
            (resp: string): Board[] => {
                return JSON.parse(resp).map((data: Object) => {
                    return new Board(data);
                });
            },
        );
    }

    static querySlug(slug: string, token?: CancellableToken): Promise<Board> {
        return request("GET", `/api/1.0/boards/${slug}/`, {}, token).then(
            (resp: string): Board => {
                return new Board(JSON.parse(resp));
            },
        );
    }

    getTopics(token?: CancellableToken): Promise<Topic[]> {
        return Topic.queryAll(this.slug, token);
    }
}
