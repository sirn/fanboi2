import {VNode, create, diff, patch, h} from 'virtual-dom';
import {SingletonComponent} from './base';
import {Board} from '../models/board';


const animationDuration = 200;


class BoardSelectorListView {
    boards: Board[];
    boardList: VNode[];

    constructor(boards: Board[]) {
        this.boards = boards;
        this.boardList = this.renderBoards();
    }

    render(args?: any): VNode {
        return h('div', BoardSelectorListView.getViewClassName(args), [
            h('div', {className: 'js-board-selector-list-inner'},
                this.boardList
            )
        ]);
    }

    private renderBoards(): VNode[] {
        return this.boards.map(function(board: Board): VNode {
            return h('div', {className: 'cascade'}, [
                h('div', {className: 'container'}, [
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

    private static renderHeader(board: Board): VNode {
        return h('div', {className: 'cascade-header'}, [
            h('a', {href: `/${board.slug}/`}, [String(board.title)]),
        ]);
    }

    private static renderBody(board: Board): VNode {
        return h('div', {className: 'cascade-body'}, [
            String(board.description)
        ]);
    }
}


export class BoardSelector extends SingletonComponent {
    boards: Board[];

    buttonElement: Element;

    listView: BoardSelectorListView;
    listNode: VNode;
    listElement: Element;
    listHeight: number;
    listState: boolean;

    protected bindOne(element: Element): void {
        let self = this;
        let className = element.className.split(' ');

        className.push('js-board-selector');
        element.className = className.join(' ');

        let buttonNode = h('div',
            {className: 'js-board-selector-button'},
            [h('a', {'href': '#'}, ['Boards'])]
        );

        this.buttonElement = create(buttonNode);
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
            Board.queryAll().then(function(
                boards: Array<Board>
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
        this.listElement = create(this.listNode);

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

            let patches = diff(self.listNode, viewNode);
            self.listElement = patch(self.listElement, patches);
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

            let patches = diff(self.listNode, viewNode);
            self.listElement = patch(self.listElement, patches);
            self.listNode = viewNode;

            if (elapsed < animationDuration) {
                requestAnimationFrame(animateStep);
            }
        }

        requestAnimationFrame(animateStep);
    }
}
