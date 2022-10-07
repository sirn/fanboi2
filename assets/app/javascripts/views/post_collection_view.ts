import isEqual = require("lodash.isequal");
import { h, VNode } from "virtual-dom";
import { Post } from "../models/post";
import { formatDate } from "../utils/formatters";
import { mergeClasses, mergeDatasets } from "../utils/template";

export class PostCollectionView {
    posts: Post[];

    // Cache
    postsNode: VNode[];
    postArgs: any = [];

    constructor(posts: Post[]) {
        this.posts = posts;
    }

    render(args: any = {}): VNode {
        let postArgs = args.post || {};

        if (!this.postsNode || !isEqual(this.postArgs, postArgs)) {
            let postPanelArgs = postArgs.panel || { className: "panel--shade2" };
            let postContainerArgs = postArgs.container || {};

            this.postArgs = postArgs;
            this.postsNode = this.posts.map((post: Post): VNode => {
                return h(
                    "div",
                    mergeDatasets(
                        mergeClasses(postPanelArgs, ["panel", "panel--separator"]),
                        {
                            post: post.number,
                        }
                    ),
                    [
                        h("div", mergeClasses(postContainerArgs, ["container"]), [
                            h(
                                "div",
                                mergeClasses(postArgs, [
                                    "post",
                                    "post--datetime-mobile",
                                ]),
                                [
                                    h(
                                        "div",
                                        { className: "panel__item post__header" },
                                        [
                                            h(
                                                "span",
                                                {
                                                    className: [
                                                        "post__item",
                                                        ...[
                                                            post.bumped
                                                                ? "post__item--bumped"
                                                                : "post__item--saged",
                                                        ],
                                                        "u-mg-right-xs",
                                                    ].join(" "),
                                                    dataset: {
                                                        topicQuickReply: post.number,
                                                    },
                                                },
                                                [post.number.toString()]
                                            ),
                                            h(
                                                "span",
                                                {
                                                    className: [
                                                        "post__item",
                                                        "post__item--name",
                                                        "u-mg-right-xs",
                                                    ].join(" "),
                                                },
                                                [post.name]
                                            ),
                                            h(
                                                "span",
                                                {
                                                    className: [
                                                        "post__item",
                                                        "post__item--datetime",
                                                        "u-mg-right-xs-tablet",
                                                    ].join(" "),
                                                },
                                                [
                                                    `Posted ${formatDate(
                                                        new Date(post.createdAt)
                                                    )}`,
                                                ]
                                            ),
                                            post.ident
                                                ? h(
                                                      "span",
                                                      {
                                                          className: [
                                                              "post__item",
                                                              "post__item--ident",
                                                              "ident",
                                                              ...(post.identType !=
                                                              "ident"
                                                                  ? [
                                                                        `ident--${post.identType.replace(
                                                                            "ident_",
                                                                            ""
                                                                        )}`,
                                                                    ]
                                                                  : []),
                                                          ].join(" "),
                                                      },
                                                      [
                                                          `${PostCollectionView.getPostIdentName(
                                                              post
                                                          )}:${post.ident}`,
                                                      ]
                                                  )
                                                : "",
                                        ]
                                    ),
                                    h(
                                        "div",
                                        {
                                            className: "panel__item post__container",
                                            innerHTML: post.bodyFormatted,
                                        },
                                        []
                                    ),
                                ]
                            ),
                        ]),
                    ]
                );
            });
        }

        return h("div", mergeDatasets(args, { postCollection: true }), this.postsNode);
    }

    private static getPostIdentName(post: Post): string {
        switch (post.identType) {
            case "ident_v6": {
                return "ID6";
            }

            default: {
                return "ID";
            }
        }
    }
}
