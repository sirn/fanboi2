import { VNode, h } from "virtual-dom";
import { Board } from "../models/board";

export class BoardView {
    boardNode: VNode;

    constructor(board: Board) {
        this.boardNode = BoardView.renderBoard(board);
    }

    render(): VNode {
        return this.boardNode;
    }

    private static renderBoard(board: Board): VNode {
        return h("div", { className: "js-board" }, [
            h("div", { className: "cascade" }, [
                h("div", { className: "container" }, [
                    BoardView.renderTitle(board),
                    BoardView.renderDescription(board),
                ]),
            ]),
        ]);
    }

    private static renderTitle(board: Board): VNode {
        return h("div", { className: "cascade-header" }, [
            h(
                "a",
                {
                    className: "cascade-header-link",
                    href: `/${board.slug}/`,
                },
                [board.title],
            ),
        ]);
    }

    private static renderDescription(board: Board): VNode {
        return h("div", { className: "cascade-body" }, [board.description]);
    }
}
