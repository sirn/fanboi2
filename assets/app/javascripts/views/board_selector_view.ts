import {VNode, h} from 'virtual-dom';
import {Board} from '../models/board';
import {BoardView} from './board_view';


export class BoardSelectorView {
    boards: Board[];
    boardList: VNode[];

    constructor(boards: Board[]) {
        this.boards = boards;
        this.boardList = this.renderBoards();
    }

    render(args?: any): VNode {
        return h('div', BoardSelectorView.getViewClassName(args), [
            h('div', {className: 'js-board-selector-inner'},
                this.boardList
            )
        ]);
    }

    private renderBoards(): VNode[] {
        return this.boards.map(function(board: Board): VNode {
            return new BoardView(board).render();
        })
    }

    private static getViewClassName(args?: any): any {
        let className = 'js-board-selector';

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
}
