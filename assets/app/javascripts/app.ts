import domready = require("domready");
import { BoardSelector } from "./components/board_selector";
import { ThemeSelector } from "./components/theme_selector";
import { AnchorPopover } from "./components/anchor_popover";
import { TopicManager } from "./components/topic_manager";
import { TopicReloader } from "./components/topic_reloader";
import { TopicStateTracker } from "./components/topic_state_tracker";
import { TopicInlineReply } from "./components/topic_inline_reply";
import { TopicQuickReply } from "./components/topic_quick_reply";

domready(function(): void {
    new BoardSelector();
    new ThemeSelector();
    new AnchorPopover();

    // Components with topic manager dependencies.
    new TopicManager();
    new TopicReloader();
    new TopicStateTracker();
    new TopicInlineReply();
    new TopicQuickReply();
});
