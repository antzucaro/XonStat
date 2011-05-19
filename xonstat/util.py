import re

def strip_colors(str=None):
    str = re.sub(r'\^x\w\w\w', '', str)
    str = re.sub(r'\^\d', '', str)
    return str

def html_colors(str=None):
    orig = str
    str = re.sub(r'\^x(\w)(\w)(\w)', 
            "<span style='color:#\g<1>\g<1>\g<2>\g<2>\g<3>\g<3>'>", str)
    str = re.sub(r'\^1', "<span style='color:#FF9900'>", str)
    str = re.sub(r'\^2', "<span style='color:#33FF00'>", str)
    str = re.sub(r'\^3', "<span style='color:#FFFF00'>", str)
    str = re.sub(r'\^4', "<span style='color:#3366FF'>", str)
    str = re.sub(r'\^5', "<span style='color:#33FFFF'>", str)
    str = re.sub(r'\^6', "<span style='color:#FF3366'>", str)
    str = re.sub(r'\^7', "<span style='color:#FFFFFF'>", str)
    str = re.sub(r'\^8', "<span style='color:#999999'>", str)
    str = re.sub(r'\^9', "<span style='color:#666666'>", str)
    str = re.sub(r'\^0', "<span style='color:#333333'>", str)

    for span in range(len(re.findall(r'\^x\w\w\w|\^\d', orig))):
        str += "</span>"

    return str

def page_url(page):
    return current_route_url(request, page=page, _query=request.GET)
