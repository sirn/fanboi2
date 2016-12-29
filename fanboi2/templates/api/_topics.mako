<%namespace name='formatters' module='fanboi2.helpers.formatters' />
<div class="api-section" id="api-board-topics-new">
    <div class="api-request">
        <div class="container">
            <h2 class="api-request-title">Creating new topic in a board <span class="api-request-name">#api-board-topics-new</span></h2>
            <div class="api-request-endpoint"><span class="api-request-verb verb-post">POST</span> ${formatters.unquoted_path(request, 'api_board_topics', board='{api-board.slug}')}</div>
            <div class="api-request-body">
                <p>Use this endpoint to create a new topic in a specific board. Please note that this API will <em>enqueue</em> the topic with the global posting queue and will not guarantee that the topic will be successfully posted. To retrieve the status of topic creation, please see <a href="#api-task">#api-task</a>.</p>
                <table class="api-table">
                    <thead class="api-table-header">
                        <tr class="api-table-row">
                            <th class="api-table-item title">Parameters</th>
                            <th class="api-table-item title">Type</th>
                            <th class="api-table-item title">Description</th>
                        </tr>
                    </thead>
                    <tbody class="api-table-body">
                        <tr class="api-table-row">
                            <th class="api-table-item title">title</th>
                            <th class="api-table-item type">String</th>
                            <td class="api-table-item">Title of the topic. From 5 to 200 characters.</td>
                        </tr>
                        <tr class="api-table-row">
                            <th class="api-table-item title">body</th>
                            <th class="api-table-item type">String</th>
                            <td class="api-table-item">Content of the topic. From 2 to 4,000 characters.</td>
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

<div class="api-section" id="api-board-topics">
    <div class="api-request">
        <div class="container">
            <h2 class="api-request-title">Retrieving topics associated to a board <span class="api-request-name">#api-board-topics</span></h2>
            <div class="api-request-endpoint"><span class="api-request-verb verb-get">GET</span> ${formatters.unquoted_path(request, 'api_board_topics', board='{api-board.slug}')}</div>
            <div class="api-request-body">
                <p>Use this endpoint to retrieve a list of topics associated to the specific board. By default this API will return the same data as board's "All topics" page which includes open topic and topic that are closed (locked and archived) within 1 week of last posted date. It is also possible to include recent posts with <em>query string</em> but doing so with this API is not recommended.</p>
                <table class="api-table">
                    <thead class="api-table-header">
                        <tr class="api-table-row">
                            <th class="api-table-item title">Query string</th>
                            <th class="api-table-item title">Description</th>
                        </tr>
                    </thead>
                    <tbody class="api-table-body">
                        <tr class="api-table-row">
                            <th class="api-table-item title">?posts=1</th>
                            <td class="api-table-item">Include the recent 30 posts in a <code>posts</code> object.</td>
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
                <p><code>Array</code> containing <a href="#api-topic">#api-topic</a>.</p>
            </div>
        </div>
    </div>
</div>

<div class="api-section" id="api-topic">
    <div class="api-request">
        <div class="container">
            <h2 class="api-request-title">Retrieving a topic <span class="api-request-name">#api-topic</span></h2>
            <div class="api-request-endpoint"><span class="api-request-verb verb-get">GET</span> ${formatters.unquoted_path(request, 'api_topic', topic='{api-topic.id}')}</div>
            <div class="api-request-body">
                <p>Use this endpoint to retrieve any individual topic. This endpoint by default will not include any posts but it is possible to instruct the API to include them using <em>query string</em>. Posts retrieved as part of this API is limited to the recent 30 posts. For retrieving a full list of posts, see <a href="#api-topic-posts">#api-topic-posts</a> and <a href="#api-topic-posts-scoped">#api-topic-posts-scoped</a>.</p>
                <table class="api-table">
                    <thead class="api-table-header">
                        <tr class="api-table-row">
                            <th class="api-table-item title">Query string</th>
                            <th class="api-table-item title">Description</th>
                        </tr>
                    </thead>
                    <tbody class="api-table-body">
                        <tr class="api-table-row">
                            <th class="api-table-item title">?posts=1</th>
                            <td class="api-table-item">Include the recent 30 posts in a <code>posts</code> object.</td>
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
                                <p>The type of API object. The value is always "topic".</p>
                                <pre class="codeblock">"type":"topic"</pre>
                            </td>
                        </tr>
                        <tr class="api-table-row">
                            <th class="api-table-item title">id</th>
                            <td class="api-table-item type">Integer</td>
                            <td class="api-table-item">
                                <p>Internal ID for the topic.</p>
                                <pre class="codeblock">"id":1</pre>
                            </td>
                        </tr>
                        <tr class="api-table-row">
                            <th class="api-table-item title">board_id</th>
                            <td class="api-table-item type">Integer</td>
                            <td class="api-table-item">
                                <p>Internal ID of a board the topic is associated with.</p>
                                <pre class="codeblock">"board_id":1</pre>
                            </td>
                        </tr>
                        <tr class="api-table-row">
                            <th class="api-table-item title">bumped_at</th>
                            <td class="api-table-item type">String</td>
                            <td class="api-table-item">
                                <p><a href="http://en.wikipedia.org/wiki/ISO_8601">ISO 8601</a>-formatted datetime of when the topic was last bumped to top of the board.</p>
                                <pre class="codeblock">"bumped_at":"2014-05-07T07:22:01.831981-07:00"</pre>
                            </td>
                        </tr>
                        <tr class="api-table-row">
                            <th class="api-table-item title">created_at</th>
                            <td class="api-table-item type">String</td>
                            <td class="api-table-item">
                                <p><a href="http://en.wikipedia.org/wiki/ISO_8601">ISO 8601</a>-formatted datetime of when the topic was created.</p>
                                <pre class="codeblock">"created_at":"2013-02-06T16:45:20.275693-08:00"</pre>
                            </td>
                        </tr>
                        <tr class="api-table-row">
                            <th class="api-table-item title">post_count</th>
                            <td class="api-table-item type">Integer</td>
                            <td class="api-table-item">
                                <p>Number of posts in the topic.</p>
                                <pre class="codeblock">"post_count":693</pre>
                            </td>
                        </tr>
                        <tr class="api-table-row">
                            <th class="api-table-item title">posted_at</th>
                            <td class="api-table-item type">String</td>
                            <td class="api-table-item">
                                <p><a href="http://en.wikipedia.org/wiki/ISO_8601">ISO 8601</a>-formatted datetime of when a new post was made to the topic regardless of bump status.</p>
                                <pre class="codeblock">"posted_at":"2014-05-07T07:52:27.700932-07:00"</pre>
                            </td>
                        </tr>
                        <tr class="api-table-row">
                            <th class="api-table-item title">status</th>
                            <td class="api-table-item type">String</td>
                            <td class="api-table-item">
                                <p>Status string whether the topic is still active or not. Available values are:</p>
                                <ul>
                                    <li><strong>open</strong> — the topic is active and postable.</li>
                                    <li><strong>locked</strong> — the topic has been locked by moderator and could not be posted.</li>
                                    <li><strong>archived</strong> — the topic has been automatically archived and could not be posted.</li>
                                </ul>
                                <pre class="codeblock">"status":"open"</pre>
                            </td>
                        </tr>
                        <tr class="api-table-row">
                            <th class="api-table-item title">title</th>
                            <td class="api-table-item type">String</td>
                            <td class="api-table-item">
                                <p>The title of the topic entered by the user in new topic form.</p>
                                <pre class="codeblock">"title":"ยินดีต้อนรับเข้าสู่ Fanboi Channel 2.0"</pre>
                            </td>
                        </tr>
                        <tr class="api-table-row">
                            <th class="api-table-item title">path</th>
                            <td class="api-table-item type">String</td>
                            <td class="api-table-item">
                                <p>The path to this resource.</p>
                                <pre class="codeblock">"path":"/api/1.0/topics/1/"</pre>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</div>
