<%namespace name='formatters' module='fanboi2.formatters' />
<div class="sheet">
    <div class="container">
        <h2 class="sheet-title">Boards</h2>
        <div class="sheet-body">
            <table class="api-table table" id="api-boards">
                <tbody class="api-table-body table-group">
                    <tr class="table-row">
                        <th class="table-row-header">Name</th>
                        <td class="table-row-item"><strong>api_boards</strong></td>
                    </tr>
                    <tr class="table-row">
                        <th class="table-row-header">Request</th>
                        <td class="table-row-item"><code>GET ${formatters.unquoted_path(request, 'api_boards')}</code></td>
                    </tr>
                    <tr class="table-row">
                        <th class="table-row-header">Response</th>
                        <td class="table-row-item"><code>Array</code> containing <a href="#api-board">api_board</a>.</td>
                    </tr>
                </tbody>
            </table>

            <table class="api-table table" id="api-board">
                <tbody class="api-table-body table-group">
                    <tr class="table-row">
                        <th class="table-row-header">Name</th>
                        <td class="table-row-item"><strong>api_board</strong></td>
                    </tr>
                    <tr class="table-row">
                        <th class="table-row-header">Request</th>
                        <td class="table-row-item"><code>GET ${formatters.unquoted_path(request, 'api_board', board='{api_board.slug}')}</code></td>
                    </tr>
                    <tr class="table-row">
                        <th class="table-row-header">Response</th>
                        <td class="table-row-item">
                            <p><code>Object</code> containing the fields as listed below. Unicode strings are escaped in actual response.</p>
                            <table class="api-table table inner">
                                <thead class="api-table-header table-group">
                                    <tr class="table-row">
                                        <th class="table-row-header">Field</th>
                                        <th class="table-row-header">Type</th>
                                        <th class="table-row-header">Description</th>
                                    </tr>
                                </thead>
                                <tbody class="api-table-body table-group">
                                    <tr class="table-row">
                                        <th class="table-row-header">description</th>
                                        <td class="api-table-row-type table-row-item">String</td>
                                        <td class="table-row-item">
                                            <p>The description of the board.</p>
                                            <pre class="codeblock">"description":"บอร์ดอิสระสำหรับพูดคุยเรื่องใดก็ได้ที่หมวดที่มีอยู่ไม่ครอบคลุม"</pre>
                                        </td>
                                    </tr>
                                    <tr class="table-row">
                                        <th class="table-row-header">title</th>
                                        <td class="api-table-row-type table-row-item">String</td>
                                        <td class="table-row-item">
                                            <p>The title of the board.</p>
                                            <pre class="codeblock">"title":"Lounge"</pre>
                                        </td>
                                    </tr>
                                    <tr class="table-row">
                                        <th class="table-row-header">settings</th>
                                        <td class="api-table-row-type table-row-item">Object</td>
                                        <td class="table-row-item">
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
                                    <tr class="table-row">
                                        <th class="table-row-header">slug</th>
                                        <td class="api-table-row-type table-row-item">String</td>
                                        <td class="table-row-item">
                                            <p>The identity slug of the board.</p>
                                            <pre class="codeblock">"slug":"lounge"</pre>
                                        </td>
                                    </tr>
                                    <tr class="table-row">
                                        <th class="table-row-header">agreements</th>
                                        <td class="api-table-row-type table-row-item">String</td>
                                        <td class="table-row-item">
                                            <p>A <a href="http://daringfireball.net/projects/markdown/">Markdown</a>-formatted agreements for using the board.</p>
                                            <pre class="codeblock">"agreements":"* ห้ามมีเนื้อหาเกี่ยวข้องกับการเมืองหรือสถาบันพระมหากษัตริย์โดยเด็ดขาด"</pre>
                                        </td>
                                    </tr>
                                    <tr class="table-row">
                                        <th class="table-row-header">id</th>
                                        <td class="api-table-row-type table-row-item">Integer</td>
                                        <td class="table-row-item">
                                            <p>Internal ID for the board.</p>
                                            <pre class="codeblock">"id":1</pre>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</div>
