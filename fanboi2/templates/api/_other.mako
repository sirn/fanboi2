<%namespace name='formatters' module='fanboi2.formatters' />
<div class="api-section" id="api-task">
    <div class="api-request">
        <div class="container">
            <h2 class="api-request-title">Retrieving a specific task <span class="api-request-name">#api-task</span></h2>
            <div class="api-request-endpoint"><span class="api-request-verb verb-get">GET</span> ${formatters.unquoted_path(request, 'api_task', task='{task.id}')}</div>
            <div class="api-request-body">
                <p>Use this endpoint to retrieve a status of a task.</p>
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
                                <p>The type of API object. The value is always "task".</p>
                                <pre class="codeblock">"type":"task"</pre>
                            </td>
                        </tr>
                        <tr class="api-table-row">
                            <th class="api-table-item title">id</th>
                            <td class="api-table-item type">String</td>
                            <td class="api-table-item">
                                <p>Internal ID for the task.</p>
                                <pre class="codeblock">"id":"aff5dede-7f4e-4e48-ad4d-2f6396a5e75c"</pre>
                            </td>
                        </tr>
                        <tr class="api-table-row">
                            <th class="api-table-item title">status</th>
                            <td class="api-table-item type">String</td>
                            <td class="api-table-item">
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
                                <pre class="codeblock">"status":"open"</pre>
                            </td>
                        </tr>
                        <tr class="api-table-row">
                            <th class="api-table-item title">data</th>
                            <td class="api-table-item type">Object</td>
                            <td class="api-table-item">
                                <p>Result of task processing. It could be one of the following objects depending on the type of task.</p>
                                <ul>
                                    <li><a href="#api-topic">#api-topic</a></li>
                                    <li><a href="#api-topic-posts">#api-topic-posts</a></li>
                                    <li><a href="#api-error">#api-error</a></li>
                                </ul>
                                <p>Only available if <code>status</code> is <strong>success</strong>.</p>
                                <pre class="codeblock">"data":{ ... }</pre>
                            </td>
                        </tr>
                        <tr class="api-table-row">
                            <th class="api-table-item title">path</th>
                            <td class="api-table-item type">String</td>
                            <td class="api-table-item">
                                <p>The path to this resource.</p>
                                <pre class="codeblock">"path":"/api/1.0/tasks/aff5dede-7f4e-4e48-ad4d-2f6396a5e75c/"</pre>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</div>

<div class="api-section" id="api-error">
    <div class="api-request">
        <div class="container">
            <h2 class="api-request-title">Errors <span class="api-request-name">#api-error</span></h2>
            <div class="api-request-body">
                <p>An object representing general errors.</p>
            </div>
        </div>
    </div>
    <div class="api-response">
        <div class="container">
            <h3 class="api-response-title">Object</h3>
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
                                <p>The type of API object. The value is always "error".</p>
                                <pre class="codeblock">"type":"error"</pre>
                            </td>
                        </tr>
                        <tr class="api-table-row">
                            <th class="api-table-item title">status</th>
                            <td class="api-table-item type">String</td>
                            <td class="api-table-item">
                                <p>Error status. Available statuses are:</p>
                                <ul>
                                    <li><strong>unknown</strong> — an unknown error occurred.</li>
                                    <li><strong>rate_limited</strong> — this IP address has been rate-limited.</li>
                                    <li><strong>params_invalid</strong> — required parameters are missing from the request.</li>
                                    <li><strong>spam_rejected</strong> — the post or topic has been identified as spam.</li>
                                    <li><strong>dnsbl_rejected</strong> — this IP address is blocked in one of DNSBL databases.</li>
                                    <li><strong>status_rejected</strong> — this board or topic disallows posting.</li>
                                </ul>
                                <pre class="codeblock">"status":"rate_limited"</pre>
                            </td>
                        </tr>
                        <tr class="api-table-row">
                            <th class="api-table-item title">message</th>
                            <td class="api-table-item type">String</td>
                            <td class="api-table-item">
                                <p>Description of the error.</p>
                                <pre class="codeblock">"message":"Please wait 20 seconds before retrying."</pre>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</div>

