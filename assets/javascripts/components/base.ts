import { NotImplementedError } from "../utils/errors";

export interface IComponent {
    targetSelector: string;
}

export class DelegationComponent implements IComponent {
    public targetSelector: string;

    constructor() {
        window.setTimeout((): void => {
            this.bindGlobal();
        }, 1);
    }

    protected bindGlobal(): void {
        throw new NotImplementedError();
    }
}

export class SingletonComponent implements IComponent {
    public targetSelector: string;

    constructor($context?: Element | Document) {
        if (!$context) {
            $context = document;
        }

        window.setTimeout((): void => {
            if ($context) {
                let $element = $context.querySelector(this.targetSelector);
                if ($element) {
                    this.bindOne($element);
                }
            }
        }, 1);
    }

    protected bindOne($element: Element): void {
        throw new NotImplementedError();
    }
}

export class CollectionComponent implements IComponent {
    public targetSelector: string;

    constructor($context?: Element | Document) {
        if (!$context) {
            $context = document;
        }

        window.setTimeout((): void => {
            if ($context) {
                let $elements = $context.querySelectorAll(this.targetSelector);
                this.bindAll($elements);
            }
        }, 1);
    }

    protected bindAll($targets: NodeListOf<Element>): void {
        for (let i = 0, len = $targets.length; i < len; i++) {
            this.bindOne($targets[i]);
        }
    }

    protected bindOne($target: Element): void {
        throw new NotImplementedError();
    }
}
