<%namespace name="formatters" module="fanboi2.helpers.formatters" />
<%namespace name="api" file="../partials/_api.mako" />
<%api:render_api name="api-boards" title="Retrieving boards" method="GET">
    <%def name="path()">
        ${formatters.unquoted_path(request, 'api_boards')}
    </%def>
    <%def name="description()">
        <p>Use this endpoint to retrieve a list of boards. The data retrieved from this endpoint is rarely updated and should be safe to cache. It is possible to include recent topics and its recent posts with <em>query strings</em> (see also <a href="#api-board">#api-board</a> and <a href="#api-topic">#api-topic</a>), doing so with this API is not recommended as it will put extra loads on the server.</p>
    </%def>
    <%def name="response_body()">
        <p><code>Array</code> containing <a href="#api-board">#api-board</a>.</p>
    </%def>
</%api:render_api>
<%api:render_api name="api-board" title="Retrieving a board" method="GET">
    <%def name="path()">
        ${formatters.unquoted_path(request, 'api_board', board='{api-board.slug}')}
    </%def>
    <%def name="description()">
        <p>Use this endpoint to retrieve any individual board. By default this endpoint will not include <em>topics</em> and <em>recent posts</em> in the response. It is possible to instruct the API to include those data with <em>query strings</em> listed below. Passing both <code>?topics=1&posts=1</code> will make the API effectively returning the same data as board's "Recent topics" page.</p>
    </%def>
    <%def name="request_query()">
        <tr>
            <th>?topics=1</th>
            <td>Include the recent 10 topics in a <code>topics</code> object.</td>
        </tr>
        <tr>
            <th>?posts=1</th>
            <td>Include the recent 30 posts in a <code>posts</code> object. Only if <code>topics</code> is present.</td>
        </tr>
    </%def>
    <%def name="response_body()">
        <p><code>Object</code> containing the fields as listed below. Unicode strings are escaped in actual response.</p>
    </%def>
    <%def name="response_object()">
        <tr>
            <th>type</th>
            <td>String</td>
            <td>
                <p>The type of API object. The value is always "board".</p>
                <pre>"type":"board"</pre>
            </td>
        </tr>
        <tr>
            <th>id</th>
            <td>Integer</td>
            <td>
                <p>Internal ID for the board.</p>
                <pre>"id":1</pre>
            </td>
        </tr>
        <tr>
            <th>agreements</th>
            <td>String</td>
            <td>
                <p>A <a href="http://daringfireball.net/projects/markdown/">Markdown</a>-formatted agreements for using the board.</p>
                <pre>"agreements":"* ห้ามมีเนื้อหาเกี่ยวข้องกับการเมืองหรือสถาบันพระมหากษัตริย์โดยเด็ดขาด"</pre>
            </td>
        </tr>
        <tr>
            <th>description</th>
            <td>String</td>
            <td>
                <p>The description of the board.</p>
                <pre>"description":"บอร์ดอิสระสำหรับพูดคุยเรื่องใดก็ได้ที่หมวดที่มีอยู่ไม่ครอบคลุม"</pre>
            </td>
        </tr>
        <tr>
            <th>settings</th>
            <td>Object</td>
            <td>
                <p>The settings for the board. Available options are:</p>
                <ul>
                    <li><strong>post_delay</strong> — <code>Integer</code>, number of seconds user should wait before posting a new post.</li>
                    <li><strong>use_ident</strong> — <code>Boolean</code>, whether to generate ID for each post in the board.</li>
                    <li><strong>name</strong> — <code>String</code>, the default name for each post in case user did not provide a name.</li>
                    <li><strong>max_posts</strong> — <code>Integer</code>, number of maximum posts per each topic in the board.</li>
                </ul>
                <pre>"settings":{<br>    "post_delay":10,<br>    "use_ident":true,<br>    "name":"Nameless Fanboi",<br>    "max_posts":1000<br>}</pre>
            </td>
        </tr>
        <tr>
            <th>slug</th>
            <td>String</td>
            <td>
                <p>The identity slug of the board.</p>
                <pre>"slug":"lounge"</pre>
            </td>
        </tr>
        <tr>
            <th>status</th>
            <td>String</td>
            <td>
                <p>Status string whether the board is still active or not. Available values are:</p>
                <ul>
                    <li><strong>open</strong> — the board is postable.</li>
                    <li><strong>restricted</strong> — the board is postable but no new topics can be made.</li>
                    <li><strong>locked</strong> — the board could not be posted.</li>
                    <li><strong>archived</strong> — the board could not be posted and is no longer listed in board list.</li>
                </ul>
                <pre>"status":"open"</pre>
            </td>
        </tr>
        <tr>
            <th>title</th>
            <td>String</td>
            <td>
                <p>The title of the board.</p>
                <pre>"title":"Lounge"</pre>
            </td>
        </tr>
        <tr>
            <th>path</th>
            <td>String</td>
            <td>
                <p>The path to this resource.</p>
                <pre>"path":"/api/1.0/boards/lounge/"</pre>
            </td>
        </tr>
    </%def>
</%api:render_api>
