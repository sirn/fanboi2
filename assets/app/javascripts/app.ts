import domready = require('domready');
import {BoardSelector} from './components/board_selector';
import {ThemeSelector} from './components/theme_selector';
import {AnchorPopover} from './components/anchor_popover';


domready(function(): void {
    new BoardSelector('[data-board-selector]');
    new ThemeSelector('[data-theme-selector]');
    new AnchorPopover('[data-anchor]');
});
