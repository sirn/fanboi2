/// <reference path="typings/node/node.d.ts" />
/// <reference path="typings/domready/domready.d.ts" />

import 'babel-polyfill';
import 'dom4';

import BoardSelector from './components/board_selector';

require('domready')(function(): void {
    new BoardSelector(".header");
});
