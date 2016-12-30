<%namespace name='formatters' module='fanboi2.helpers.formatters' />
<div class="api-section" id="api-boards">
    <div class="api-request">
        <div class="container">
            <h2 class="api-request-title">Retrieving boards <span class="api-request-name">#api-boards</span></h2>
            <div class="api-request-endpoint"><span class="api-request-verb verb-get">GET</span> ${formatters.unquoted_path(request, 'api_boards')}</div>
            <div class="api-request-body">
                <p>Use this endpoint to retrieve a list of boards. The data retrieved from this endpoint is rarely updated and should be safe to cache. It is possible to include recent topics and its recent posts with <em>query strings</em> (see also <a href="#api-board">#api-board</a> and <a href="#api-topic">#api-topic</a>), doing so with this API is not recommended as it will put extra loads on the server.</p>
            </div>
        </div>
    </div>
    <div class="api-response">
        <div class="container">
            <h3 class="api-response-title">Response</h3>
            <div class="api-response-body">
                <p><code>Array</code> containing <a href="#api-board">#api-board</a>.</p>
            </div>
        </div>
    </div>
</div>

<div class="api-section" id="api-board">
    <div class="api-request">
        <div class="container">
            <h2 class="api-request-title">Retrieving a board <span class="api-request-name">#api-board</span></h2>
            <div class="api-request-endpoint"><span class="api-request-verb verb-get">GET</span> ${formatters.unquoted_path(request, 'api_board', board='{api-board.slug}')}</div>
            <div class="api-request-body">
                <p>Use this endpoint to retrieve any individual board. By default this endpoint will not include <em>topics</em> and <em>recent posts</em> in the response. It is possible to instruct the API to include those data with <em>query strings</em> listed below. Passing both <code>?topics=1&posts=1</code> will make the API effectively returning the same data as board's "Recent topics" page.</p>
                <table class="api-table">
                    <thead class="api-table-header">
                        <tr class="api-table-row">
                            <th class="api-table-item title">Query string</th>
                            <th class="api-table-item title">Description</th>
                        </tr>
                    </thead>
                    <tbody class="api-table-body">
                        <tr class="api-table-row">
                            <th class="api-table-item title">?topics=1</th>
                            <td class="api-table-item">Include the recent 10 topics in a <code>topics</code> object.</td>
                        </tr>
                        <tr class="api-table-row">
                            <th class="api-table-item title">?posts=1</th>
                            <td class="api-table-item">Include the recent 30 posts in a <code>posts</code> object. Only if <code>topics</code> is present.</td>
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
                <p><code>Object</code> containing the fields as listed below. Unicode strings are escaped in actual response.</p>
                <table class="api-table">
                    <thead class="api-table-header">
                        <tr class="api-table-row">
                            <th class="api-table-item title">Field</th>
                            <th class="api-table-item title">Type</th>
                            <th class="api-table-item title">Description</th>
                        </tr>
                    </thead>
                    <tbody class="api-table-body">
                        <tr class="api-table-row">
                            <th class="api-table-item title">type</th>
                            <td class="api-table-item type">String</td>
                            <td class="api-table-item">
                                <p>The type of API object. The value is always "board".</p>
                                <pre class="codeblock">"type":"board"</pre>
                            </td>
                        </tr>
                        <tr class="api-table-row">
                            <th class="api-table-item title">id</th>
                            <td class="api-table-item type">Integer</td>
                            <td class="api-table-item">
                                <p>Internal ID for the board.</p>
                                <pre class="codeblock">"id":1</pre>
                            </td>
                        </tr>
                        <tr class="api-table-row">
                            <th class="api-table-item title">agreements</th>
                            <td class="api-table-item type">String</td>
                            <td class="api-table-item">
                                <p>A <a href="http://daringfireball.net/projects/markdown/">Markdown</a>-formatted agreements for using the board.</p>
                                <pre class="codeblock">"agreements":"* ห้ามมีเนื้อหาเกี่ยวข้องกับการเมืองหรือสถาบันพระมหากษัตริย์โดยเด็ดขาด"</pre>
                            </td>
                        </tr>
                        <tr class="api-table-row">
                            <th class="api-table-item title">description</th>
                            <td class="api-table-item type">String</td>
                            <td class="api-table-item">
                                <p>The description of the board.</p>
                                <pre class="codeblock">"description":"บอร์ดอิสระสำหรับพูดคุยเรื่องใดก็ได้ที่หมวดที่มีอยู่ไม่ครอบคลุม"</pre>
                            </td>
                        </tr>
                        <tr class="api-table-row">
                            <th class="api-table-item title">settings</th>
                            <td class="api-table-item type">Object</td>
                            <td class="api-table-item">
                                <p>The settings for the board. Available options are:</p>
                                <ul>
                                    <li><strong>post_delay</strong> — <code>Integer</code>, number of seconds user should wait before posting a new post.</li>
                                    <li><strong>use_ident</strong> — <code>Boolean</code>, whether to generate ID for each post in the board.</li>
                                    <li><strong>name</strong> — <code>String</code>, the default name for each post in case user did not provide a name.</li>
                                    <li><strong>max_posts</strong> — <code>Integer</code>, number of maximum posts per each topic in the board.</li>
                                </ul>
                                <pre class="codeblock">"settings":{<br>    "post_delay":10,<br>    "use_ident":true,<br>    "name":"Nameless Fanboi",<br>    "max_posts":1000<br>}</pre>
                            </td>
                        </tr>
                        <tr class="api-table-row">
                            <th class="api-table-item title">slug</th>
                            <td class="api-table-item type">String</td>
                            <td class="api-table-item">
                                <p>The identity slug of the board.</p>
                                <pre class="codeblock">"slug":"lounge"</pre>
                            </td>
                        </tr>
                        <tr class="api-table-row">
                            <th class="api-table-item title">status</th>
                            <td class="api-table-item type">String</td>
                            <td class="api-table-item">
                                <p>Status string whether the board is still active or not. Available values are:</p>
                                <ul>
                                    <li><strong>open</strong> — the board is postable.</li>
                                    <li><strong>restricted</strong> — the board is postable but no new topics can be made.</li>
                                    <li><strong>locked</strong> — the board could not be posted.</li>
                                    <li><strong>archived</strong> — the board could not be posted and is no longer listed in board list.</li>
                                </ul>
                                <pre class="codeblock">"status":"open"</pre>
                            </td>
                        </tr>
                        <tr class="api-table-row">
                            <th class="api-table-item title">title</th>
                            <td class="api-table-item type">String</td>
                            <td class="api-table-item">
                                <p>The title of the board.</p>
                                <pre class="codeblock">"title":"Lounge"</pre>
                            </td>
                        </tr>
                        <tr class="api-table-row">
                            <th class="api-table-item title">path</th>
                            <td class="api-table-item type">String</td>
                            <td class="api-table-item">
                                <p>The path to this resource.</p>
                                <pre class="codeblock">"path":"/api/1.0/boards/lounge/"</pre>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</div>
