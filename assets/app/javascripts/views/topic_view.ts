import { VNode, h } from "virtual-dom";
import { formatDate } from "../utils/formatters";
import { mergeClasses } from "../utils/template";
import { Topic } from "../models/topic";

export class TopicView {
    topic: Topic;

    constructor(topic: Topic) {
        this.topic = topic;
    }

    render(args: any = {}): VNode {
        let panelArgs = args.panel || { className: "panel--shade1" };
        let containerArgs = args.container || { className: "u-pd-vertical-m" };
        let titleArgs = args.title || {};
        let bodyArgs = args.body || { className: "u-txt-s u-txt-gray4" };

        return h("div", mergeClasses(panelArgs, ["panel"]), [
            h("div", mergeClasses(containerArgs, ["container"]), [
                h("h3", mergeClasses(titleArgs, ["panel__item"]), [this.topic.title]),
                h("div", mergeClasses(bodyArgs, ["panel__item"]), [
                    h("ul", { className: "list" }, [
                        h("li", { className: "list__item" }, [
                            "Last posted ",
                            h("strong", {}, [
                                formatDate(new Date(this.topic.postedAt)),
                            ]),
                        ]),
                        h("li", { className: "list__item" }, [
                            "Total of ",
                            h("strong", {}, [`${this.topic.postCount} posts`]),
                        ]),
                    ]),
                ]),
            ]),
        ]);
    }
}
