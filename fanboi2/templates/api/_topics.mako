<%namespace name='formatters' module='fanboi2.formatters' />
<div class="sheet">
    <div class="container">
        <h2 class="sheet-title">Topics</h2>
        <div class="sheet-body">
            <table class="api-table table" id="api-board-topics">
                <tbody class="table-group">
                    <tr class="table-row">
                        <th class="table-row-header">Name</th>
                        <td class="table-row-item"><strong>api_board_topics</strong></td>
                    </tr>
                    <tr class="table-row">
                        <th class="table-row-header">Request</th>
                        <td class="table-row-item"><code>GET ${formatters.unquoted_path(request, 'api_board_topics', board='{api_board.slug}')}</code></td>
                    </tr>
                    <tr class="table-row">
                        <th class="table-row-header">Response</th>
                        <td class="table-row-item"><code>Array</code> containing <a href="#api-topic">api_topic</a>.</td>
                    </tr>
                </tbody>
            </table>

            <table class="api-table table" id="api-topic">
                <tbody class="table-group">
                    <tr class="table-row">
                        <th class="table-row-header">Name</th>
                        <td class="table-row-item"><strong>api_topic</strong></td>
                    </tr>
                    <tr class="table-row">
                        <th class="table-row-header">Request</th>
                        <td class="table-row-item"><code>GET ${formatters.unquoted_path(request, 'api_topic', topic='{api_topic.id}')}</code></td>
                    </tr>
                    <tr class="table-row">
                        <th class="table-row-header">Response</th>
                        <td class="table-row-item">
                            <p><code>Object</code> containing the fields as listed below. Unicode strings are escaped in actual response.</p>
                            <table class="api-table table inner">
                                <thead class="table-group header">
                                    <tr class="table-row">
                                        <th class="table-row-header">Field</th>
                                        <th class="table-row-header type">Type</th>
                                        <th class="table-row-header">Description</th>
                                    </tr>
                                </thead>
                                <tbody class="table-group">
                                    <tr class="table-row">
                                        <th class="table-row-header">board_id</th>
                                        <td class="table-row-item type">Integer</td>
                                        <td class="table-row-item">
                                            <p>Internal ID of a board the topic is associated with.</p>
                                            <pre class="codeblock">"id":1</pre>
                                        </td>
                                    </tr>
                                    <tr class="table-row">
                                        <th class="table-row-header">bumped_at</th>
                                        <td class="table-row-item type">String</td>
                                        <td class="table-row-item">
                                            <p><a href="http://en.wikipedia.org/wiki/ISO_8601">ISO 8601</a>-formatted datetime of when the topic was last bumped to top of the board.</p>
                                            <pre class="codeblock">"bumped_at":"2014-05-07T07:22:01.831981-07:00"</pre>
                                        </td>
                                    </tr>
                                    <tr class="table-row">
                                        <th class="table-row-header">status</th>
                                        <td class="table-row-item type">String</td>
                                        <td class="table-row-item">
                                            <p>Status string whether the topic is still active or not. Available values are:</p>
                                            <ul>
                                                <li><strong>open</strong> — the topic is active and postable.</li>
                                                <li><strong>locked</strong> — the topic has been locked by moderator and could not be posted.</li>
                                                <li><strong>archived</strong> — the topic has been automatically archived and could not be posted.</li>
                                            </ul>
                                            <pre class="codeblock">"status":"open"</pre>
                                        </td>
                                    </tr>
                                    <tr class="table-row">
                                        <th class="table-row-header">title</th>
                                        <td class="table-row-item type">String</td>
                                        <td class="table-row-item">
                                            <p>The title of the topic entered by the user in new topic form.</p>
                                            <pre class="codeblock">"title":"ยินดีต้อนรับเข้าสู่ Fanboi Channel 2.0"</pre>
                                        </td>
                                    </tr>
                                    <tr class="table-row">
                                        <th class="table-row-header">post_count</th>
                                        <td class="table-row-item type">Integer</td>
                                        <td class="table-row-item">
                                            <p>Number of posts in the topic.</p>
                                            <pre class="codeblock">"post_count":693</pre>
                                        </td>
                                    </tr>
                                    <tr class="table-row">
                                        <th class="table-row-header">created_at</th>
                                        <td class="table-row-item type">String</td>
                                        <td class="table-row-item">
                                            <p><a href="http://en.wikipedia.org/wiki/ISO_8601">ISO 8601</a>-formatted datetime of when the topic was created.</p>
                                            <pre class="codeblock">"created_at":"2013-02-06T16:45:20.275693-08:00"</pre>
                                        </td>
                                    </tr>
                                    <tr class="table-row">
                                        <th class="table-row-header">posted_at</th>
                                        <td class="table-row-item type">String</td>
                                        <td class="table-row-item">
                                            <p><a href="http://en.wikipedia.org/wiki/ISO_8601">ISO 8601</a>-formatted datetime of when a new post was made to the topic regardless of bump status.</p>
                                            <pre class="codeblock">"posted_at":"2014-05-07T07:52:27.700932-07:00"</pre>
                                        </td>
                                    </tr>
                                    <tr class="table-row">
                                        <th class="table-row-header">id</th>
                                        <td class="table-row-item type">Integer</td>
                                        <td class="table-row-item">
                                            <p>Internal ID for the topic.</p>
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
