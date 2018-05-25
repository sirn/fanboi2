import { VNode, create, diff, patch } from "virtual-dom";
import { CollectionComponent } from "./base";
import { ITopicEventConstructor, ITopicEventHandler } from "./topic/base";
import { TopicState } from "./topic/topic_state";
import { TopicLoadPosts } from "./topic/topic_load_posts";
import { TopicNewPost } from "./topic/topic_new_post";

export class TopicManager extends CollectionComponent {
    public targetSelector = "[data-topic]";

    protected bindOne($target: Element): void {
        let topicIdAttr = $target.getAttribute("data-topic");

        if (topicIdAttr) {
            let topicId = parseInt(topicIdAttr, 10);

            this.bindEvent($target, topicId, "updateState", TopicState);
            this.bindEvent($target, topicId, "readState", TopicState);
            this.bindEvent($target, topicId, "loadPosts", TopicLoadPosts);
            this.bindEvent($target, topicId, "newPost", TopicNewPost);
        }
    }

    private bindEvent(
        $target: Element,
        topicId: number,
        eventName: string,
        eventHandler: ITopicEventConstructor,
    ): void {
        let handler = new eventHandler(topicId, $target);

        $target.addEventListener(eventName, (e: CustomEvent) => {
            e.stopPropagation();
            handler.bind(e);
        });
    }
}
