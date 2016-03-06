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

        // Attempt to restore height on resize. Since the resize may cause
        // clientHeight to change (and will cause the board selector to be
        // clipped or has extra whitespace).
        window.addEventListener('resize', function(e: Event) {
            let listHeight = self.getListHeight();
            if (self.listHeight != listHeight) {
                self.listHeight = listHeight;
                if (self.listState) {
                    self.showBoardSelector(false);
                    this.listState = true;
                }
            }
        });
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
            this.hideBoardSelector(true);
            this.listState = false;
        } else {
            this.showBoardSelector(true);
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

        this.listHeight = this.getListHeight();
    }

    private hideBoardSelector(animate?: boolean): void {
        let self = this;

        if (animate) {
            let startTime: number;
            let animateStep = function(time: number) {
                if (!startTime) {
                    startTime = time;
                }

                let elapsed = Math.min(time - startTime, animationDuration);
                let elapsedPercent = elapsed/animationDuration;
                self.updateListElement(self.listHeight * (1 - elapsedPercent));

                if (elapsed < animationDuration) {
                    requestAnimationFrame(animateStep);
                }
            }

            requestAnimationFrame(animateStep);
        } else {
            this.updateListElement(0, 'hidden');
        }
    }

    private showBoardSelector(animate?: boolean): void {
        let self = this;

        if (animate) {
            let startTime: number;
            let animateStep = function(time: number) {
                if (!startTime) {
                    startTime = time;
                }

                let elapsed = Math.min(time - startTime, animationDuration);
                let elapsedPercent = elapsed/animationDuration;
                self.updateListElement(self.listHeight * elapsedPercent);

                if (elapsed < animationDuration) {
                    requestAnimationFrame(animateStep);
                }
            }

            requestAnimationFrame(animateStep);
        } else {
            this.updateListElement(this.listHeight);
        }
    }

    private updateListElement(height: number, visibility?: string) {
        if (!visibility) {
            visibility = 'visible';
        }

        let viewNode = this.listView.render({
            style: {
                height: `${height}px`,
                visibility: visibility,
            }
        });

        let patches = diff(this.listNode, viewNode);
        this.listElement = patch(this.listElement, patches);
        this.listNode = viewNode;
    }

    private getListHeight(): number {
        return this.listElement.querySelector(
            '.js-board-selector-list-inner'
        ).clientHeight;
    }
}
