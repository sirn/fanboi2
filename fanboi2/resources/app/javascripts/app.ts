/// <reference path="typings/node/node.d.ts" />
/// <reference path="typings/virtual-dom/virtual-dom.d.ts" />
/// <reference path="typings/domready/domready.d.ts" />

import 'babel-polyfill';
import * as VirtualDOM from 'virtual-dom';

import Topic from './models/topic';
import Post from './models/post';

require('domready')(function(): void {
    Topic.queryId(1000).then(function(topic: Topic) {
        topic.getPosts("l5").then(function(posts: Iterable<Post>) {
            for (var post of posts) {
                console.log(post);
            }
        });
    });
});
