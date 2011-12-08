<%def name="navlinks(view, curr, last)">

<%
if (curr+4) > last:
    last_linked_page = last
else:
    last_linked_page = curr+4

pages_to_link = range(curr+1, last_linked_page+1)
%>

<a class="pagination" href="${request.route_url(view, page=1)}" name="First Page"><<</a>

% if curr != 1:
<a class="pagination" href="${request.route_url(view, page=curr-1)}" name="Previous Page"><</a>
% endif

% for page_num in pages_to_link:
<a class="pagination" href="${request.route_url(view, page=page_num)}" name="Go to page ${page_num}">${page_num}</a>
% endfor

% if curr != last:
<a class="pagination" href="${request.route_url(view, page=curr+1)}" name="Next Page">></a>
% endif

<a class="pagination" href="${request.route_url(view, page=last)}" name="Last Page">>></a>

(Page <a href="${request.route_url(view, page=curr)}" name="Go to page ${curr}">${curr}</a> of <a href="${request.route_url(view, page=last)}" name="Last Page">${last}</a>)
</%def>
