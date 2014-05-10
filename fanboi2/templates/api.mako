<%namespace name="formatters" module="fanboi2.formatters" />
<%inherit file="partials/_layout.mako" />
<header class="header header-boards">
    <div class="container">
        <p>API documentation.</p>
    </div>
</header>

<div class="item-api">
    <div class="container">
        <p class="alert">Fanboi2 API is currently under active development and may change at any time. Use it at your own risk!</p>

        <table id="api-boards" class="table-api">
            <tr>
                <th class="table-api-label">API name</th>
                <td class="table-api-details"><strong>api_boards</strong></td>
            </tr>
            <tr>
                <th class="table-api-label">Request</th>
                <td class="table-api-details"><code class="code">GET ${formatters.unquoted_path(request, 'api_boards')}</code></td>
            </tr>
            <tr>
                <th class="table-api-label">Response</th>
                <td class="table-api-details"><code class="code">Array</code> containing <a href="#api-board">api_board</a>.</td>
            </tr>
        </table>

        <table id="api-board" class="table-api">
            <tr>
                <th class="table-api-label">API name</th>
                <td class="table-api-details"><strong>api_board</strong></td>
            </tr>
            <tr>
                <th class="table-api-label">Request</th>
                <td class="table-api-details"><code class="code">GET ${formatters.unquoted_path(request, 'api_board', board='{api_board.slug}')}</code></td>
            </tr>
            <tr>
                <th class="table-api-label">Response</th>
                <td class="table-api-details">
                    <p><code class="code">Object</code> containing the fields as listed below. Unicode strings are escaped in actual response.</p>
                    <table class="table-api">
                        <tr>
                            <th>Field</th>
                            <th>Type</th>
                            <th>Description</th>
                        </tr>
                        <tr>
                            <th class="table-api-field">description</th>
                            <td class="table-api-type">String</td>
                            <td class="table-api-description">
                                <p>The description of the board.</p>
                                <pre class="code">"description":"บอร์ดอิสระสำหรับพูดคุยเรื่องใดก็ได้ที่หมวดที่มีอยู่ไม่ครอบคลุม"</pre>
                            </td>
                        </tr>
                        <tr>
                            <th class="table-api-field">title</th>
                            <td class="table-api-type">String</td>
                            <td class="table-api-description">
                                <p>The title of the board.</p>
                                <pre class="code">"title":"Lounge"</pre>
                            </td>
                        </tr>
                        <tr>
                            <th class="table-api-field">settings</th>
                            <td class="table-api-type">Object</td>
                            <td class="table-api-description">
                                <p>The settings for the board. Available options are:</p>
                                <ul>
                                    <li><strong>post_delay</strong> — <code class="code">Integer</code>, number of seconds user should wait before posting a new post.</li>
                                    <li><strong>use_ident</strong> — <code class="code">Boolean</code>, whether to generate ID for each post in the board.</li>
                                    <li><strong>name</strong> — <code class="code">name</code>, the default name for each post in case user did not provide a name.</li>
                                    <li><strong>max_posts</strong> — <code class="code">Integer</code>, number of maximum posts per each topic in the board.</li>
                                </ul>
                                <pre class="code">"settings":{<br>    "post_delay":10,<br>    "use_ident":true,<br>    "name":"Nameless Fanboi",<br>    "max_posts":1000<br>}</pre>
                            </td>
                        </tr>
                        <tr>
                            <th class="table-api-field">slug</th>
                            <td class="table-api-type">String</td>
                            <td class="table-api-description">
                                <p>The identity slug of the board.</p>
                                <pre class="code">"slug":"lounge"</pre>
                            </td>
                        </tr>
                        <tr>
                            <th class="table-api-field">agreements</th>
                            <td class="table-api-type">String</td>
                            <td class="table-api-description">
                                <p>A <a href="http://daringfireball.net/projects/markdown/">Markdown</a>-formatted agreements for using the board.</p>
                                <pre class="code">"agreements":"* ห้ามมีเนื้อหาเกี่ยวข้องกับการเมืองหรือสถาบันพระมหากษัตริย์โดยเด็ดขาด"</pre>
                            </td>
                        </tr>
                        <tr>
                            <th class="table-api-field">id</th>
                            <td class="table-api-type">Integer</td>
                            <td class="table-api-description">
                                <p>Internal ID for the board.</p>
                                <pre class="code">"id":1</pre>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>

        <table id="api-board-topics" class="table-api">
            <tr>
                <th class="table-api-label">API name</th>
                <td class="table-api-details"><strong>api_board_topics</strong></td>
            </tr>
            <tr>
                <th class="table-api-label">Request</th>
                <td class="table-api-details"><code class="code">GET ${formatters.unquoted_path(request, 'api_board_topics', board='{api_board.slug}')}</code></td>
            </tr>
            <tr>
                <th class="table-api-label">Response</th>
                <td class="table-api-details"><code class="code">Array</code> containing <a href="#api-topic">api_topic</a>.</td>
            </tr>
        </table>

        <table id="api-topic" class="table-api">
            <tr>
                <th class="table-api-label">API name</th>
                <td class="table-api-details"><strong>api_topic</strong></td>
            </tr>
            <tr>
                <th class="table-api-label">Request</th>
                <td class="table-api-details"><code class="code">GET ${formatters.unquoted_path(request, 'api_topic', topic='{api_topic.id}')}</code></td>
            </tr>
            <tr>
                <th class="table-api-label">Response</th>
                <td class="table-api-details">
                    <p><code class="code">Object</code> containing the fields as listed below. Unicode strings are escaped in actual response.</p>
                    <table class="table-api">
                        <tr>
                            <th>Field</th>
                            <th>Type</th>
                            <th>Description</th>
                        </tr>
                        <tr>
                            <th class="table-api-field">board_id</th>
                            <td class="table-api-type">Integer</td>
                            <td class="table-api-description">
                                <p>Internal ID of a board the topic is associated with.</p>
                                <pre class="code">"id":1</pre>
                            </td>
                        </tr>
                        <tr>
                            <th class="table-api-field">bumped_at</th>
                            <td class="table-api-type">String</td>
                            <td class="table-api-description">
                                <p><a href="http://en.wikipedia.org/wiki/ISO_8601">ISO 8601</a>-formatted datetime of when the topic was last bumped to top of the board.</p>
                                <pre class="code">"bumped_at":"2014-05-07T07:22:01.831981-07:00"</pre>
                            </td>
                        </tr>
                        <tr>
                            <th class="table-api-field">status</th>
                            <td class="table-api-type">String</td>
                            <td class="table-api-description">
                                <p>Status string whether the topic is still active or not. Available values are:</p>
                                <ul>
                                    <li><strong>open</strong> — the topic is active and postable.</li>
                                    <li><strong>locked</strong> — the topic has been locked by moderator and could not be posted.</li>
                                    <li><strong>archived</strong> — the topic has been automatically archived and could not be posted.</li>
                                </ul>
                                <pre class="code">"status":"open"</pre>
                            </td>
                        </tr>
                        <tr>
                            <th class="table-api-field">title</th>
                            <td class="table-api-type">String</td>
                            <td class="table-api-description">
                                <p>The title of the topic entered by the user in new topic form.</p>
                                <pre class="code">"title":"ยินดีต้อนรับเข้าสู่ Fanboi Channel 2.0"</pre>
                            </td>
                        </tr>
                        <tr>
                            <th class="table-api-field">post_count</th>
                            <td class="table-api-type">Integer</td>
                            <td class="table-api-description">
                                <p>Number of posts in the topic.</p>
                                <pre class="code">"post_count":693</pre>
                            </td>
                        </tr>
                        <tr>
                            <th class="table-api-field">created_at</th>
                            <td class="table-api-type">String</td>
                            <td class="table-api-description">
                                <p><a href="http://en.wikipedia.org/wiki/ISO_8601">ISO 8601</a>-formatted datetime of when the topic was created.</p>
                                <pre class="code">"created_at":"2013-02-06T16:45:20.275693-08:00"</pre>
                            </td>
                        </tr>
                        <tr>
                            <th class="table-api-field">posted_at</th>
                            <td class="table-api-type">String</td>
                            <td class="table-api-description">
                                <p><a href="http://en.wikipedia.org/wiki/ISO_8601">ISO 8601</a>-formatted datetime of when a new post was made to the topic regardless of bump status.</p>
                                <pre class="code">"posted_at":"2014-05-07T07:52:27.700932-07:00"</pre>
                            </td>
                        </tr>
                        <tr>
                            <th class="table-api-field">id</th>
                            <td class="table-api-type">Integer</td>
                            <td class="table-api-description">
                                <p>Internal ID for the topic.</p>
                                <pre class="code">"id":1</pre>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>

        <table id="api-topic-posts" class="table-api">
            <tr>
                <th class="table-api-label">API name</th>
                <td class="table-api-details"><strong>api_topic_posts</strong></td>
            </tr>
            <tr>
                <th class="table-api-label">Request</th>
                <td class="table-api-details"><code class="code">GET ${formatters.unquoted_path(request, 'api_topic_posts', topic='{api_topic.id}')}</code></td>
            </tr>
            <tr>
                <th class="table-api-label">Response</th>
                <td class="table-api-details">
                    <p><code class="code">Array</code> containing <code class="code">Object</code> of the below fields. Unicode strings are escaped in actual response.</p>
                    <table class="table-api">
                        <tr>
                            <th>Field</th>
                            <th>Type</th>
                            <th>Description</th>
                        </tr>
                        <tr>
                            <th class="table-api-field">body</th>
                            <td class="table-api-type">String</td>
                            <td class="table-api-description">
                                <p>The post body entered by the user in new topic or reply form.</p>
                                <pre class="code">"body":"..."</pre>
                            </td>
                        </tr>
                        <tr>
                            <th class="table-api-field">bumped</th>
                            <td class="table-api-type">Boolean</td>
                            <td class="table-api-description">
                                <p>Boolean flag whether the post bumped the topic to top of the board.</p>
                                <pre class="code">"bumped":true</pre>
                            </td>
                        </tr>
                        <tr>
                            <th class="table-api-field">body_formatted</th>
                            <td class="table-api-type">String</td>
                            <td class="table-api-description">
                                <p>Same as <strong>body</strong> but format it to HTML using internal formatter.</p>
                                <pre class="code">"body_formatted":"&lt;p&gt;...&lt;/p&gt;"</pre>
                            </td>
                        </tr>
                        <tr>
                            <th class="table-api-field">name</th>
                            <td class="table-api-type">String</td>
                            <td class="table-api-description">
                                <p>The name entered for this post.</p>
                                <pre class="code">"name":"Nameless Fanboi"</pre>
                            </td>
                        </tr>
                        <tr>
                            <th class="table-api-field">topic_id</th>
                            <td class="table-api-type">Integer</td>
                            <td class="table-api-description">
                                <p>Internal ID of a topic the post is associated with.</p>
                                <pre class="code">"topic_id":1</pre>
                            </td>
                        </tr>
                        <tr>
                            <th class="table-api-field">created_at</th>
                            <td class="table-api-type">String</td>
                            <td class="table-api-description">
                                <p><a href="http://en.wikipedia.org/wiki/ISO_8601">ISO 8601</a>-formatted datetime of when the post was created.</p>
                                <pre class="code">"created_at":"2013-02-06T16:45:20.275693-08:00"</pre>
                            </td>
                        </tr>
                        <tr>
                            <th class="table-api-field">ident</th>
                            <td class="table-api-type">String</td>
                            <td class="table-api-description">
                                <p>Unique ID for each user that was generated when the board has <strong>use_ident</strong> enabled.</p>
                                <pre class="code">"ident":"7xFKuAP5G"</pre>
                            </td>
                        </tr>
                        <tr>
                            <th class="table-api-field">id</th>
                            <td class="table-api-type">Integer</td>
                            <td class="table-api-description">
                                <p>Internal ID for the post.</p>
                                <pre class="code">"id":1</pre>
                            </td>
                        </tr>
                        <tr>
                            <th class="table-api-field">number</th>
                            <td class="table-api-type">Integer</td>
                            <td class="table-api-description">
                                <p>Order of the post within the topic.</p>
                                <pre class="code">"number":1</pre>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>

        <table id="api-topic-posts-scoped" class="table-api">
            <tr>
                <th class="table-api-label">API name</th>
                <td class="table-api-details"><strong>api_topic_posts_scoped</strong></td>
            </tr>
            <tr>
                <th class="table-api-label">Request</th>
                <td class="table-api-details">
                    <p><code class="code">GET ${formatters.unquoted_path(request, 'api_topic_posts_scoped', topic='{api_topic.id}', query='{query}')}</code></p>
                    <p>The query could be one of the following:</p>
                    <table class="table-api">
                        <tr>
                            <th class="table-api-query">Query</th>
                            <th class="table-api-description">Description</th>
                        </tr>
                        <tr>
                            <th class="table-api-query">{n}</th>
                            <td class="table-api-description">Query a single post with <em>n</em> number.</td>
                        </tr>
                        <tr>
                            <th class="table-api-query">{n1}-{n2}</th>
                            <td class="table-api-description">Query posts from <em>n1</em> to <em>n2</em>. If <em>n1</em> or <em>n2</em> is not given, 0 and last post are assumed respectively.</td>
                        </tr>
                        <tr>
                            <th class="table-api-query">l{n}</th>
                            <td class="table-api-description">Query the last <em>n</em> posts, for example, <strong>l10</strong> will list the last 10 posts.</td>
                        </tr>
                        <tr>
                            <th class="table-api-query">recent</th>
                            <td class="table-api-description">Alias for <strong>l30</strong>.</td>
                        </tr>
                    </table>
                </td>
            </tr>
            <tr>
                <th class="table-api-label">Response</th>
                <td class="table-api-details">Same as <a href="#api-topic-posts">api_topic_posts</a>.</td>
            </tr>
        </table>
    </div>
</div>
