/// <reference path="../typings/virtual-dom/virtual-dom.d.ts" />

import * as VirtualDOM from 'virtual-dom';
import Board from "../models/board";

var h = VirtualDOM.h;
var createElement = VirtualDOM.create;

class BoardSelectorButton {
    label: string;

    constructor(label: string) {
        this.label = label;
    }

    render(): VirtualDOM.VNode {
        return h('div', {className: 'js-board-selector-button'}, [
            h('a', {href: '#'}, [this.label]),
        ])
    }
}

class BoardSelectorList {
    boards: Board[];
    show: boolean;

    constructor(boards: Board[], show?: boolean) {
        this.boards = boards;
        this.show = !!show;
    }

    render(): VirtualDOM.VNode {
        return h('div',
            {className: this.getCssFromState()},
            this.renderList()
        )
    }

    private getCssFromState(): string {
        return [
            'js-board-selector-list',
            this.show ? 'enabled' : 'disabled'
        ].join(' ');
    }

    private renderList(): VirtualDOM.VNode[] {
        return this.boards.map(function (board:Board):VirtualDOM.VNode {
            return h('div', {className: 'cascade'}, [
                h('div', {className: 'container'}, [
                    h('div', {className: 'cascade-header'}, [
                        h('a', {href: `/${board.slug}/`}, String(board.title))
                    ]),
                    h('div', {className: 'cascade-body'},
                        String(board.description)
                    ),
                ]),
            ])
        });
    }
}

export default class BoardSelector {
    targetElement: Element;
    buttonNode: VirtualDOM.VNode;
    buttonElement: Element;
    listNode: VirtualDOM.VNode;
    listElement: Element;
    boards: Board[];

    constructor(targetElement: string) {
        this.targetElement = document.querySelector(targetElement);

        let className = this.targetElement.className.split(' ');
        className.push('js-board-selector');
        this.targetElement.className = className.join(' ');

        this.attachList();
        this.attachButton();
    }

    private attachList(): void {
        let view = new BoardSelectorList([]);
        this.listNode = view.render();
        this.listElement = createElement(this.listNode);
        document.body.insertBefore(
            this.listElement,
            this.targetElement.nextSibling
        )
    }

    private attachButton(): void {
        let view = new BoardSelectorButton('Boards');
        this.buttonNode = view.render();
        this.buttonElement = createElement(this.buttonNode);

        let containerElement = this.targetElement.querySelector('.container');
        containerElement.appendChild(this.buttonElement);

        let self = this;
        self.buttonElement.addEventListener('click', function(e: Event): void {
            e.preventDefault();
            self.eventButtonClicked();
        });
    }

    private eventButtonClicked(): void {
        let self = this;

        if (this.boards) {
            this.toggleBoardSelectorListState();
        } else {
            Board.queryAll().then(function (boards: Iterable<Board>): void {
                self.boards = Array.from(boards);
                self.toggleBoardSelectorListState();
            });
        }
    }

    private toggleBoardSelectorListState(): void {
        let state = this.listElement.className.includes('disabled');
        let view = new BoardSelectorList(Array.from(this.boards), state);
        let viewNode = view.render();
        let patches = VirtualDOM.diff(this.listNode, viewNode);

        this.listElement = VirtualDOM.patch(this.listElement, patches);
        this.listNode = viewNode;
    }
}