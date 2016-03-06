import {request} from '../utils/request';
import {Model, IModelData} from './base';
import {CancellableToken} from '../utils/cancellable';


export class Post extends Model {
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

    serialize(data: IModelData) {
        Model.assertType(data, 'post');

        this.type = data['type'];
        this.id = data['id'];
        this.body = data['body'];
        this.bodyFormatted = data['body_formatted'];
        this.bumped = data['bumped'];
        this.createdAt = data['created_at'];
        this.ident = data['ident'];
        this.name = data['name'];
        this.number = data['number'];
        this.topicId = data['topic_id'];
        this.path = data['path'];
    }

    static queryAll(
        topicId: number,
        query?: string,
        token?: CancellableToken
    ): Promise<Post[]> {
        let entryPoint: string;

        if (query) {
            entryPoint = `/api/1.0/topics/${topicId}/posts/${query}/`;
        } else {
            entryPoint = `/api/1.0/topics/${topicId}/posts/`;
        }

        return request('GET', entryPoint, token).then(function(resp) {
            return JSON.parse(resp).map(function(data: Object): Post {
                return new Post(data);
            });
        });
    }
}
