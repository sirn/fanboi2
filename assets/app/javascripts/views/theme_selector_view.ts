import { h, VNode } from "virtual-dom";

export interface ITheme {
    className: string;
    identifier: string;
    name: string;
}

export class ThemeSelectorView {
    constructor(public themes: ITheme[]) {}

    render(currentTheme?: string): VNode {
        return h(
            "ul",
            { className: "panel__item list flex flex--row flex--gap-s u-txt-s" },
            [
                h("li", { className: "list__item flex__item" }, ["Theme"]),
                h("li", { className: "list__item flex__item" }, [
                    h(
                        "ul",
                        { className: "list flex flex--row flex--gap-s" },
                        this.themes.map((theme: ITheme): VNode => {
                            return h("li", { className: "list__item flex__item" }, [
                                h(
                                    "a",
                                    {
                                        href: "#",
                                        dataset: {
                                            themeSelectorItem: theme.identifier,
                                        },
                                        className:
                                            currentTheme &&
                                            currentTheme == theme.identifier
                                                ? [
                                                      "u-txt-unlinked",
                                                      "u-txt-gray4",
                                                  ].join(" ")
                                                : [],
                                    },
                                    [
                                        currentTheme && currentTheme == theme.identifier
                                            ? h("strong", {}, [theme.name])
                                            : theme.name,
                                    ]
                                ),
                            ]);
                        })
                    ),
                ]),
            ]
        );
    }
}
