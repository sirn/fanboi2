import { VNode, create, diff, patch, h } from "virtual-dom";

export interface ITheme {
    className: string;
    identifier: string;
    name: string;
}

export class ThemeSelectorView {
    constructor(public themes: ITheme[]) {}

    render(currentTheme?: string): VNode {
        return h("ul", { className: "links" }, [
            h("li", { className: "links__item" }, ["Theme"]),
            this.renderThemes(currentTheme),
        ]);
    }

    private renderThemes(currentTheme?: string): VNode[] {
        return this.themes.map((theme: ITheme): VNode => {
            let themeSelectorClass = ThemeSelectorView.getSelectorStateClass(
                theme.identifier,
                currentTheme,
            );

            return h(
                "li",
                {
                    className: "links__item" + themeSelectorClass,
                },
                [
                    h(
                        "a",
                        {
                            href: "#",
                            dataset: { themeSelectorItem: theme.identifier },
                        },
                        [theme.name],
                    ),
                ],
            );
        });
    }

    static getSelectorStateClass(identifier: string, currentTheme?: string): string {
        return currentTheme && currentTheme == identifier
            ? " links__item--current"
            : "";
    }
}
