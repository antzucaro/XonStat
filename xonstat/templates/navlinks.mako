<%def name="navlinks(view, curr, last, **kwargs)">
% if not (curr == last and curr == 1):
    % if curr != 1:
            <a class="pagination" href="${request.route_url(view, page=curr-1, **kwargs)}" name="Previous Page">previous</a>
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
            <a class="pagination" href="${request.route_url(view, page=last, **kwargs)}" name="Last Page">${last}</a>

        % elif last-curr < 6:
            <a class="pagination" href="${request.route_url(view, page=1, **kwargs)}" name="First Page">1</a>
            <span class="pagination">...</span>
            % for i in range(last-5, last+1):
            ${link_page(view, i, curr, **kwargs)}
            % endfor
        % else:
            <a class="pagination" href="${request.route_url(view, page=1, **kwargs)}" name="First Page">1</a>

            <span class="pagination">...</span>
            % for i in range(curr-2, curr+3):
            ${link_page(view, i, curr, **kwargs)}
            % endfor
            <span class="pagination">...</span>
            <a class="pagination" href="${request.route_url(view, page=last, **kwargs)}" name="Last Page">${last}</a>

        % endif
    % endif

    % if curr != last:
        <a class="pagination" href="${request.route_url(view, page=curr+1, **kwargs)}" name="Next Page">next</a>
    % endif
% endif
</%def>

<%def name="link_page(view, page_num, curr_page, **kwargs)">
% if page_num == curr_page:
<span class="pagination" style="color:#d95b00;">${page_num}</span>
% else:
    <a class="pagination" href="${request.route_url(view, page=page_num, **kwargs)}" name="Go to page ${page_num}">${page_num}</a>
% endif
</%def>
