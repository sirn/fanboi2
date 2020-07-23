import { VNode, h } from "virtual-dom";
import { formatDate } from "../utils/formatters";
import { Post } from "../models/post";

export class PostCollectionView {
    postsNode: VNode;

    constructor(posts: Post[]) {
        this.postsNode = PostCollectionView.renderPosts(posts);
    }

    render(): VNode {
        return this.postsNode;
    }

    private static renderPosts(posts: Post[]): VNode {
        return h(
            "div",
            { className: "js-post-collection" },
            posts.map(
                (post: Post): VNode => {
                    return h("div", { className: "post" }, [
                        h("div", { className: "container" }, [
                            PostCollectionView.renderHeader(post),
                            PostCollectionView.renderBody(post)
                        ])
                    ]);
                }
            )
        );
    }

    private static renderHeader(post: Post): VNode {
        return h("div", { className: "post-header" }, [
            PostCollectionView.renderHeaderNumber(post),
            PostCollectionView.renderHeaderName(post),
            PostCollectionView.renderHeaderDate(post),
            PostCollectionView.renderHeaderIdent(post)
        ]);
    }

    private static renderHeaderNumber(post: Post): VNode {
        let classList = ["post-header-item", "number"];

        if (post.bumped) {
            classList.push("bumped");
        }

        return h(
            "span",
            {
                className: classList.join(" "),
                dataset: {
                    topicQuickReply: post.number
                }
            },
            [post.number.toString()]
        );
    }

    private static renderHeaderName(post: Post): VNode {
        return h(
            "span",
            {
                className: "post-header-item name"
            },
            [post.name]
        );
    }

    private static renderHeaderDate(post: Post): VNode {
        let createdAt = new Date(post.createdAt);
        let formatter = formatDate(createdAt);

        return h(
            "span",
            {
                className: "post-header-item date"
            },
            [`Posted ${formatter}`]
        );
    }

    private static renderHeaderIdent(post: Post): VNode | string {
        if (post.ident) {
            let identCls = ["post-header-item", "ident"];
            let identName = "ID";

            switch (post.identType) {
                case "ident_v6": {
                    identName = "ID6";
                    identCls.push("ident-v6");
                    break;
                }

                default: {
                    identName = "ID";
                    if (post.identType != "ident") {
                        identCls.push(post.identType.replace("_", "-"));
                    }
                    break;
                }
            }

            return h(
                "span",
                {
                    className: identCls.join(" ")
                },
                [`${identName}:${post.ident}`]
            );
        } else {
            return "";
        }
    }

    private static renderBody(post: Post): VNode {
        return h(
            "div",
            {
                className: "post-body",
                innerHTML: post.bodyFormatted
            },
            []
        );
    }
}
