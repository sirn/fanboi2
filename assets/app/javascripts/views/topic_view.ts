import {VNode, h} from 'virtual-dom';
import {formatDate} from '../utils/date_formatter';
import {Topic} from '../models/topic';


export class TopicView {
    topic: Topic;

    constructor(topic: Topic) {
        this.topic = topic;
    }

    render(): VNode {
        return h('div',
            {className: 'js-topic'},
            [
                h('div', {className: 'topic-header'}, [
                    h('div', {className: 'container'}, [
                        TopicView.renderTitle(this.topic),
                        TopicView.renderDate(this.topic),
                        TopicView.renderCount(this.topic),
                    ])
                ])
            ]
        );
    }

    private static renderTitle(topic: Topic): VNode {
        return h('h3', {className: 'topic-header-title'}, [
            String(topic.title)
        ]);
    }

    private static renderDate(topic: Topic): VNode {
        let postedAt = new Date(topic.postedAt);
        let formatter = formatDate(postedAt);
        return h('p', {className: 'topic-header-item'}, [
            String('Last posted '),
            h('strong', {}, [String(formatter)]),
        ]);
    }

    private static renderCount(topic: Topic): VNode {
        return h('p', {className: 'topic-header-item'}, [
            String('Total of '),
            h('strong', {}, [String(`${topic.postCount} posts`)]),
        ]);
    }
}
