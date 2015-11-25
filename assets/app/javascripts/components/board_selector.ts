/// <reference path="../typings/virtual-dom/virtual-dom.d.ts" />

import * as VirtualDOM from 'virtual-dom';
import Board from "../models/board";

class BoardSelectorList {
    boards: Board[];
    show: boolean;

    constructor(boards: Board[], show?: boolean) {
        this.boards = boards;
        this.show = !!show;
    }

    render(): VirtualDOM.VNode {
        return VirtualDOM.h('div',
            {className: this.getCssFromState()},
            this.boards.map(function(board: Board): VirtualDOM.VNode {
                return VirtualDOM.h('div', {className: 'cascade'}, [
                    VirtualDOM.h('div', {className: 'container'}, [
                        VirtualDOM.h('div', {className: 'cascade-header'}, [
                            VirtualDOM.h('a',
                                {href: `/${board.slug}/`},
                                String(board.title)
                            ),
                        ]),
                        VirtualDOM.h('div',
                            {className: 'cascade-body'},
                            String(board.description)
                        ),
                    ]),
                ])
            })
        )
    }

    private getCssFromState(): string {
        return [
            'js-board-selector-list',
            this.show ? 'enabled' : 'disabled'
        ].join(' ');
    }
}

export default class BoardSelector {
    targetElement: Element;
    buttonNode: VirtualDOM.VNode;
    buttonElement: Element;
    listNode: VirtualDOM.VNode;
    listElement: Element;
    boards: Board[];

    constructor(targetSelector: string) {
        this.targetElement = document.querySelector(targetSelector);

        let className = this.targetElement.className.split(' ');
        className.push('js-board-selector');
        this.targetElement.className = className.join(' ');

        this.attachList();
        this.attachButton();
    }

    private attachList(): void {
        let view = new BoardSelectorList([]);
        this.listNode = view.render();
        this.listElement = VirtualDOM.create(this.listNode);

        document.body.insertBefore(
            this.listElement,
            this.targetElement.nextSibling
        )
    }

    private attachButton(): void {
        let self = this;
        this.buttonNode = VirtualDOM.h('div',
            {className: 'js-board-selector-button'},
            [VirtualDOM.h('a', {'href': '#'}, ['Boards'])]
        );

        this.buttonElement = VirtualDOM.create(this.buttonNode);
        this.buttonElement.addEventListener('click', function(e) {
            e.preventDefault();
            self.eventButtonClicked();
        });

        let containerElement = this.targetElement.querySelector('.container');
        containerElement.appendChild(this.buttonElement);
    }

    private eventButtonClicked(): void {
        let self = this;

        if (this.boards) {
            this.toggleBoardSelectorListState();
        } else {
            Board.queryAll().then(function(boards: Iterable<Board>): void {
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