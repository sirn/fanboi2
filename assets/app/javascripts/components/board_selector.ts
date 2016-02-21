import vdom = require('virtual-dom');
import board = require('../models/board');


const animationDuration = 200;


class BoardSelectorListView {
    boards: board.Board[];
    boardList: vdom.VNode[];

    constructor(boards: board.Board[]) {
        this.boards = boards;
        this.boardList = this.renderBoards();
    }

    render(args?: any): vdom.VNode {
        return vdom.h('div', BoardSelectorListView.getViewClassName(args), [
            vdom.h('div', {className: 'js-board-selector-list-inner'},
                this.boardList
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

    private static getViewClassName(args?: any): any {
        let className = 'js-board-selector-list';

        if (!args) {
            args = {};
        }

        if (args.className) {
            let classNames = args.className.split(' ');
            classNames.push(className);
            args.className = classNames.join(' ');
        } else {
            args.className = className;
        }

        return args;
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

    listView: BoardSelectorListView;
    listNode: vdom.VNode;
    listElement: Element;
    listHeight: number;
    listState: boolean;

    constructor(targetSelector: string) {
        this.targetElement = document.querySelector(targetSelector);

        let className = this.targetElement.className.split(' ');
        className.push('js-board-selector');
        this.targetElement.className = className.join(' ');

        this.attachButton();
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
                self.attachBoardSelector();
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

    private attachBoardSelector(): void {
        this.listView = new BoardSelectorListView(this.boards);
        this.listNode = this.listView.render();
        this.listElement = vdom.create(this.listNode);

        document.body.insertBefore(
            this.listElement,
            this.targetElement.nextSibling
        )

        let wrapper = '.js-board-selector-list-inner';
        let wrapperElement = this.listElement.querySelector(wrapper);
        this.listHeight = wrapperElement.clientHeight;
    }

    private hideBoardSelector(): void {
        let self = this;
        let startTime: number;

        let animateStep = function(time: number) {
            if (!startTime) {
                startTime = time;
            }

            let elapsed = Math.min(time - startTime, animationDuration);
            let elapsedPercent = elapsed/animationDuration;

            let viewNode = self.listView.render({
                style: {
                    height: `${self.listHeight * (1 - elapsedPercent)}px`,
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
        let startTime: number;

        let animateStep = function(time: number) {
            if (!startTime) {
                startTime = time;
            }

            let elapsed = Math.min(time - startTime, animationDuration);
            let elapsedPercent = elapsed/animationDuration;

            let viewNode = self.listView.render({
                style: {
                    height: `${self.listHeight * elapsedPercent}px`,
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
}
