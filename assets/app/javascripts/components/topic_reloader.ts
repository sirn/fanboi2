import {create} from 'virtual-dom';

import {SingletonComponent} from './base';
import {Post} from '../models/post';
import {PostCollectionView} from '../views/post_collection_view';
import {LoadingState} from '../utils/loading';


export class TopicReloader extends SingletonComponent {
    public targetSelector = '[data-topic-reloader]';

    targetElement: Element;
    buttonElement: Element;
    topicId: number;
    lastPostNumber: number;
    loadingState: LoadingState;

    protected bindOne(element: Element) {
        let self = this;
        let buttonSelector = '[data-topic-reloader-button]';

        this.loadingState = new LoadingState();
        this.topicId = parseInt(element.getAttribute('data-topic-reloader'), 10);
        this.targetElement = element;
        this.refreshButtonState();
        this.listenDocumentEvent();

        this.buttonElement.addEventListener('click', function(e: Event) {
            e.preventDefault();
            self.eventButtonClicked();
        });
    }

    private eventButtonClicked(): void {
        let self = this;

        this.loadingState.bind(this.buttonElement, function() {
            return Post.queryAll(
                self.topicId,
                `${self.lastPostNumber + 1}-`
            ).then(function(posts: Array<Post>) {
                if (posts && posts.length) {
                    let lastPost = posts[posts.length - 1];
                    self.refreshButtonState(lastPost.number);
                    self.updateHistoryState(lastPost.number);
                    self.renderButtonAlt();
                    self.appendPosts(posts);
                }
            });
        });
    }

    private listenDocumentEvent(): void {
        let self = this;
        document.addEventListener('reloadTopic', function(e: CustomEvent) {
            if (e.detail.topicId == self.topicId) {
                self.eventButtonClicked();
            }
        });
    }

    private refreshButtonState(newNum?: number): void {
        let btnAttribute = 'data-topic-reloader-button';

        if (!this.buttonElement) {
            let btnSelector = `[${btnAttribute}]`;
            this.buttonElement = this.targetElement.querySelector(btnSelector);
            this.lastPostNumber = parseInt(
                this.buttonElement.getAttribute(btnAttribute),
                10
            );
        }

        if (newNum) {
            this.lastPostNumber = newNum;
            this.buttonElement.setAttribute(btnAttribute, String(newNum));
            this.buttonElement.setAttribute(
                'href',
                this.buttonElement.getAttribute('href').replace(
                    /^(\/\w+\/\d+)\/\d+\-\/$/,
                    `$1/${newNum}-/`
                )
            );
        }
    }

    private updateHistoryState(newNum?: number): void {
        if (window.history.replaceState) {
            let path = window.location.pathname;
            let newPath: string;

            if (path.match(/\/\d+\/?$/)) {
                newPath = path.replace(
                    /\/(\d+)\/?$/,
                    `/$1-${newNum}/`
                );
            } else if (path.match(/\-\d+\/?$/)) {
                newPath = path.replace(
                    /(\d+)\/?$/,
                    `${newNum}/`
                );
            }

            if (newPath) {
                window.history.replaceState(
                    null,
                    `Posts until ${newNum}`,
                    newPath
                );
            }
        }
    }

    private renderButtonAlt(): void {
        let btnAltLabelAttr = 'data-topic-reloader-alt-label';
        let btnAltLabel = this.buttonElement.getAttribute(btnAltLabelAttr);

        if (btnAltLabel) {
            this.buttonElement.innerHTML = btnAltLabel;
        }

        let btnAltClassAttr = 'data-topic-reloader-alt-class';
        let btnAltClass = this.buttonElement.getAttribute(btnAltClassAttr);

        if (btnAltClass) {
            this.buttonElement.className = btnAltClass;
        }
    }

    private appendPosts(posts: Post[]): void {
        let lastElement: Element;

        // Insert after the last .js-post-collection block or .post block
        // whichever available first. Because the JS view will always wrap its
        // child in a block element.
        let jsPosts = this.targetElement.querySelectorAll('.js-post-collection');
        if (jsPosts && jsPosts.length) {
            lastElement = jsPosts[jsPosts.length - 1];
        }

        if (!lastElement) {
            let posts = this.targetElement.querySelectorAll('.post');
            lastElement = posts[posts.length - 1];
        }

        if (lastElement) {
            let postNode = new PostCollectionView(posts).render();
            let postElement = create(postNode);

            this.targetElement.insertBefore(
                postElement,
                lastElement.nextSibling
            );
        }
    }
}
