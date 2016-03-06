import domready = require('domready');
import {BoardSelector} from './components/board_selector';
import {AnchorPopover} from './components/anchor_popover';


domready(function(): void {
    new BoardSelector('[data-board-selector]');
    new AnchorPopover('[data-anchor]');
});
