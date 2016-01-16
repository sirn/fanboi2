/// <reference path="../typings/virtual-dom/virtual-dom.d.ts" />
/// <reference path="../typings/es6-promise/es6-promise.d.ts" />
/// <reference path="../typings/lodash.merge/lodash.merge.d.ts" />

import vdom = require('virtual-dom');
import board = require('../models/board');
import merge = require('lodash.merge');


const animationDuration = 200;


class BoardSelectorListView {
    boards: board.Board[];

    constructor(boards: board.Board[]) {
        this.boards = boards;
    }

    render(args?: any): vdom.VNode {
        return vdom.h('div', BoardSelectorListView.getViewClassName(args), [
            vdom.h('div', {className: 'js-board-selector-list-inner'},
                this.renderBoards()
            )
        ]);
    }

    private renderBoards(): vdom.VNode[] {
        return this.boards.map(function(board: board.Board): vdom.VNode {
            return vdom.h('div', {className: 'cascade'}, [
                vdom.h('div', {className: 'container'}, [
                    BoardSelectorListView.renderHeader(board),
                    BoardSelectorListView.renderBody(board),
                ]),
            ]);
        })
    }

    private static getViewClassName(args?: any) {
        return merge({className: 'js-board-selector-list'}, args);
    }

    private static renderHeader(board: board.Board): vdom.VNode {
        return vdom.h('div', {className: 'cascade-header'}, [
            vdom.h('a', {href: `/${board.slug}/`}, [String(board.title)]),
        ]);
    }

    private static renderBody(board: board.Board): vdom.VNode {
        return vdom.h('div', {className: 'cascade-body'}, [
            String(board.description)
        ]);
    }
}


export class BoardSelector {
    boards: board.Board[];

    targetElement: Element;
    buttonNode: vdom.VNode;
    buttonElement: Element;

    listNode: vdom.VNode;
    listElement: Element;
    listState: boolean;

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
        if (this.listState) {
            this.hideBoardSelector();
            this.listState = false;
        } else {
            this.showBoardSelector();
            this.listState = true;
        }
    }

    private hideBoardSelector(): void {
        let self = this;
        let view = new BoardSelectorListView(this.boards);
        let maxHeight = this.computeBoardSelectorHeight();
        let startTime: number;

        let animateStep = function(time: number) {
            if (!startTime) {
                startTime = time;
            }

            let elapsed = Math.min(time - startTime, animationDuration);
            let elapsedPercent = elapsed/animationDuration;

            let viewNode = view.render({
                style: {
                    height: `${maxHeight * (1 - elapsedPercent)}px`,
                    visibility: 'visible',
                }
            });

            let patches = vdom.diff(self.listNode, viewNode);
            self.listElement = vdom.patch(self.listElement, patches);
            self.listNode = viewNode;

            if (elapsed < animationDuration) {
                requestAnimationFrame(animateStep);
            }
        }

        requestAnimationFrame(animateStep);
    }

    private showBoardSelector(): void {
        let self = this;
        let view = new BoardSelectorListView(this.boards);

        // Need to re-render to compute actual height.
        this.renderBoardSelector(view);
        let maxHeight = this.computeBoardSelectorHeight();
        let startTime: number;

        let animateStep = function(time: number) {
            if (!startTime) {
                startTime = time;
            }

            let elapsed = Math.min(time - startTime, animationDuration);
            let elapsedPercent = elapsed/animationDuration;

            let viewNode = view.render({
                style: {
                    height: `${maxHeight * elapsedPercent}px`,
                    visibility: 'visible',
                }
            });

            let patches = vdom.diff(self.listNode, viewNode);
            self.listElement = vdom.patch(self.listElement, patches);
            self.listNode = viewNode;

            if (elapsed < animationDuration) {
                requestAnimationFrame(animateStep);
            }
        }

        requestAnimationFrame(animateStep);
    }

    private renderBoardSelector(view: BoardSelectorListView): void {
        let viewNode = view.render();
        let patches = vdom.diff(this.listNode, viewNode);

        this.listElement = vdom.patch(this.listElement, patches);
        this.listNode = viewNode;
    }

    private computeBoardSelectorHeight(): number {
        let wrapper = '.js-board-selector-list-inner';
        let wrapperElement = this.listElement.querySelector(wrapper);
        return wrapperElement.clientHeight;
    }
}
