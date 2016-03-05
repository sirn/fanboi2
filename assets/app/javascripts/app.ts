import domready = require('domready');
import boardSelector = require('./components/board_selector');
import anchorPopover = require('./components/anchor_popover');

domready(function(): void {
    new boardSelector.BoardSelector('.header');
    new anchorPopover.AnchorPopover('[data-anchor]');
});
