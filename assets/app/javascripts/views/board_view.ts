import { h, VNode } from "virtual-dom";
import { Board } from "../models/board";
import { mergeClasses } from "../utils/template";

export class BoardView {
    board: Board;

    constructor(board: Board) {
        this.board = board;
    }

    render(args: any = {}): VNode {
        let panelArgs = args.panel || {};
        let containerArgs = args.container || { className: "u-pd-vertical-l" };

        return h(
            "div",
            mergeClasses(panelArgs, ["panel", "panel--separator", "panel--unit-link"]),
            [
                h("div", mergeClasses(containerArgs, ["container"]), [
                    h("h3", { className: "panel__item" }, [
                        h(
                            "a",
                            {
                                className: "panel__link",
                                href: `/${this.board.slug}/`,
                            },
                            [this.board.title]
                        ),
                    ]),
                    h("div", { className: "panel__item u-txt-s u-txt-gray4" }, [
                        this.board.description,
                    ]),
                ]),
            ]
        );
    }
}
