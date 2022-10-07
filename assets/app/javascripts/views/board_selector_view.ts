import isEqual = require("lodash.isequal");
import { h, VNode } from "virtual-dom";
import { Board } from "../models/board";
import { BoardView } from "./board_view";

export class BoardSelectorView {
    boards: Board[];

    // Cache
    boardListNode: VNode[];
    boardArgs: any = {};

    constructor(boards: Board[]) {
        this.boards = boards;
    }

    render(args: any = {}): VNode {
        let wrapperArgs = args.wrapper || {};
        let boardArgs = args.board || {};

        if (!wrapperArgs.style) {
            wrapperArgs.style = { height: "0px" };
        }

        if (!this.boardListNode || !isEqual(this.boardArgs, boardArgs)) {
            this.boardArgs = boardArgs;
            this.boardListNode = this.boards.map((board: Board): VNode => {
                return new BoardView(board).render(boardArgs);
            });
        }

        wrapperArgs.style.overflow = "hidden";
        return h("div", wrapperArgs, [
            h("div", { dataset: { boardSelectorInner: true } }, this.boardListNode),
        ]);
    }
}
