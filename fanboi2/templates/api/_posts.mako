<%namespace name="formatters" module="fanboi2.helpers.formatters" />
<%namespace name="api" file="../partials/_api.mako" />
<%api:render_api name="api-topic-posts-new" title="Creating new post in a topic" method="POST">
    <%def name="path()">
        ${formatters.unquoted_path(request, 'api_topic_posts', topic='{api-topic.id}')}
    </%def>
    <%def name="description()">
        <p>Use this endpoint to create a new post in a specific topic (i.e. post a reply). Please note that this API will <em>enqueue</em> the post with the global posting queue and will not guarantee that the post will be successful. To retrieve the status of the post, please see <a href="#api-task">#api-task</a>.</p>
    </%def>
    <%def name="request_object()">
        <tr>
            <th>body</th>
            <td>String</td>
            <td>Content of the topic. From 5 to 4,000 characters.</td>
        </tr>
        <tr>
            <th>bumped</th>
            <td>Boolean</td>
            <td>A flag whether the post should bump the topic to top of the board.</td>
        </tr>
    </%def>
    <%def name="response_body()">
        <p>Either an <a href="#api-task">#api-task</a> or an <a herf="#api-error">#api-error</a>.</p>
    </%def>
</%api:render_api>
<%api:render_api name="api-topic-posts" title="Retrieving posts associated to a topic" method="GET">
    <%def name="path()">
        ${formatters.unquoted_path(request, 'api_topic_posts', topic='{api-topic.id}')}
    </%def>
    <%def name="description()">
        <p>Use this endpoint to retrieve a list of posts associated to the specific topic. By default this API will returns all posts. For a more specific query scope, please see <a href="#api-topic-posts-scoped">#api-topic-posts-scoped</a>.</p>
    </%def>
    <%def name="request_query()">
        <tr>
            <th>?topic=1</th>
            <td>Include the topic in a <code>topic</code> object.</td>
        </tr>
        <tr>
            <th>?board=1</th>
            <td>Include the board in a <code>boards</code> object. Only if <code>topic</code> is present.</td>
        </tr>
    </%def>
    <%def name="response_object()">
        <tr>
            <th>type</th>
            <td>String</td>
            <td>
                <p>The type of API object. The value is always "post".</p>
                <pre>"type":"post"</pre>
            </td>
        </tr>
        <tr>
            <th>id</th>
            <td>Integer</td>
            <td>
                <p>Internal ID for the post.</p>
                <pre>"id":1</pre>
            </td>
        </tr>
        <tr>
            <th>body</th>
            <td>String</td>
            <td>
                <p>The post body entered by the user in new topic or reply form.</p>
                <pre>"body":"..."</pre>
            </td>
        </tr>
        <tr>
            <th>body_formatted</th>
            <td>String</td>
            <td>
                <p>Same as <strong>body</strong> but format it to HTML using internal formatter.</p>
                <pre>"body_formatted":"&lt;p&gt;...&lt;/p&gt;"</pre>
            </td>
        </tr>
        <tr>
            <th>bumped</th>
            <td>Boolean</td>
            <td>
                <p>A flag whether the post bumped the topic to top of the board.</p>
                <pre>"bumped":true</pre>
            </td>
        </tr>
        <tr>
            <th>created_at</th>
            <td>String</td>
            <td>
                <p><a href="http://en.wikipedia.org/wiki/ISO_8601">ISO 8601</a>-formatted datetime of when the post was created.</p>
                <pre>"created_at":"2013-02-06T16:45:20.275693-08:00"</pre>
            </td>
        </tr>
        <tr>
            <th>ident</th>
            <td>String</td>
            <td>
                <p>Unique ID for each user that was generated when the board has <strong>use_ident</strong> enabled.</p>
                <pre>"ident":"7xFKuAP5G"</pre>
            </td>
        </tr>
        <tr>
            <th>ident_type</th>
            <td>String</td>
            <td>
                <p>The type of the user ident.</p>
                <p>IPv6 idents are normalized to <code>/64</code> CIDR by default which may be shared between multiple users in some network configuration (such as mobile network) and thus are distinguised by a separate ident_type.</p>
                <ul>
                    <li><strong>ident</strong> — normal user ident (IPv4)</li>
                    <li><strong>ident_v6</strong> — normal user ident (IPv6)</li>
                    <li><strong>ident_admin</strong> — admin ident</li>
                </ul>
                <pre>"ident_type":"ident"</pre>
            </td>
        </tr>
        <tr>
            <th>name</th>
            <td>String</td>
            <td>
                <p>The name entered for this post.</p>
                <pre>"name":"Nameless Fanboi"</pre>
            </td>
        </tr>
        <tr>
            <th>number</th>
            <td>Integer</td>
            <td>
                <p>Order of the post within the topic.</p>
                <pre>"number":1</pre>
            </td>
        </tr>
        <tr>
            <th>topic_id</th>
            <td>Integer</td>
            <td>
                <p>Internal ID of a topic the post is associated with.</p>
                <pre>"topic_id":1</pre>
            </td>
        </tr>
        <tr>
            <th>path</th>
            <td>String</td>
            <td>
                <p>The path to this resource.</p>
                <pre>"path":"/api/1.0/topics/1/posts/"</pre>
            </td>
        </tr>
    </%def>
</%api:render_api>
<%api:render_api name="api-topic-posts-scoped" title="Retrieving posts associated to a topic with scope" method="GET">
    <%def name="path()">
        ${formatters.unquoted_path(request, 'api_topic_posts_scoped', topic='{api-topic.id}', query='{query}')}
    </%def>
    <%def name="description()">
        <p>Use this endpoint to scope posts with the given <em>queries</em>.</p>
    </%def>
    <%def name="request_query()">
        <tr>
            <th>?topic=1</th>
            <td>Include the topic in a <code>topic</code> object.</td>
        </tr>
        <tr>
            <th>?board=1</th>
            <td>Include the board in a <code>boards</code> object. Only if <code>topic</code> is present.</td>
        </tr>
    </%def>
    <%def name="request_body()">
        <p>The <em>query</em> could be one of the following:</p>
        <table>
            <thead>
                <tr>
                    <th>Query</th>
                    <th>Description</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <th>{n}</th>
                    <td>Query a single post with <em>n</em> number.</td>
                </tr>
                <tr>
                    <th>{n1}-{n2}</th>
                    <td>Query posts from <em>n1</em> to <em>n2</em>. If <em>n1</em> or <em>n2</em> is not given, 0 and last post are assumed respectively.</td>
                </tr>
                <tr>
                    <th>l{n}</th>
                    <td>Query the last <em>n</em> posts, for example, <strong>l10</strong> will list the last 10 posts.</td>
                </tr>
                <tr>
                    <th>recent</th>
                    <td>Alias for <strong>l30</strong>.</td>
                </tr>
            </tbody>
        </table>
    </%def>
    <%def name="response_body()">
        <p>Same as <a href="#api-topic-posts">#api-topic-posts</a>.</p>
    </%def>
</%api:render_api>
