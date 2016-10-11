import {NotImplementedError} from '../utils/errors';


export interface IComponent {
    targetSelector: string;
}


export class DelegationComponent implements IComponent {
    public targetSelector: string;

    constructor() {
        let self = this;
        setTimeout(function(): void {
            self.bindGlobal();
        }, 1);
    }

    protected bindGlobal(): void {
        throw new NotImplementedError;
    }
}


export class SingletonComponent implements IComponent {
    public targetSelector: string;

    constructor(context?: Element | Document) {
        let self = this;

        if (context == null) {
            context = document;
        }

        setTimeout(function(): void {
            let targetElement = context.querySelector(self.targetSelector);
            if (targetElement) {
                self.bindOne(targetElement);
            }
        }, 1);
    }

    protected bindOne(element: Element): void {
        throw new NotImplementedError;
    }
}


export class CollectionComponent implements IComponent {
    public targetSelector: string;

    constructor(context?: Element | Document) {
        let self = this;

        if (context == null) {
            context = document;
        }

        setTimeout(function(): void {
            let targetElements = context.querySelectorAll(self.targetSelector);
            self.bindAll(targetElements);
        }, 1);
    }

    protected bindAll(targetElements: NodeListOf<Element>): void {
        for (let i = 0, len = targetElements.length; i < len; i++) {
            this.bindOne(targetElements[i]);
        }
    }

    protected bindOne(element: Element): void {
        throw new NotImplementedError;
    }
}
