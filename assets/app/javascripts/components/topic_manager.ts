import {VNode, create, diff, patch} from 'virtual-dom';
import {CollectionComponent} from './base';
import {ITopicEventConstructor, ITopicEventHandler} from './topic/base';
import {TopicState} from './topic/topic_state';
import {TopicLoadPosts} from './topic/topic_load_posts';
import {TopicNewPost} from './topic/topic_new_post';


export class TopicManager extends CollectionComponent {
    public targetSelector = '[data-topic]';

    topicId: number;

    protected bindOne(element: Element): void {
        this.topicId = parseInt(element.getAttribute('data-topic'), 10);
        this.bindEvent(element, 'updateState', TopicState);
        this.bindEvent(element, 'readState',   TopicState);
        this.bindEvent(element, 'loadPosts',   TopicLoadPosts);
        this.bindEvent(element, 'newPost',     TopicNewPost);
    }

    private bindEvent(
        element: Element,
        eventName: string,
        eventHandler: ITopicEventConstructor
    ): void {
        let self = this;
        let handler = new eventHandler(this.topicId, element);
        element.addEventListener(eventName, function(e: CustomEvent) {
            handler.bind(e);
        });
    }
}
