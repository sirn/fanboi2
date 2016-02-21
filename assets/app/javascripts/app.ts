import domready = require('domready');
import boardSelector = require('./components/board_selector');
import inlineQuote = require('./components/inline_quote');

domready(function(): void {
    new boardSelector.BoardSelector('.header');
    new inlineQuote.InlineQuote('[data-number]');
});
