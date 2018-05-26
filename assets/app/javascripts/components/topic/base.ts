export interface ITopicEventConstructor {
    new (topicId: number, element: Element): ITopicEventHandler;
}

export interface ITopicEventHandler {
    topicId: number;
    element: Element;
    bind(event: CustomEvent): void;
}
