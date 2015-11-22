interface Element {
    query(relativeSelectors: string): Element;
    queryAll(relativeSelectors: string): Array<Element>;

    prepend(nodes: Node | string | Array<Node | string>): void;
    append(nodes: Node | string | Array<Node | string>): void;

    before(nodes: Node | string | Array<Node | string>): void;
    after(nodes: Node | string | Array<Node | string>): void;
    replaceWith(nodes: Node | string | Array<Node | string>): void;
    remove(): void;

    matches(selector: string): boolean;
    closest(selector: string): Element;
}

interface Document {
    query(relativeSelectors: string): Element;
    queryAll(relativeSelectors: string): Array<Element>;
}