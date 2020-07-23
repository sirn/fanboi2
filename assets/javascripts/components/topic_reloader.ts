import { SingletonComponent } from "./base";
import { dispatchCustomEvent } from "../utils/elements";
import { LoadingState } from "../utils/loading";

export class TopicReloader extends SingletonComponent {
    public targetSelector = "[data-topic-reloader]";

    protected bindOne($target: Element) {
        let $topic = $target.closest("[data-topic]");
        let loadingState = new LoadingState();

        $target.addEventListener("click", (e: Event) => {
            e.preventDefault();
            loadingState.bind(() => {
                return new Promise(resolve => {
                    dispatchCustomEvent($target, "loadPosts", {
                        callback: () => {
                            resolve();
                        },
                    });
                });
            }, $target);
        });

        if ($topic) {
            $topic.addEventListener("postsLoaded", (e: CustomEvent) => {
                this.updateButtonAlt($target);
                this.refreshButtonState($target, e.detail.lastPostNumber);
                this.updateButtonAlt($target);
            });
        }
    }

    private updateButtonAlt($target: Element): void {
        let altLabel = $target.getAttribute("data-topic-reloader-label");
        let altClass = $target.getAttribute("data-topic-reloader-class");

        if (altLabel) {
            $target.innerHTML = altLabel;
        }

        if (altClass) {
            $target.className = altClass;
        }
    }

    private refreshButtonState($target: Element, lastPostNumber: number): void {
        let originalHref = $target.getAttribute("href");

        if (originalHref) {
            $target.setAttribute(
                "href",
                originalHref.replace(
                    /^(\/\w+\/\d+)\/\d+\-\/$/,
                    `$1/${lastPostNumber}-/`,
                ),
            );
        }
    }
}
