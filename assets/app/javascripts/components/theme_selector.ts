import Cookies = require('js-cookie');
import {VNode, create, diff, patch, h} from 'virtual-dom';
import {SingletonComponent} from './base';


class Theme {
    className: string;
    constructor(public identifier: string, public name: string) {}
}


const themes = [
    new Theme('topaz', 'Topaz'),
    new Theme('obsidian', 'Obsidian'),
    new Theme('debug', 'Debug'),
];


class ThemeSelectorListView {
    themeListNode: VNode[];

    constructor(public themes: Theme[]) {}

    render(currentTheme?: string): VNode {
        return h('div', {className: 'js-theme-selector'}, [
            h('span', {
                className: 'js-theme-selector-title'
            }, [String('Theme')]),
            this.renderThemes(currentTheme),
        ]);
    }

    private renderThemes(currentTheme?: string): VNode {
        return h('ul',
            {className: 'js-theme-selector-list'},
            this.themes.map(function(theme: Theme): VNode {
                return h('li', {className: 'js-theme-selector-list-item'}, [
                    h('a', {
                        href: '#',
                        dataset: {themeSelectorItem: theme.identifier},
                        className: ThemeSelectorListView.getSelectorStateClass(
                            theme.identifier,
                            currentTheme
                        ),
                    }, [String(theme.name)])
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


export class ThemeSelector extends SingletonComponent {
    selectorView: ThemeSelectorListView;
    selectorNode: VNode;
    selectorElement: Element;

    protected bindOne(element: Element) {
        this.selectorView = new ThemeSelectorListView(themes);
        this.selectorNode = this.selectorView.render(
            document.body.className.replace(/theme-/, '')
        );

        this.selectorElement = create(this.selectorNode);
        this.targetElement.appendChild(this.selectorElement);
        this.bindSelectorEvent();
    }

    private bindSelectorEvent(): void {
        let self = this;

        this.targetElement.addEventListener('click', function(e: Event) {
            let target = <Element>e.target;
            if (target.matches('[data-theme-selector-item]')) {
                e.preventDefault();

                let themeId = target.getAttribute('data-theme-selector-item');
                document.body.className = `theme-${themeId}`;
                Cookies.set('_theme', themeId, {
                    expires: 365,
                    path: '/'
                });

                let viewNode = self.selectorView.render(themeId);
                let patches = diff(self.selectorNode, viewNode);
                self.selectorElement = patch(self.selectorElement, patches);
                self.selectorNode = viewNode;
            }
        });
    }
}
