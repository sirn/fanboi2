import Cookies = require("js-cookie");
import { VNode, create, diff, patch, h } from "virtual-dom";
import { SingletonComponent } from "./base";
import { ThemeSelectorView, ITheme } from "../views/theme_selector_view";

export class Theme implements ITheme {
    className: string;
    constructor(public identifier: string, public name: string) {}
}

const themes = [
    new Theme("topaz", "Topaz"),
    new Theme("obsidian", "Obsidian"),
    new Theme("debug", "Debug"),
];

export class ThemeSelector extends SingletonComponent {
    public targetSelector = "[data-theme-selector]";

    protected bindOne($target: Element) {
        let selectorView = new ThemeSelectorView(themes);
        let selectorNode = selectorView.render(
            document.body.className.replace(/theme-/, ""),
        );

        let $selector = create(selectorNode);

        $target.appendChild($selector);
        $target.addEventListener("click", (e: Event) => {
            let $click = e.target;

            if (
                $click instanceof Element &&
                $click.matches("[data-theme-selector-item]")
            ) {
                let themeId = $click.getAttribute("data-theme-selector-item");

                e.preventDefault();

                if (themeId) {
                    let viewNode = selectorView.render(themeId);
                    let patches = diff(selectorNode, viewNode);

                    $selector = patch($selector, patches);
                    selectorNode = viewNode;

                    document.body.className = `theme-${themeId}`;
                    Cookies.set("_theme", themeId, {
                        expires: 365,
                        path: "/",
                    });
                }
            }
        });
    }
}
