import { VNode, create, diff, h, patch } from "virtual-dom";

import { SingletonComponent } from "./base";
import { Board } from "../models/board";
import { BoardSelectorView } from "../views/board_selector_view";
import { addClass } from "../utils/elements";

const animationDuration = 200;

export class BoardSelector extends SingletonComponent {
    public targetSelector = "[data-board-selector]";

    protected bindOne($element: Element): void {
        let $button: Element;
        let $selector: Element | undefined;
        let selectorView: BoardSelectorView | undefined;
        let selectorNode: VNode | undefined;
        let selectorState: boolean = false;
        let throttleTimer: number;

        let _render = (height: number = 0): Promise<any> => {
            if (!$selector) {
                return Board.queryAll().then((boards: Board[]) => {
                    selectorView = new BoardSelectorView(boards);
                    selectorNode = selectorView.render();
                    $selector = create(selectorNode);
                    document.body.insertBefore($selector, $element.nextSibling);
                });
            } else {
                return new Promise(resolve => {
                    resolve();
                });
            }
        };

        let _update = (height: number): void => {
            if ($selector && selectorView && selectorNode) {
                let newSelectorNode = selectorView.render({
                    style: {
                        height: `${height}px`,
                    },
                });

                let patches = diff(selectorNode, newSelectorNode);
                $selector = patch($selector, patches);
                selectorNode = newSelectorNode;
            }
        };

        let _animate = (updateFn: ((elapsedPercent: number) => void)) => {
            let startTime: number = 0;
            let _animateStep = (time: number) => {
                if (!startTime) {
                    startTime = time;
                }

                let elapsed = Math.min(time - startTime, animationDuration);
                let elapsedPercent = elapsed / animationDuration;

                updateFn(elapsedPercent);

                if (elapsed < animationDuration) {
                    requestAnimationFrame(_animateStep);
                }
            };

            requestAnimationFrame(_animateStep);
        };

        $button = create(
            h("div", { className: "js-board-selector-button" }, [
                h("a", { href: "#" }, ["Boards"]),
            ]),
        );

        $button.addEventListener("click", e => {
            e.preventDefault();
            _render().then(() => {
                if ($selector) {
                    let selectorHeight = BoardSelector.getSelectorHeight($selector);

                    if (selectorState) {
                        selectorState = false;
                        _animate((elapsedPercent: number) => {
                            _update(selectorHeight * (1 - elapsedPercent));
                        });
                    } else {
                        selectorState = true;
                        _animate((elapsedPercent: number) => {
                            _update(selectorHeight * elapsedPercent);
                        });
                    }
                }
            });
        });

        let $container = $element.querySelector(".container");
        if ($container) {
            $container.appendChild($button);
            addClass($element, ["js-board-selector-wrapper"]);
        }

        // Attempt to restore height on resize. Since the resize may cause
        // clientHeight to change (and will cause the board selector to be
        // clipped or has extra whitespace).
        //
        // Do nothing if resize was called before board selector was attached
        // or if selector was attached but not displayed.
        window.addEventListener("resize", (e: Event) => {
            clearTimeout(throttleTimer);
            throttleTimer = window.setTimeout(() => {
                if ($selector && selectorState) {
                    _update(BoardSelector.getSelectorHeight($selector));
                    selectorState = true;
                }
            }, 100);
        });
    }

    private static getSelectorHeight($selector: Element): number {
        let $el = $selector.querySelector(".js-board-selector-inner");

        if ($el) {
            return $el.clientHeight;
        }

        throw new Error("Could not retrieve board selector height.");
    }
}
