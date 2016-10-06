import Cookies = require('js-cookie');
import {VNode, create, diff, patch, h} from 'virtual-dom';

import {SingletonComponent} from './base';
import {ThemeSelectorView, ITheme} from '../views/theme_selector_view';


export class Theme implements ITheme {
    className: string;
    constructor(public identifier: string, public name: string) {}
}


const themes = [
    new Theme('topaz', 'Topaz'),
    new Theme('obsidian', 'Obsidian'),
    new Theme('debug', 'Debug'),
];


export class ThemeSelector extends SingletonComponent {
    public targetSelector = '[data-theme-selector]';

    targetElement: Element;
    selectorView: ThemeSelectorView;
    selectorNode: VNode;
    selectorElement: Element;

    protected bindOne(element: Element) {
        this.selectorView = new ThemeSelectorView(themes);
        this.selectorNode = this.selectorView.render(
            document.body.className.replace(/theme-/, '')
        );

        this.targetElement = element;
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
