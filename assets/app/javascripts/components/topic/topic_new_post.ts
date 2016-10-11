import {ITopicEventHandler} from './base';
import {Post} from '../../models/post';
import {dispatchCustomEvent} from '../../utils/elements';
import {ResourceError} from '../../utils/errors';
import {LoadingState} from '../../utils/loading';


export class TopicNewPost implements ITopicEventHandler {
    loadingState: LoadingState;

    constructor(public topicId: number, public element: Element) {
        this.loadingState = new LoadingState();
    }

    bind(e: CustomEvent): void {
        let self = this;
        let params: any = e.detail.params;
        let callback: ((lastPostNumber: number) => void) = e.detail.callback;
        let errCb: ((error: ResourceError) => void) = e.detail.errorCallback;

        if (!params) { throw new Error('newPost require a params'); }

        this.loadingState.bind(null, function() {
            return Post.createOne(self.topicId, params).then(function(){
                dispatchCustomEvent(self.element, 'postCreated');
                dispatchCustomEvent(self.element, 'loadPosts', {
                    callback: function(lastPostNumber: number) {
                        if (callback) {
                            callback(lastPostNumber);
                        }
                    }
                });
            }).catch(function(error: ResourceError) {
                if (errCb) {
                    errCb(error);
                    dispatchCustomEvent(self.element, 'postCreateError', {
                        error: error
                    });
                }
            });
        });
    }
}
