import {SingletonComponent} from './base';
import {dispatchCustomEvent} from '../utils/elements';
import {LoadingState} from '../utils/loading';


export class TopicReloader extends SingletonComponent {
    public targetSelector = '[data-topic-reloader]';

    protected bindOne(element: Element) {
        let self = this;
        let loadingState = new LoadingState();

        element.addEventListener('click', function(e: Event) {
            e.preventDefault();
            loadingState.bind(element, function() {
                return new Promise(function(resolve) {
                    dispatchCustomEvent(element, 'loadPosts', {
                        callback: function() {
                            resolve();
                        }
                    });
                });
            });
        });

        let topicElement = element.closest('[data-topic]');
        topicElement.addEventListener('postsLoaded', function(e: CustomEvent) {
            self.updateButtonAlt(element);
            self.refreshButtonState(element, e.detail.lastPostNumber);
            self.updateButtonAlt(element);
        });
    }

    private updateButtonAlt(element: Element): void {
        let altLabel = element.getAttribute('data-topic-reloader-label');
        let altClass = element.getAttribute('data-topic-reloader-class');
        if (altLabel) { element.innerHTML = altLabel; }
        if (altClass) { element.className = altClass; }
    }

    private refreshButtonState(element: Element, lastPostNumber: number): void {
        element.setAttribute(
            'href',
            element.getAttribute('href').replace(
                /^(\/\w+\/\d+)\/\d+\-\/$/,
                `$1/${lastPostNumber}-/`
            )
        );
    }
}
