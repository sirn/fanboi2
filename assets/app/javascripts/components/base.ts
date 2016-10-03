import {NotImplementedError} from '../utils/errors';


export interface IComponent {
    targetSelector: string;
}


export class DelegationComponent implements IComponent {
    constructor(public targetSelector: string) {
        this.bindGlobal();
    }

    protected bindGlobal(): void {
        throw new NotImplementedError;
    }
}


export class SingletonComponent implements IComponent {
    targetElement: Element;

    constructor(public targetSelector: string) {
        this.targetElement = document.querySelector(targetSelector);
        if (this.targetElement) {
            this.bindOne(this.targetElement);
        }
    }

    protected bindOne(element: Element): void {
        throw new NotImplementedError;
    }
}


export class CollectionComponent implements IComponent {
    targetElements: NodeListOf<Element>;

    constructor(public targetSelector: string) {
        this.targetElements = document.querySelectorAll(targetSelector);
        this.bindAll();
    }

    protected bindAll(): void {
        for (let i = 0, len = this.targetElements.length; i < len; i++) {
            this.bindOne(this.targetElements[i]);
        }
    }

    protected bindOne(element: Element): void {
        throw new NotImplementedError;
    }
}
