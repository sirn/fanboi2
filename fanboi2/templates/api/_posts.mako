<%namespace name='formatters' module='fanboi2.helpers.formatters' />
<div class="api-section" id="api-topic-posts-new">
    <div class="api-request">
        <div class="container">
            <h2 class="api-request-title">Creating new post in a topic <span class="api-request-name">#api-topic-posts-new</span></h2>
            <div class="api-request-endpoint"><span class="api-request-verb verb-post">POST</span> ${formatters.unquoted_path(request, 'api_topic_posts', topic='{api-topic.id}')}</div>
            <div class="api-request-body">
                <p>Use this endpoint to create a new post in a specific topic (i.e. post a reply). Please note that this API will <em>enqueue</em> the post with the global posting queue and will not guarantee that the post will be successful. To retrieve the status of the post, please see <a href="#api-task">#api-task</a>.</p>
                <table class="api-table">
                    <thead class="api-table-header">
                        <tr class="api-table-row">
                            <th class="api-table-item title lead">Parameters</th>
                            <th class="api-table-item title sublead">Type</th>
                            <th class="api-table-item title">Description</th>
                        </tr>
                    </thead>
                    <tbody class="api-table-body">
                        <tr class="api-table-row">
                            <th class="api-table-item title">body</th>
                            <td class="api-table-item type">String</td>
                            <td class="api-table-item">Content of the topic. From 5 to 4,000 characters.</td>
                        </tr>
                        <tr class="api-table-row">
                            <th class="api-table-item title">bumped</th>
                            <td class="api-table-item type">Boolean</td>
                            <td class="api-table-item">A flag whether the post should bump the topic to top of the board.</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    <div class="api-response">
        <div class="container">
            <h3 class="api-response-title">Response</h3>
            <div class="api-response-body">
                <p>Either an <a href="#api-task">#api-task</a> or an <a herf="#api-error">#api-error</a>.</p>
            </div>
        </div>
    </div>
</div>

<div class="api-section" id="api-topic-posts">
    <div class="api-request">
        <div class="container">
            <h2 class="api-request-title">Retrieving posts associated to a topic <span class="api-request-name">#api-topic-posts</span></h2>
            <div class="api-request-endpoint"><span class="api-request-verb verb-get">GET</span> ${formatters.unquoted_path(request, 'api_topic_posts', topic='{api-topic.id}')}</div>
            <div class="api-request-body">
                <p>Use this endpoint to retrieve a list of posts associated to the specific topic. By default this API will returns all posts. For a more specific query scope, please see <a href="#api-topic-posts-scoped">#api-topic-posts-scoped</a>.</p>
                <table class="api-table">
                    <thead class="api-table-header">
                        <tr class="api-table-row">
                            <th class="api-table-item title lead">Query string</th>
                            <th class="api-table-item title">Description</th>
                        </tr>
                    </thead>
                    <tbody class="api-table-body">
                        <tr class="api-table-row">
                            <th class="api-table-item title">?topic=1</th>
                            <td class="api-table-item">Include the topic in a <code>topic</code> object.</td>
                        </tr>
                        <tr class="api-table-row">
                            <th class="api-table-item title">?board=1</th>
                            <td class="api-table-item">Include the board in a <code>boards</code> object. Only if <code>topic</code> is present.</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    <div class="api-response">
        <div class="container">
            <h3 class="api-response-title">Response</h3>
            <div class="api-response-body">
                <table class="api-table inner">
                    <thead class="api-table-header">
                        <tr class="api-table-row">
                            <th class="api-table-item title lead">Field</th>
                            <th class="api-table-item title sublead">Type</th>
                            <th class="api-table-item title">Description</th>
                        </tr>
                    </thead>
                    <tbody class="api-table-body">
                        <tr class="api-table-row">
                            <th class="api-table-item title">type</th>
                            <td class="api-table-item type">String</td>
                            <td class="api-table-item">
                                <p>The type of API object. The value is always "post".</p>
                                <pre class="codeblock">"type":"post"</pre>
                            </td>
                        </tr>
                        <tr class="api-table-row">
                            <th class="api-table-item title">id</th>
                            <td class="api-table-item type">Integer</td>
                            <td class="api-table-item">
                                <p>Internal ID for the post.</p>
                                <pre class="codeblock">"id":1</pre>
                            </td>
                        </tr>
                        <tr class="api-table-row">
                            <th class="api-table-item title">body</th>
                            <td class="api-table-item type">String</td>
                            <td class="api-table-item">
                                <p>The post body entered by the user in new topic or reply form.</p>
                                <pre class="codeblock">"body":"..."</pre>
                            </td>
                        </tr>
                        <tr class="api-table-row">
                            <th class="api-table-item title">body_formatted</th>
                            <td class="api-table-item type">String</td>
                            <td class="api-table-item">
                                <p>Same as <strong>body</strong> but format it to HTML using internal formatter.</p>
                                <pre class="codeblock">"body_formatted":"&lt;p&gt;...&lt;/p&gt;"</pre>
                            </td>
                        </tr>
                        <tr class="api-table-row">
                            <th class="api-table-item title">bumped</th>
                            <td class="api-table-item type">Boolean</td>
                            <td class="api-table-item">
                                <p>A flag whether the post bumped the topic to top of the board.</p>
                                <pre class="codeblock">"bumped":true</pre>
                            </td>
                        </tr>
                        <tr class="api-table-row">
                            <th class="api-table-item title">created_at</th>
                            <td class="api-table-item type">String</td>
                            <td class="api-table-item">
                                <p><a href="http://en.wikipedia.org/wiki/ISO_8601">ISO 8601</a>-formatted datetime of when the post was created.</p>
                                <pre class="codeblock">"created_at":"2013-02-06T16:45:20.275693-08:00"</pre>
                            </td>
                        </tr>
                        <tr class="api-table-row">
                            <th class="api-table-item title">ident</th>
                            <td class="api-table-item type">String</td>
                            <td class="api-table-item">
                                <p>Unique ID for each user that was generated when the board has <strong>use_ident</strong> enabled.</p>
                                <pre class="codeblock">"ident":"7xFKuAP5G"</pre>
                            </td>
                        </tr>
                        <tr class="api-table-row">
                            <th class="api-table-item title">name</th>
                            <td class="api-table-item type">String</td>
                            <td class="api-table-item">
                                <p>The name entered for this post.</p>
                                <pre class="codeblock">"name":"Nameless Fanboi"</pre>
                            </td>
                        </tr>
                        <tr class="api-table-row">
                            <th class="api-table-item title">number</th>
                            <td class="api-table-item type">Integer</td>
                            <td class="api-table-item">
                                <p>Order of the post within the topic.</p>
                                <pre class="codeblock">"number":1</pre>
                            </td>
                        </tr>
                        <tr class="api-table-row">
                            <th class="api-table-item title">topic_id</th>
                            <td class="api-table-item type">Integer</td>
                            <td class="api-table-item">
                                <p>Internal ID of a topic the post is associated with.</p>
                                <pre class="codeblock">"topic_id":1</pre>
                            </td>
                        </tr>
                        <tr class="api-table-row">
                            <th class="api-table-item title">path</th>
                            <td class="api-table-item type">String</td>
                            <td class="api-table-item">
                                <p>The path to this resource.</p>
                                <pre class="codeblock">"path":"/api/1.0/topics/1/posts/"</pre>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</div>

<div class="api-section" id="api-topic-posts-scoped">
    <div class="api-request">
        <div class="container">
            <h2 class="api-request-title">Retrieving posts associated to a topic with scope <span class="api-request-name">#api-topic-posts-scoped</span></h2>
            <div class="api-request-endpoint"><span class="api-request-verb verb-get">GET</span> ${formatters.unquoted_path(request, 'api_topic_posts_scoped', topic='{api-topic.id}', query='{query}')}</div>
            <div class="api-request-body">
                <p>Use this endpoint to scope posts with the given <em>queries</em>. The <em>query</em> could be one of the following:</p>
                <table class="api-table">
                    <thead class="api-table-header">
                        <tr class="api-table-row">
                            <th class="api-table-item title lead">Query</th>
                            <th class="api-table-item title">Description</th>
                        </tr>
                    </thead>
                    <tbody class="api-table-body">
                        <tr class="api-table-row">
                            <th class="api-table-item title">{n}</th>
                            <td class="api-table-item">Query a single post with <em>n</em> number.</td>
                        </tr>
                        <tr class="api-table-row">
                            <th class="api-table-item title">{n1}-{n2}</th>
                            <td class="api-table-item">Query posts from <em>n1</em> to <em>n2</em>. If <em>n1</em> or <em>n2</em> is not given, 0 and last post are assumed respectively.</td>
                        </tr>
                        <tr class="api-table-row">
                            <th class="api-table-item title">l{n}</th>
                            <td class="api-table-item">Query the last <em>n</em> posts, for example, <strong>l10</strong> will list the last 10 posts.</td>
                        </tr>
                        <tr class="api-table-row">
                            <th class="api-table-item title">recent</th>
                            <td class="api-table-item">Alias for <strong>l30</strong>.</td>
                        </tr>
                    </tbody>
                </table>
                <table class="api-table">
                    <thead class="api-table-header">
                        <tr class="api-table-row">
                            <th class="api-table-item title lead">Query string</th>
                            <th class="api-table-item title">Description</th>
                        </tr>
                    </thead>
                    <tbody class="api-table-body">
                        <tr class="api-table-row">
                            <th class="api-table-item title">?topic=1</th>
                            <td class="api-table-item">Include the topic in a <code>topic</code> object.</td>
                        </tr>
                        <tr class="api-table-row">
                            <th class="api-table-item title">?board=1</th>
                            <td class="api-table-item">Include the board in a <code>boards</code> object. Only if <code>topic</code> is present.</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    <div class="api-response">
        <div class="container">
            <h3 class="api-response-title">Response</h3>
            <div class="api-response-body">
                <p>Same as <a href="#api-topic-posts">#api-topic-posts</a>.</p>
            </div>
        </div>
    </div>
</div>
