import {VNode, h} from 'virtual-dom';
import {formatDate} from '../utils/formatters';
import {Post} from '../models/post';


export class PostCollectionView {
    posts: Post[];

    constructor(posts: Post[]) {
        this.posts = posts;
    }

    render(): VNode {
        return h('div',
            {className: 'js-post-collection'},
            this.posts.map(function(post: Post): VNode {
                return PostCollectionView.renderPost(post);
            })
        );
    }

    private static renderPost(post: Post): VNode {
        return h('div', {className: 'post'}, [
            h('div', {className: 'container'}, [
                PostCollectionView.renderHeader(post),
                PostCollectionView.renderBody(post),
            ])
        ]);
    }

    private static renderHeader(post: Post): VNode {
        return h('div', {className: 'post-header'}, [
            PostCollectionView.renderHeaderNumber(post),
            PostCollectionView.renderHeaderName(post),
            PostCollectionView.renderHeaderDate(post),
            PostCollectionView.renderHeaderIdent(post),
        ]);
    }

    private static renderHeaderNumber(post: Post): VNode {
        let classList = ['post-header-item', 'number'];
        if (post.bumped) { classList.push('bumped'); }
        return h('span', {
            className: classList.join(' '),
        }, [String(post.number)]);
    }

    private static renderHeaderName(post: Post): VNode {
        return h('span', {
            className: 'post-header-item name'
        }, [String(post.name)]);
    }

    private static renderHeaderDate(post: Post): VNode {
        let createdAt = new Date(post.createdAt);
        let formatter = formatDate(createdAt);
        return h('span', {
            className: 'post-header-item date'
        }, [String(`Posted ${formatter}`)]);
    }

    private static renderHeaderIdent(post: Post): VNode | string {
        if (post.ident) {
            return h('span', {
                className: 'post-header-item ident'
            }, [String(`ID:${post.ident}`)]);
        } else {
            return String(null);
        }
    }

    private static renderBody(post: Post): VNode {
        return h('div', {
            className: 'post-body',
            innerHTML: post.bodyFormatted,
        }, []);
    }
}
