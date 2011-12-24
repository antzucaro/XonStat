<%def name="navlinks(view, curr, last, query=None)">
% if curr != last:
    % if curr != 1:
        % if query is not None:
            <a class="pagination" href="${request.route_url(view, page=curr-1, _query=query)}" name="Previous Page">previous</a>
        % else:
            <a class="pagination" href="${request.route_url(view, page=curr-1)}" name="Previous Page">previous</a>
        % endif
    % endif

    % if last < 8:
        % for i in range(1, last+1):
        ${link_page(view, i, curr, query)}
        % endfor
    % else:
        % if curr < 5:
            % for i in range(1,7):
            ${link_page(view, i, curr, query)}
            % endfor
            <span class="pagination">...</span>
            % if query is not None:
                <a class="pagination" href="${request.route_url(view, page=last, _query=query)}" name="Last Page">${last}</a>
            % else:
                <a class="pagination" href="${request.route_url(view, page=last)}" name="Last Page">${last}</a>
            % endif

        % elif last-curr < 6:
            % if query is not None:
                <a class="pagination" href="${request.route_url(view, page=1, _query=query)}" name="First Page">1</a>
            % else:
                <a class="pagination" href="${request.route_url(view, page=1)}" name="First Page">1</a>
            % endif
            <span class="pagination">...</span>
            % for i in range(last-5, last+1):
            ${link_page(view, i, curr, query)}
            % endfor
        % else:
            % if query is not None:
                <a class="pagination" href="${request.route_url(view, page=1, _query=query)}" name="First Page">1</a>
            % else:
                <a class="pagination" href="${request.route_url(view, page=1)}" name="First Page">1</a>
            % endif

            <span class="pagination">...</span>
            % for i in range(curr-2, curr+3):
            ${link_page(view, i, curr, query)}
            % endfor
            <span class="pagination">...</span>
            % if query is not None:
                <a class="pagination" href="${request.route_url(view, page=last, _query=query)}" name="Last Page">${last}</a>
            % else:
                <a class="pagination" href="${request.route_url(view, page=last)}" name="Last Page">${last}</a>
            % endif

        % endif
    % endif

    % if curr != last:
        % if query is not None:
            <a class="pagination" href="${request.route_url(view, page=curr+1, _query=query)}" name="Next Page">next</a>
        % else:
            <a class="pagination" href="${request.route_url(view, page=curr+1)}" name="Next Page">next</a>
        % endif
    % endif
% endif
</%def>

<%def name="link_page(view, page_num, curr_page, query)">
% if page_num == curr_page:
<span class="pagination" style="color:#d95b00;">${page_num}</span>
% else:
    % if query is not None:
        <a class="pagination" href="${request.route_url(view, page=page_num, _query=query)}" name="Go to page ${page_num}">${page_num}</a>
    % else:
        <a class="pagination" href="${request.route_url(view, page=page_num)}" name="Go to page ${page_num}">${page_num}</a>
    % endif
% endif
</%def>
