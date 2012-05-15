<%def name="navlinks(view, curr, last, **kwargs)">
<%
kwargs['_query'] = {'page': None}

if 'search_query' in kwargs.keys():
    kwargs['_query'] = dict(kwargs['_query'].items() + kwargs['search_query'].items())
%>

% if not (curr == last and curr == 1):
    % if curr != 1:
            <% kwargs['_query']['page'] = curr-1 %>
            <a class="pagination" href="${request.route_url(view, **kwargs)}" name="Previous Page">previous</a>
    % endif

    % if last < 8:
        % for i in range(1, last+1):
        ${link_page(view, i, curr, **kwargs)}
        % endfor
    % else:
        % if curr < 5:
            % for i in range(1,7):
            ${link_page(view, i, curr, **kwargs)}
            % endfor
            <span class="pagination">...</span>
            <% kwargs['_query']['page'] = last %>
            <a class="pagination" href="${request.route_url(view, **kwargs)}" name="Last Page">${last}</a>

        % elif last-curr < 6:
            <% kwargs['_query']['page'] = 1 %>
            <a class="pagination" href="${request.route_url(view, **kwargs)}" name="First Page">1</a>
            <span class="pagination">...</span>
            % for i in range(last-5, last+1):
            ${link_page(view, i, curr, **kwargs)}
            % endfor
        % else:
            <% kwargs['_query']['page'] = 1 %>
            <a class="pagination" href="${request.route_url(view, **kwargs)}" name="First Page">1</a>

            <span class="pagination">...</span>
            % for i in range(curr-2, curr+3):
            ${link_page(view, i, curr, **kwargs)}
            % endfor
            <span class="pagination">...</span>
            <% kwargs['_query']['page'] = last %>
            <a class="pagination" href="${request.route_url(view, **kwargs)}" name="Last Page">${last}</a>

        % endif
    % endif

    % if curr != last:
            <% kwargs['_query']['page'] = curr+1 %>
        <a class="pagination" href="${request.route_url(view, **kwargs)}" name="Next Page">next</a>
    % endif
% endif
</%def>

<%def name="link_page(view, page_num, curr_page, **kwargs)">
% if page_num == curr_page:
<span class="pagination" style="color:#d95b00;">${page_num}</span>
% else:
    <% kwargs['_query']['page'] = page_num %>
    <a class="pagination" href="${request.route_url(view, **kwargs)}" name="Go to page ${page_num}">${page_num}</a>
% endif
</%def>
