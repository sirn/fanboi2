import { VNode, h } from "virtual-dom";
import { Board } from "../models/board";
import { BoardView } from "./board_view";

export class BoardSelectorView {
    boardListNode: VNode[];

    constructor(boards: Board[]) {
        this.boardListNode = BoardSelectorView.renderBoards(boards);
    }

    render(args: any = {}): VNode {
        return h("div", BoardSelectorView.getViewClassName(args), [
            h("div", { className: "js-board-selector-inner" }, this.boardListNode),
        ]);
    }

    private static renderBoards(boards: Board[]): VNode[] {
        return boards.map((board: Board): VNode => {
            return new BoardView(board).render();
        });
    }

    private static getViewClassName(args: any): any {
        const className = "js-board-selector";

        if (args.className) {
            let classNames = args.className.split(" ");
            classNames.push(className);
            args.className = classNames.join(" ");
        } else {
            args.className = className;
        }

        return args;
    }
}
