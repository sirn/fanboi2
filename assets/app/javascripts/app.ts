import domready = require('domready');
import {BoardSelector} from './components/board_selector';
import {ThemeSelector} from './components/theme_selector';
import {TopicReloader} from './components/topic_reloader';
import {AnchorPopover} from './components/anchor_popover';
import {StateTracker} from './components/state_tracker';
import {InlineReply} from './components/inline_reply';


domready(function(): void {
    new BoardSelector();
    new ThemeSelector();
    new TopicReloader();
    new AnchorPopover();
    new StateTracker();
    new InlineReply();
});
