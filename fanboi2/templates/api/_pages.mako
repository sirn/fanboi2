<%namespace name="formatters" module="fanboi2.helpers.formatters" />
<%namespace name="api" file="../partials/_api.mako" />
<%api:render_api name="api-pages" title="Retrieving pages" method="GET">
    <%def name="path()">
        ${formatters.unquoted_path(request, 'api_pages')}
    </%def>
    <%def name="description()">
        <p>Use this endpoint to retrieve a list of all pages. Usually these pages will contain static content, such as guidelines or help.
    </%def>
    <%def name="response_body()">
        <p><code>Array</code> containing <a href="#api-page">#api-page</a>.</p>
    </%def>
</%api:render_api>
<%api:render_api name="api-page" title="Retrieving a page" method="GET">
    <%def name="path()">
        ${formatters.unquoted_path(request, 'api_page', page='{api-page.slug}')}
    </%def>
    <%def name="description()">
        <p>Use this endpoint to retrieve any individual page.</p>
    </%def>
    <%def name="response_object()">
        <tr>
            <th>type</th>
            <td>String</td>
            <td>
                <p>The type of API object. The value is always "page".</p>
                <pre>"type":"page"</pre>
            </td>
        </tr>
        <tr>
            <th>id</th>
            <td>Integer</td>
            <td>
                <p>Internal ID for the page.</p>
                <pre>"id":1</pre>
            </td>
        </tr>
        <tr>
            <th>body</th>
            <td>String</td>
            <td>
                <p>The page body.</p>
                <pre>"body":"..."</pre>
            </td>
        </tr>
        <tr>
            <th>body_formatted</th>
            <td>String</td>
            <td>
                <p>Same as <strong>body</strong> but format it using specified <strong>formatter</strong>. Note that this field is meant to be rendered in a HTML viewer and will escape the body in case the formatter is "none". If the content will not be displayed in a HTML viewer in case the formatter is "none", <strong>body</strong> must be used instead.</p>
                <pre>"body_formatted":"&lt;p&gt;&lt;em&gt;Hello, world&lt;/em&gt;&lt;/p&gt;\n"</pre>
            </td>
        </tr>
        <tr>
            <th>formatter</th>
            <td>String</td>
            <td>
                <p>Name of a formatter to format this page's body. Available values are:</p>
                <ul>
                    <li><strong>markdown</strong> — render this page using Markdown formatter (see also <a href="http://misaka.61924.nl/">Misaka</a>).</li>
                    <li><strong>html</strong> — render this page as HTML without any escaping.</li>
                    <li><strong>none</strong> — render this page as text or escape HTML as appropriate.</li>
                </ul>
                <pre>"formatter":"markdown"</pre>
            </td>
        </tr>
        <tr>
            <th>namespace</th>
            <td>String</td>
            <td>
                <p>Namespace of this page, usually "public".</p>
                <pre>"namespace":"public"</pre>
            </td>
        </tr>
        <tr>
            <th>slug</th>
            <td>String</td>
            <td>
                <p>The identity of this page.</p>
                <pre>"slug":"hello"</pre>
            </td>
        </tr>
        <tr>
            <th>title</th>
            <td>String</td>
            <td>
                <p>The title of this page.</p>
                <pre>"title":"Hello, world!"</pre>
            </td>
        </tr>
        <tr>
            <th>updated_at</th>
            <td>String</td>
            <td>
                <p><a href="http://en.wikipedia.org/wiki/ISO_8601">ISO 8601</a>-formatted datetime of when the post was updated.</p>
                <pre>"updated_at":"2016-10-29T14:59:12.451212-08:00"</pre>
            </td>
        </tr>
        <tr>
            <th>path</th>
            <td>String</td>
            <td>
                <p>The path to this resource.</p>
                <pre>"page":"/api/1.0/pages/hello/"</pre>
            </td>
        </tr>
    </%def>
</%api:render_api>
