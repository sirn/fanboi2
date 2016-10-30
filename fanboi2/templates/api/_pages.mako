<%namespace name='formatters' module='fanboi2.helpers.formatters' />
<div class="api-section" id="api-pages">
    <div class="api-request">
        <div class="container">
            <h2 class="api-request-title">Retrieving pages <span class="api-request-name">#api-pages</span></h2>
            <div class="api-request-endpoint"><span class="api-request-verb verb-get">GET</span> ${formatters.unquoted_path(request, 'api_pages')}</div>
            <div class="api-request-body">
                <p>Use this endpoint to retrieve a list of all pages. Usually these pages will contain static content, such as guidelines or help.
            </div>
        </div>
    </div>
    <div class="api-response">
        <div class="container">
            <h3 class="api-response-title">Response</h3>
            <div class="api-response-body">
                <p><code>Array</code> containing <a href="#api-page">#api-page</a>.</p>
            </div>
        </div>
    </div>
</div>

<div class="api-section" id="api-page">
    <div class="api-request">
        <div class="container">
            <h2 class="api-request-title">Retrieving a page <span class="api-request-name">#api-page</span></h2>
            <div class="api-request-endpoint"><span class="api-request-verb verb-get">GET</span> ${formatters.unquoted_path(request, 'api_page', page='{api-page.slug}')}</div>
            <div class="api-request-body">
                <p>Use this endpoint to retrieve any individual page.</p>
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
                                <p>The type of API object. The value is always "page".</p>
                                <pre class="codeblock">"type":"page"</pre>
                            </td>
                        </tr>
                        <tr class="api-table-row">
                            <th class="api-table-item title">id</th>
                            <td class="api-table-item type">Integer</td>
                            <td class="api-table-item">
                                <p>Internal ID for the page.</p>
                                <pre class="codeblock">"id":1</pre>
                            </td>
                        </tr>
                        <tr class="api-table-row">
                            <th class="api-table-item title">body</th>
                            <td class="api-table-item type">String</td>
                            <td class="api-table-item">
                                <p>The page body.</p>
                                <pre class="codeblock">"body":"..."</pre>
                            </td>
                        </tr>
                        <tr class="api-table-row">
                            <th class="api-table-item title">body_formatted</th>
                            <td class="api-table-item type">String</td>
                            <td class="api-table-item">
                                <p>Same as <strong>body</strong> but format it using specified <strong>formatter</strong>. Note that this field is meant to be rendered in a HTML viewer and will escape the body in case the formatter is "none". If the content will not be displayed in a HTML viewer in case the formatter is "none", <strong>body</strong> must be used instead.</p>
                                <pre class="codeblock">"body_formatted":"&lt;p&gt;&lt;em&gt;Hello, world&lt;/em&gt;&lt;/p&gt;\n"</pre>
                            </td>
                        </tr>
                        <tr class="api-table-row">
                            <th class="api-table-item title">formatter</th>
                            <td class="api-table-item type">String</td>
                            <td class="api-table-item">
                                <p>Name of a formatter to format this page's body. Available values are:</p>
                                <ul>
                                    <li><strong>markdown</strong> — render this page using Markdown formatter (see also <a href="http://misaka.61924.nl/">Misaka</a>).</li>
                                    <li><strong>html</strong> — render this page as HTML without any escaping.</li>
                                    <li><strong>none</strong> — render this page as text or escape HTML as appropriate.</li>
                                </ul>
                                <pre class="codeblock">"formatter":"markdown"</pre>
                            </td>
                        </tr>
                        <tr class="api-table-row">
                            <th class="api-table-item title">namespace</th>
                            <td class="api-table-item type">String</td>
                            <td class="api-table-item">
                                <p>Namespace of this page, usually "public".</p>
                                <pre class="codeblock">"namespace":"public"</pre>
                            </td>
                        </tr>
                        <tr class="api-table-row">
                            <th class="api-table-item title">slug</th>
                            <td class="api-table-item type">String</td>
                            <td class="api-table-item">
                                <p>The identity of this page.</p>
                                <pre class="codeblock">"slug":"hello"</pre>
                            </td>
                        </tr>
                        <tr class="api-table-row">
                            <th class="api-table-item title">title</th>
                            <td class="api-table-item type">String</td>
                            <td class="api-table-item">
                                <p>The title of this page.</p>
                                <pre class="codeblock">"title":"Hello, world!"</pre>
                            </td>
                        </tr>
                        <tr class="api-table-row">
                            <th class="api-table-item title">updated_at</th>
                            <td class="api-table-item type">String</td>
                            <td class="api-table-item">
                                <p><a href="http://en.wikipedia.org/wiki/ISO_8601">ISO 8601</a>-formatted datetime of when the post was updated.</p>
                                <pre class="codeblock">"updated_at":"2016-10-29T14:59:12.451212-08:00"</pre>
                            </td>
                        </tr>
                        <tr class="api-table-row">
                            <th class="api-table-item title">path</th>
                            <td class="api-table-item type">String</td>
                            <td class="api-table-item">
                                <p>The path to this resource.</p>
                                <pre class="codeblock">"page":"/api/1.0/pages/hello/"</pre>
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
                            <th class="api-table-item title">Query</th>
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