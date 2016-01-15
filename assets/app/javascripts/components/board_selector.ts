/// <reference path="../typings/virtual-dom/virtual-dom.d.ts" />
/// <reference path="../typings/es6-promise/es6-promise.d.ts" />

import vdom = require('virtual-dom');
import board = require('../models/board');


class BoardSelectorListView {
    boards: board.Board[];
    show: boolean;

    constructor(boards: board.Board[], show?: boolean) {
        this.boards = boards;
        this.show = !!show;
    }

    render(): vdom.VNode {
        return vdom.h('div',
            {className: this.getCssFromState()},
            this.boards.map(function(board: board.Board): vdom.VNode {
                return vdom.h('div', {className: 'cascade'}, [
                    vdom.h('div', {className: 'container'}, [
                        vdom.h('div', {className: 'cascade-header'}, [
                            vdom.h('a',
                                {href: `/${board.slug}/`},
                                String(board.title)
                            ),
                        ]),
                        vdom.h('div',
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


export class BoardSelector {
    targetElement: Element;
    buttonNode: vdom.VNode;
    buttonElement: Element;
    listNode: vdom.VNode;
    listElement: Element;
    boards: board.Board[];

    constructor(targetSelector: string) {
        this.targetElement = document.querySelector(targetSelector);

        let className = this.targetElement.className.split(' ');
        className.push('js-board-selector');
        this.targetElement.className = className.join(' ');

        this.attachList();
        this.attachButton();
    }

    private attachList(): void {
        let view = new BoardSelectorListView([]);
        this.listNode = view.render();
        this.listElement = vdom.create(this.listNode);

        document.body.insertBefore(
            this.listElement,
            this.targetElement.nextSibling
        )
    }

    private attachButton(): void {
        let self = this;
        this.buttonNode = vdom.h('div',
            {className: 'js-board-selector-button'},
            [vdom.h('a', {'href': '#'}, ['Boards'])]
        );

        this.buttonElement = vdom.create(this.buttonNode);
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
            board.Board.queryAll().then(function(
                boards: Array<board.Board>
            ): void {
                self.boards = boards;
                self.toggleBoardSelectorListState();
            });
        }
    }

    private toggleBoardSelectorListState(): void {
        let state = this.listElement.className.indexOf('disabled') != -1;
        let view = new BoardSelectorListView(this.boards, state);
        let viewNode = view.render();
        let patches = vdom.diff(this.listNode, viewNode);

        this.listElement = vdom.patch(this.listElement, patches);
        this.listNode = viewNode;
    }
}
