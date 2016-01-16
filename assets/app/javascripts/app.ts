/// <reference path="typings/domready/domready.d.ts" />
/// <reference path="typings/whatwg-fetch/whatwg-fetch.d.ts" />

import 'whatwg-fetch';

import domready = require('domready');
import boardSelector = require('./components/board_selector');
import inlineQuote = require('./components/inline_quote');


domready(function(): void {
    new boardSelector.BoardSelector('.header');
    new inlineQuote.InlineQuote('[data-number]');
});
