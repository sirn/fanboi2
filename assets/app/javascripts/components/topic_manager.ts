import {VNode, create, diff, patch} from 'virtual-dom';
import {CollectionComponent} from './base';
import {ITopicEventConstructor, ITopicEventHandler} from './topic/base';
import {TopicState} from './topic/topic_state';
import {TopicLoadPosts} from './topic/topic_load_posts';
import {TopicNewPost} from './topic/topic_new_post';


export class TopicManager extends CollectionComponent {
    public targetSelector = '[data-topic]';

    protected bindOne(element: Element): void {
        let topicId = parseInt(element.getAttribute('data-topic'), 10);
        this.bindEvent(topicId, element, 'updateState', TopicState);
        this.bindEvent(topicId, element, 'readState',   TopicState);
        this.bindEvent(topicId, element, 'loadPosts',   TopicLoadPosts);
        this.bindEvent(topicId, element, 'newPost',     TopicNewPost);
    }

    private bindEvent(
        topicId: number,
        element: Element,
        eventName: string,
        eventHandler: ITopicEventConstructor
    ): void {
        let self = this;
        let handler = new eventHandler(topicId, element);
        element.addEventListener(eventName, function(e: CustomEvent) {
            e.stopPropagation();
            handler.bind(e);
        });
    }
}
