<%def name="navlinks(view, curr, last, **kwargs)">
<%
kwargs['_query'] = {'page': None}

if 'search_query' in kwargs.keys():
    kwargs['_query'] = dict(kwargs['_query'].items() + kwargs['search_query'].items())
%>

% if not last:
    <% last = 1 %>
% endif

% if not (curr == last and curr == 1):
<div class="row">
<div class="small-12 columns text-center">
<ul class="pagination">
    % if curr != 1:
            <% kwargs['_query']['page'] = curr-1 %>
            <li><a href="${request.route_url(view, **kwargs)}" name="Previous Page"><i class="glyphicon glyphicon-arrow-left"></i></a></li>
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
            <li><span>...<span></li>
            <% kwargs['_query']['page'] = last %>
            <li><a  href="${request.route_url(view, **kwargs)}" name="Last Page">${last}</a></li>

        % elif last-curr < 6:
            <% kwargs['_query']['page'] = 1 %>
            <li><a  href="${request.route_url(view, **kwargs)}" name="First Page">1</a></li>
            <li><span >...</span></li>
            % for i in range(last-5, last+1):
            ${link_page(view, i, curr, **kwargs)}
            % endfor
        % else:
            <% kwargs['_query']['page'] = 1 %>
            <li><a  href="${request.route_url(view, **kwargs)}" name="First Page">1</a></li>

            <li><span >...</span></li>
            % for i in range(curr-2, curr+3):
            ${link_page(view, i, curr, **kwargs)}
            % endfor
            <li><span >...</span></li>
            <% kwargs['_query']['page'] = last %>
            <li><a  href="${request.route_url(view, **kwargs)}" name="Last Page">${last}</a></li>

        % endif
    % endif

    % if curr != last:
            <% kwargs['_query']['page'] = curr+1 %>
        <li><a  href="${request.route_url(view, **kwargs)}" name="Next Page"><i class="glyphicon glyphicon-arrow-right"></i></a></li>
    % endif
</ul>
</div> <!-- end span12 -->
</div> <!-- end row -->
% endif
</%def>

<%def name="link_page(view, page_num, curr_page, **kwargs)">
% if page_num == curr_page:
<li>${page_num}</li>
% else:
    <% kwargs['_query']['page'] = page_num %>
    <li><a  href="${request.route_url(view, **kwargs)}" name="Go to page ${page_num}">${page_num}</a></li>
% endif
</%def>
