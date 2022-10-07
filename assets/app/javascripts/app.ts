import domready = require("domready");
import { BoardSelector } from "./components/board_selector";
import { ThemeSelector } from "./components/theme_selector";
import { AnchorModal } from "./components/anchor_modal";
import { TopicManager } from "./components/topic_manager";
import { TopicReloader } from "./components/topic_reloader";
import { TopicStateTracker } from "./components/topic_state_tracker";
import { TopicReplyForm } from "./components/topic_reply_form";
import { TopicReply } from "./components/topic_reply";

domready(function (): void {
    new BoardSelector();
    new ThemeSelector();
    new AnchorModal();

    // Components with topic manager dependencies.
    new TopicManager();
    new TopicReloader();
    new TopicStateTracker();
    new TopicReplyForm();
    new TopicReply();
});
