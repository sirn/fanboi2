import {VNode, create, diff, patch, h} from 'virtual-dom';


export interface ITheme {
    className: string;
    identifier: string;
    name: string;
}


export class ThemeSelectorView {
    constructor(public themes: ITheme[]) {}

    render(currentTheme?: string): VNode {
        return h('div', {className: 'js-theme-selector'}, [
            h('span', {className: 'js-theme-selector-title'}, ['Theme']),
            this.renderThemes(currentTheme),
        ]);
    }

    private renderThemes(currentTheme?: string): VNode {
        return h('ul',
            {className: 'js-theme-selector-list'},
            this.themes.map((theme: ITheme): VNode => {
                return h('li', {className: 'js-theme-selector-list-item'}, [
                    h('a', {
                        href: '#',
                        dataset: {themeSelectorItem: theme.identifier},
                        className: ThemeSelectorView.getSelectorStateClass(
                            theme.identifier,
                            currentTheme
                        ),
                    }, [theme.name])
                ]);
            })
        );
    }

    static getSelectorStateClass(
        identifier: string,
        currentTheme?: string
    ): string {
        return currentTheme && currentTheme == identifier ? 'current' : '';
    }
}
