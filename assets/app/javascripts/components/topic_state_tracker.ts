import { CollectionComponent } from "./base";
import { dispatchCustomEvent } from "../utils/elements";

export class TopicStateTracker extends CollectionComponent {
    public targetSelector = "[data-topic-state-tracker]";

    protected bindOne($target: Element): void {
        let trackerName = $target.getAttribute("data-topic-state-tracker");

        if (!trackerName) {
            throw new Error("State tracker name is empty when it should not.");
        }

        if ($target instanceof HTMLInputElement) {
            switch ($target.type) {
                case "checkbox":
                    this.bindCheckbox(trackerName, $target);
                    break;
            }
        } else if ($target instanceof HTMLTextAreaElement) {
            this.bindTextarea(trackerName, $target);
        }
    }

    private bindCheckbox(trackerName: string, $target: HTMLInputElement): void {
        dispatchCustomEvent($target, "readState", {
            name: trackerName,
            callback: (name: string, value?: boolean) => {
                if (value != undefined) {
                    $target.checked = value;
                    $target.defaultChecked = $target.checked;
                }
            },
        });

        $target.addEventListener("change", (e: Event): void => {
            $target.defaultChecked = $target.checked;
            dispatchCustomEvent($target, "updateState", {
                name: trackerName,
                value: $target.checked,
            });
        });
    }

    private bindTextarea(trackerName: string, $target: HTMLTextAreaElement): void {
        let throttleTimer: number;

        dispatchCustomEvent($target, "readState", {
            name: trackerName,
            callback: (name: string, value?: string) => {
                if (value != undefined) {
                    $target.value = value;
                }
            },
        });

        $target.addEventListener("change", (e: Event): void => {
            clearTimeout(throttleTimer);
            throttleTimer = window.setTimeout(() => {
                dispatchCustomEvent($target, "updateState", {
                    name: trackerName,
                    value: $target.value,
                });
            }, 500);
        });
    }
}
