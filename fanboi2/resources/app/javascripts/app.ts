import Topic from './models/topic';
import Post from './models/post';

Topic.queryId(1000).then(function(topic: Topic) {
    topic.getPosts("l5").then(function(posts: Iterable<Post>) {
        for (var post of posts) {
            console.log(post);
        }
    });
});
