import { Model, IModelData } from "./base";
import { Task } from "./task";
import { CancellableToken } from "../utils/cancellable";
import { request, IRequestBody } from "../utils/request";

export class Post extends Model {
    type: string;
    id: number;
    body: string;
    bodyFormatted: string;
    bumped: boolean;
    createdAt: string;
    ident: string;
    identType: string;
    name: string;
    number: number;
    topicId: number;
    path: string;

    serialize(data: IModelData) {
        Model.assertType(data, "post");

        this.type = data["type"];
        this.id = data["id"];
        this.body = data["body"];
        this.bodyFormatted = data["body_formatted"];
        this.bumped = data["bumped"];
        this.createdAt = data["created_at"];
        this.ident = data["ident"];
        this.identType = data["ident_type"];
        this.name = data["name"];
        this.number = data["number"];
        this.topicId = data["topic_id"];
        this.path = data["path"];
    }

    static queryAll(
        topicId: number,
        query?: string,
        token?: CancellableToken
    ): Promise<Post[]> {
        let entryPoint = `/api/1.0/topics/${topicId}/posts/`;

        if (query) {
            entryPoint = `${entryPoint}${query}/`;
        }

        return request("GET", entryPoint, {}, token).then(resp => {
            return JSON.parse(resp).map(
                (data: Object): Post => {
                    return new Post(data);
                }
            );
        });
    }

    static createOne(
        topicId: number,
        params: IRequestBody,
        token?: CancellableToken
    ): Promise<Post> {
        return request("POST", `/api/1.0/topics/${topicId}/posts/`, params, token).then(
            (resp: string) => {
                let data: IModelData = JSON.parse(resp);

                if (data["type"] == "task") {
                    return Task.waitFor(data["id"], token).then((task: Task) => {
                        return new Post(task.data);
                    });
                } else {
                    return new Post(data);
                }
            }
        );
    }
}
