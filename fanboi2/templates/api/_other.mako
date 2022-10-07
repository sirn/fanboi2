<%namespace name="formatters" module="fanboi2.helpers.formatters" />
<%namespace name="api" file="../partials/_api.mako" />
<%api:render_api name="api-task" title="Retrieving a specific task" method="GET">
    <%def name="path()">
        ${formatters.unquoted_path(request, 'api_task', task='{task.id}')}
    </%def>
    <%def name="description()">
        <p>Use this endpoint to retrieve a status of a task.</p>
    </%def>
    <%def name="response_object()">
        <tr>
            <th>type</th>
            <td>String</td>
            <td>
                <p>The type of API object. The value is always "task".</p>
                <pre>"type":"task"</pre>
            </td>
        </tr>
        <tr>
            <th>id</th>
            <td>String</td>
            <td>
                <p>Internal ID for the task.</p>
                <pre>"id":"aff5dede-7f4e-4e48-ad4d-2f6396a5e75c"</pre>
            </td>
        </tr>
        <tr>
            <th>status</th>
            <td>String</td>
            <td>
                <p>Status string of the task. Available values are:</p>
                <ul>
                    <li><strong>queued</strong> — the task has been successfully queued.</li>
                    <li><strong>pending</strong> — the task is waiting to be processed.</li>
                    <li><strong>started</strong> — the task has started processing.</li>
                    <li><strong>retry</strong> — the task processing has failed due to internal errors and is queued for a retry.</li>
                    <li><strong>failure</strong> — the task has failed due to internal errors and could not be retried.</li>
                    <li><strong>success</strong> — the task has been processed successfully.</li>
                </ul>
                <p>Normally it is safe to ignore all statuses except for <strong>success</strong>. Note that <strong>success</strong> only refer to the status of the task processing and not the result. For example, it is normal for task to report success status for a post that is rejected by a spam filter. In all cases, always refer to <code>data</code> for the result.</p>
                <pre>"status":"open"</pre>
            </td>
        </tr>
        <tr>
            <th>data</th>
            <td>Object</td>
            <td>
                <p>Result of task processing. It could be one of the following objects depending on the type of task.</p>
                <ul>
                    <li><a href="#api-topic">#api-topic</a></li>
                    <li><a href="#api-topic-posts">#api-topic-posts</a></li>
                    <li><a href="#api-error">#api-error</a></li>
                </ul>
                <p>Only available if <code>status</code> is <strong>success</strong>.</p>
                <pre>"data":{ ... }</pre>
            </td>
        </tr>
        <tr>
            <th>path</th>
            <td>String</td>
            <td>
                <p>The path to this resource.</p>
                <pre>"path":"/api/1.0/tasks/aff5dede-7f4e-4e48-ad4d-2f6396a5e75c/"</pre>
            </td>
        </tr>
    </%def>
</%api:render_api>
<%api:render_api name="api-error" title="Errors">
    <%def name="description()">
        <p>An object representing general errors.</p>
    </%def>
    <%def name="response_object()">
        <tr>
            <th>type</th>
            <td>String</td>
            <td>
                <p>The type of API object. The value is always "error".</p>
                <pre>"type":"error"</pre>
            </td>
        </tr>
        <tr>
            <th>status</th>
            <td>String</td>
            <td>
                <p>Error status. Available statuses are:</p>
                <ul>
                    <li><strong>unknown</strong> — an unknown error occurred.</li>
                    <li><strong>rate_limited</strong> — this IP address has been rate-limited.</li>
                    <li><strong>params_invalid</strong> — required parameters are missing from the request.</li>
                </ul>
                <p>In case of post rejection, the following statuses are returned:</p>
                <ul>
                    <li><strong>akismet_rejected</strong> — the post or topic has been identified as spam by Akismet.</li>
                    <li><strong>dnsbl_rejected</strong> — the IP address is listed in one of DNSBL databases.</li>
                    <li><strong>ban_rejected</strong> — the IP address is listed in the ban list.</li>
                    <li><strong>proxy_rejected</strong> — the IP address has been identified as an open proxy or public VPN.</li>
                    <li><strong>status_rejected</strong> — this board or topic disallows posting.</li>
                </ul>
                <pre>"status":"rate_limited"</pre>
            </td>
        </tr>
        <tr>
            <th>message</th>
            <td>String</td>
            <td>
                <p>Description of the error.</p>
                <pre>"message":"Please wait 20 seconds before retrying."</pre>
            </td>
        </tr>
    </%def>
</%api:render_api>
