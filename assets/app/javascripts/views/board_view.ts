import {VNode, h} from 'virtual-dom';
import {Board} from '../models/board';


export class BoardView {
    board: Board;

    constructor(board: Board) {
        this.board = board;
    }

    render(): VNode {
        return h('div',
            {className: 'js-board'},
            [
                h('div', {className: 'cascade'}, [
                    h('div', {className: 'container'}, [
                        BoardView.renderTitle(this.board),
                        BoardView.renderDescription(this.board),
                    ])
                ])
            ]
        );
    }

    private static renderTitle(board: Board): VNode {
        return h('div', {className: 'cascade-header'}, [
            h('a', {
                className: 'cascade-header-link',
                href: `/${board.slug}/`
            }, String(board.title))
        ]);
    }

    private static renderDescription(board: Board): VNode {
        return h('div', {className: 'cascade-body'}, [
            String(board.description)
        ]);
    }
}
