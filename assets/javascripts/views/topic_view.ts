import { VNode, h } from "virtual-dom";
import { formatDate } from "../utils/formatters";
import { Topic } from "../models/topic";

export class TopicView {
    topicNode: VNode;

    constructor(topic: Topic) {
        this.topicNode = TopicView.renderTopic(topic);
    }

    render(): VNode {
        return this.topicNode;
    }

    private static renderTopic(topic: Topic): VNode {
        return h("div", { className: "js-topic" }, [
            h("div", { className: "topic-header" }, [
                h("div", { className: "container" }, [
                    TopicView.renderTitle(topic),
                    TopicView.renderDate(topic),
                    TopicView.renderCount(topic),
                ]),
            ]),
        ]);
    }

    private static renderTitle(topic: Topic): VNode {
        return h("h3", { className: "topic-header-title" }, [topic.title]);
    }

    private static renderDate(topic: Topic): VNode {
        let postedAt = new Date(topic.postedAt);
        let formatter = formatDate(postedAt);
        return h("p", { className: "topic-header-item" }, [
            "Last posted ",
            h("strong", {}, [formatter]),
        ]);
    }

    private static renderCount(topic: Topic): VNode {
        return h("p", { className: "topic-header-item" }, [
            "Total of ",
            h("strong", {}, [`${topic.postCount} posts`]),
        ]);
    }
}
