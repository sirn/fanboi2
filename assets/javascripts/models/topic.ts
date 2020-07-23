import { Model, IModelData } from "./base";
import { Post } from "./post";
import { CancellableToken } from "../utils/cancellable";
import { request } from "../utils/request";

enum Statuses {
    Open,
    Locked,
    Archived,
}

export class Topic extends Model {
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

    serialize(data: IModelData) {
        Model.assertType(data, "topic");

        this.type = data["type"];
        this.id = data["id"];
        this.boardId = data["board_id"];
        this.bumpedAt = data["bumped_at"];
        this.createdAt = data["created_at"];
        this.postCount = data["post_count"];
        this.postedAt = data["posted_at"];
        this.title = data["title"];
        this.path = data["path"];

        switch (data["status"]) {
            case "open":
                this.status = Statuses.Open;
                break;
            case "locked":
                this.status = Statuses.Locked;
                break;
            case "archived":
                this.status = Statuses.Archived;
                break;
        }
    }

    static queryAll(slug: string, token?: CancellableToken): Promise<Topic[]> {
        return request("GET", `/api/1.0/boards/${slug}/topics/`, {}, token).then(
            (resp: string): Topic[] => {
                return JSON.parse(resp).map((data: Object) => {
                    return new Topic(data);
                });
            },
        );
    }

    static queryId(id: number, token?: CancellableToken): Promise<Topic> {
        return request("GET", `/api/1.0/topics/${id}/`, {}, token).then(
            (resp: string) => {
                return new Topic(JSON.parse(resp));
            },
        );
    }

    getPosts(query?: string, token?: CancellableToken): Promise<Post[]> {
        return Post.queryAll(this.id, query, token);
    }
}
