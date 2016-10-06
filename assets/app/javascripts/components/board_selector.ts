import {VNode, create, diff, h, patch} from 'virtual-dom';

import {SingletonComponent} from './base';
import {Board} from '../models/board';
import {BoardSelectorView} from '../views/board_selector_view';
import {addClass} from '../utils/elements';


const animationDuration = 200;


export class BoardSelector extends SingletonComponent {
    public targetSelector = '[data-board-selector]';

    boards: Board[];
    targetElement: Element;
    buttonElement: Element;
    selectorView: BoardSelectorView;
    selectorNode: VNode;
    selectorElement: Element;
    selectorHeight: number;
    selectorState: boolean;
    resizeTimer: number;

    protected bindOne(element: Element): void {
        let self = this;
        let buttonNode = h('div',
            {className: 'js-board-selector-button'},
            [h('a', {'href': '#'}, ['Boards'])]
        );

        addClass(element, 'js-board-selector-wrapper');

        this.targetElement = element;
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
        //
        // Do nothing if resize was called before board selector was attached.
        window.addEventListener('resize', function(e: Event) {
            clearTimeout(self.resizeTimer);
            setTimeout(function(){
                if (self.selectorElement) {
                    let selectorHeight = self.getSelectorHeight();
                    if (self.selectorHeight != selectorHeight) {
                        self.selectorHeight = selectorHeight;
                        if (self.selectorState) {
                            self.showBoardSelector(false);
                            this.selectorState = true;
                        }
                    }
                }
            }, 100);
        });
    }

    private eventButtonClicked(): void {
        let self = this;

        if (this.boards) {
            this.toggleBoardSelectorState();
        } else {
            Board.queryAll().then(function(
                boards: Array<Board>
            ): void {
                self.boards = boards;
                self.attachBoardSelector();
                self.toggleBoardSelectorState();
            });
        }
    }

    private toggleBoardSelectorState(): void {
        if (this.selectorState) {
            this.hideBoardSelector(true);
            this.selectorState = false;
        } else {
            this.showBoardSelector(true);
            this.selectorState = true;
        }
    }

    private attachBoardSelector(): void {
        this.selectorView = new BoardSelectorView(this.boards);
        this.selectorNode = this.selectorView.render();
        this.selectorElement = create(this.selectorNode);

        document.body.insertBefore(
            this.selectorElement,
            this.targetElement.nextSibling
        )

        this.selectorHeight = this.getSelectorHeight();
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
                self.updateSelectorElement(
                    self.selectorHeight * (1 - elapsedPercent)
                );

                if (elapsed < animationDuration) {
                    requestAnimationFrame(animateStep);
                }
            }

            requestAnimationFrame(animateStep);
        } else {
            this.updateSelectorElement(0, 'hidden');
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
                self.updateSelectorElement(self.selectorHeight * elapsedPercent);

                if (elapsed < animationDuration) {
                    requestAnimationFrame(animateStep);
                }
            }

            requestAnimationFrame(animateStep);
        } else {
            this.updateSelectorElement(this.selectorHeight);
        }
    }

    private updateSelectorElement(height: number, visibility?: string) {
        if (!visibility) {
            visibility = 'visible';
        }

        let viewNode = this.selectorView.render({
            style: {
                height: `${height}px`,
                visibility: visibility,
            }
        });

        let patches = diff(this.selectorNode, viewNode);
        this.selectorElement = patch(this.selectorElement, patches);
        this.selectorNode = viewNode;
    }

    private getSelectorHeight(): number {
        return this.selectorElement.querySelector(
            '.js-board-selector-inner'
        ).clientHeight;
    }
}
