<%namespace name="formatters" module="fanboi2.helpers.formatters" />
<%namespace name="api" file="../partials/_api.mako" />
<%api:render_api name="api-board-topics-new" title="Creating new topic in a board" method="POST">
    <%def name="path()">
        ${formatters.unquoted_path(request, 'api_board_topics', board='{api-board.slug}')}
    </%def>
    <%def name="description()">
        <p>Use this endpoint to create a new topic in a specific board. Please note that this API will <em>enqueue</em> the topic with the global posting queue and will not guarantee that the topic will be successfully posted. To retrieve the status of topic creation, please see <a href="#api-task">#api-task</a>.</p>
    </%def>
    <%def name="request_object()">
        <tr>
            <th>title</th>
            <td>String</td>
            <td>Title of the topic. From 5 to 200 characters.</td>
        </tr>
        <tr>
            <th>body</th>
            <td>String</td>
            <td>Content of the topic. From 5 to 4,000 characters.</td>
        </tr>
    </%def>
    <%def name="response_body()">
        <p>Either an <a href="#api-task">#api-task</a> or an <a herf="#api-error">#api-error</a>.</p>
    </%def>
</%api:render_api>
<%api:render_api name="api-board-topics" title="Retrieving topics associated to a board" method="GET">
    <%def name="path()">
        ${formatters.unquoted_path(request, 'api_board_topics', board='{api-board.slug}')}
    </%def>
    <%def name="description()">
        <p>Use this endpoint to retrieve a list of topics associated to the specific board. By default this API will return the same data as board's "All topics" page which includes open topic and topic that are closed (locked and archived) within 1 week of last posted date. It is also possible to include recent posts with <em>query string</em> but doing so with this API is not recommended.</p>
    </%def>
    <%def name="request_query()">
        <tr>
            <th>?board=1</th>
            <td>Include the board in a <code>board</code> object.</td>
        </tr>
        <tr>
            <th>?posts=1</th>
            <td>Include the recent 30 posts in a <code>posts</code> object.</td>
        </tr>
    </%def>
    <%def name="response_body()">
        <p><code>Array</code> containing <a href="#api-topic">#api-topic</a>.</p>
    </%def>
</%api:render_api>
<%api:render_api name="api-topic" title="Retrieving a topic" method="GET">
    <%def name="path()">
        ${formatters.unquoted_path(request, 'api_topic', topic='{api-topic.id}')}
    </%def>
    <%def name="description()">
        <p>Use this endpoint to retrieve any individual topic. This endpoint by default will not include any posts but it is possible to instruct the API to include them using <em>query string</em>. Posts retrieved as part of this API is limited to the recent 30 posts. For retrieving a full list of posts, see <a href="#api-topic-posts">#api-topic-posts</a> and <a href="#api-topic-posts-scoped">#api-topic-posts-scoped</a>.</p>
    </%def>
    <%def name="request_query()">
        <tr>
            <th>?board=1</th>
            <td>Include the board in a <code>board</code> object.</td>
        </tr>
        <tr>
            <th>?posts=1</th>
            <td>Include the recent 30 posts in a <code>posts</code> object.</td>
        </tr>
    </%def>
    <%def name="response_object()">
        <tr>
            <th>type</th>
            <td>String</td>
            <td>
                <p>The type of API object. The value is always "topic".</p>
                <pre>"type":"topic"</pre>
            </td>
        </tr>
        <tr>
            <th>id</th>
            <td>Integer</td>
            <td>
                <p>Internal ID for the topic.</p>
                <pre>"id":1</pre>
            </td>
        </tr>
        <tr>
            <th>board_id</th>
            <td>Integer</td>
            <td>
                <p>Internal ID of a board the topic is associated with.</p>
                <pre>"board_id":1</pre>
            </td>
        </tr>
        <tr>
            <th>bumped_at</th>
            <td>String</td>
            <td>
                <p><a href="http://en.wikipedia.org/wiki/ISO_8601">ISO 8601</a>-formatted datetime of when the topic was last bumped to top of the board.</p>
                <pre>"bumped_at":"2014-05-07T07:22:01.831981-07:00"</pre>
            </td>
        </tr>
        <tr>
            <th>created_at</th>
            <td>String</td>
            <td>
                <p><a href="http://en.wikipedia.org/wiki/ISO_8601">ISO 8601</a>-formatted datetime of when the topic was created.</p>
                <pre>"created_at":"2013-02-06T16:45:20.275693-08:00"</pre>
            </td>
        </tr>
        <tr>
            <th>post_count</th>
            <td>Integer</td>
            <td>
                <p>Number of posts in the topic.</p>
                <pre>"post_count":693</pre>
            </td>
        </tr>
        <tr>
            <th>posted_at</th>
            <td>String</td>
            <td>
                <p><a href="http://en.wikipedia.org/wiki/ISO_8601">ISO 8601</a>-formatted datetime of when a new post was made to the topic regardless of bump status.</p>
                <pre>"posted_at":"2014-05-07T07:52:27.700932-07:00"</pre>
            </td>
        </tr>
        <tr>
            <th>status</th>
            <td>String</td>
            <td>
                <p>Status string whether the topic is still active or not. Available values are:</p>
                <ul>
                    <li><strong>open</strong> — the topic is active and postable.</li>
                    <li><strong>locked</strong> — the topic has been locked by moderator and could not be posted.</li>
                    <li><strong>archived</strong> — the topic has been automatically archived and could not be posted.</li>
                </ul>
                <pre>"status":"open"</pre>
            </td>
        </tr>
        <tr>
            <th>title</th>
            <td>String</td>
            <td>
                <p>The title of the topic entered by the user in new topic form.</p>
                <pre>"title":"ยินดีต้อนรับเข้าสู่ Fanboi Channel 2.0"</pre>
            </td>
        </tr>
        <tr>
            <th>path</th>
            <td>String</td>
            <td>
                <p>The path to this resource.</p>
                <pre>"path":"/api/1.0/topics/1/"</pre>
            </td>
        </tr>
    </%def>
</%api:render_api>
