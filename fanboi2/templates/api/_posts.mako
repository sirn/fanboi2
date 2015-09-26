<%namespace name='formatters' module='fanboi2.formatters' />
<div class="sheet">
    <div class="container">
        <h2 class="sheet-title">Topics</h2>
        <div class="sheet-body">
            <table class="api-table table" id="api-topic-posts">
                <tbody class="table-group">
                    <tr class="table-row">
                        <th class="table-row-header">Name</th>
                        <td class="table-row-item"><strong>api_topic_posts</strong></td>
                    </tr>
                    <tr class="table-row">
                        <th class="table-row-header">Request</th>
                        <td class="table-row-item"><code>GET ${formatters.unquoted_path(request, 'api_topic_posts', topic='{api_topic.id}')}</code></td>
                    </tr>
                    <tr class="table-row">
                        <th class="table-row-header">Response</th>
                        <td class="table-row-item">
                            <p><code>Array</code> containing <code>Object</code> of the below fields. Unicode strings are escaped in actual response.</p>
                            <table class="api-table table inner">
                                <thead class="table-group">
                                    <tr class="table-row">
                                        <th class="table-row-header">Field</th>
                                        <th class="table-row-header type">Type</th>
                                        <th class="table-row-header">Description</th>
                                    </tr>
                                </thead>
                                <tbody class="table-group">
                                    <tr class="table-row">
                                        <th class="table-row-header">body</th>
                                        <td class="table-row-item type">String</td>
                                        <td class="table-row-item">
                                            <p>The post body entered by the user in new topic or reply form.</p>
                                            <pre class="codeblock">"body":"..."</pre>
                                        </td>
                                    </tr>
                                    <tr class="table-row">
                                        <th class="table-row-header">bumped</th>
                                        <td class="table-row-item type">Boolean</td>
                                        <td class="table-row-item">
                                            <p>Boolean flag whether the post bumped the topic to top of the board.</p>
                                            <pre class="codeblock">"bumped":true</pre>
                                        </td>
                                    </tr>
                                    <tr class="table-row">
                                        <th class="table-row-header">body_formatted</th>
                                        <td class="table-row-item type">String</td>
                                        <td class="table-row-item">
                                            <p>Same as <strong>body</strong> but format it to HTML using internal formatter.</p>
                                            <pre class="codeblock">"body_formatted":"&lt;p&gt;...&lt;/p&gt;"</pre>
                                        </td>
                                    </tr>
                                    <tr class="table-row">
                                        <th class="table-row-header">name</th>
                                        <td class="table-row-item type">String</td>
                                        <td class="table-row-item">
                                            <p>The name entered for this post.</p>
                                            <pre class="codeblock">"name":"Nameless Fanboi"</pre>
                                        </td>
                                    </tr>
                                    <tr class="table-row">
                                        <th class="table-row-header">topic_id</th>
                                        <td class="table-row-item type">Integer</td>
                                        <td class="table-row-item">
                                            <p>Internal ID of a topic the post is associated with.</p>
                                            <pre class="codeblock">"topic_id":1</pre>
                                        </td>
                                    </tr>
                                    <tr class="table-row">
                                        <th class="table-row-header">created_at</th>
                                        <td class="table-row-item type">String</td>
                                        <td class="table-row-item">
                                            <p><a href="http://en.wikipedia.org/wiki/ISO_8601">ISO 8601</a>-formatted datetime of when the post was created.</p>
                                            <pre class="codeblock">"created_at":"2013-02-06T16:45:20.275693-08:00"</pre>
                                        </td>
                                    </tr>
                                    <tr class="table-row">
                                        <th class="table-row-header">ident</th>
                                        <td class="table-row-item type">String</td>
                                        <td class="table-row-item">
                                            <p>Unique ID for each user that was generated when the board has <strong>use_ident</strong> enabled.</p>
                                            <pre class="codeblock">"ident":"7xFKuAP5G"</pre>
                                        </td>
                                    </tr>
                                    <tr class="table-row">
                                        <th class="table-row-header">id</th>
                                        <td class="table-row-item type">Integer</td>
                                        <td class="table-row-item">
                                            <p>Internal ID for the post.</p>
                                            <pre class="codeblock">"id":1</pre>
                                        </td>
                                    </tr>
                                    <tr class="table-row">
                                        <th class="table-row-header">number</th>
                                        <td class="table-row-item type">Integer</td>
                                        <td class="table-row-item">
                                            <p>Order of the post within the topic.</p>
                                            <pre class="codeblock">"number":1</pre>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </td>
                    </tr>
                </tbody>
            </table>

            <table class="api-table table" id="api-topic-posts-scoped">
                <tbody class="table-group">
                    <tr class="table-row">
                        <th class="table-row-header">Name</th>
                        <td class="table-row-item"><strong>api_topic_posts_scoped</strong></td>
                    </tr>
                    <tr class="table-row">
                        <th class="table-row-header">Request</th>
                        <td class="table-row-item">
                            <p><code>GET ${formatters.unquoted_path(request, 'api_topic_posts_scoped', topic='{api_topic.id}', query='{query}')}</code></p>
                            <p>The query could be one of the following:</p>
                            <table class="api-table table inner">
                                <thead class="table-group">
                                    <tr class="table-row">
                                        <th class="table-row-header">Query</th>
                                        <th class="table-row-header">Description</th>
                                    </tr>
                                </thead>
                                <tbody class="table-group">
                                    <tr class="table-row">
                                        <th class="table-row-header">{n}</th>
                                        <td class="table-row-item">Query a single post with <em>n</em> number.</td>
                                    </tr>
                                    <tr class="table-row">
                                        <th class="table-row-header">{n1}-{n2}</th>
                                        <td class="table-row-item">Query posts from <em>n1</em> to <em>n2</em>. If <em>n1</em> or <em>n2</em> is not given, 0 and last post are assumed respectively.</td>
                                    </tr>
                                    <tr class="table-row">
                                        <th class="table-row-header">l{n}</th>
                                        <td class="table-row-item">Query the last <em>n</em> posts, for example, <strong>l10</strong> will list the last 10 posts.</td>
                                    </tr>
                                    <tr class="table-row">
                                        <th class="table-row-header">recent</th>
                                        <td class="table-row-item">Alias for <strong>l30</strong>.</td>
                                    </tr>
                                </tbody>
                            </table>
                        </td>
                    </tr>
                    <tr class="table-row">
                        <th class="table-row-header">Response</th>
                        <td class="table-row-item">Same as <a href="#api-topic-posts">api_topic_posts</a>.</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</div>
