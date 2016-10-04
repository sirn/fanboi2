import domready = require('domready');
import {BoardSelector} from './components/board_selector';
import {ThemeSelector} from './components/theme_selector';
import {TopicReloader} from './components/topic_reloader';
import {AnchorPopover} from './components/anchor_popover';
import {StateTracker} from './components/state_tracker';


domready(function(): void {
    new BoardSelector();
    new ThemeSelector();
    new TopicReloader();
    new AnchorPopover();
    new StateTracker();
});
