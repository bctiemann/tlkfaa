import logging
logger = logging.getLogger(__name__)


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

def tree_to_list(items, sort_by=None, parent_field='parent', omit=[], reverse=False):

    items_flat = []
    roots = []
    items_sorted = []
    items_keyed_by_id = {}

    for item in items:
        items_flat.append({
            'obj': item,
            'children': [],
            'depth': 0,
        })

    for item in items_flat:
        items_keyed_by_id[item['obj'].id] = item

    for item in items_flat:
        parent = getattr(item['obj'], parent_field, None)
        if parent and parent.id in items_keyed_by_id:
            parent = items_keyed_by_id[parent.id]
            parent['children'].append(item)
        else:
            roots.append(item)

    if sort_by:
        roots = sorted(roots, key=lambda k: getattr(k['obj'], sort_by), reverse=reverse)

    while len(roots):
        root = roots[0]
        del roots[0]

        if not omit or not root.obj.id in omit:
            items_sorted.append(root)
            children = sorted(root['children'], key=lambda k: getattr(k['obj'], sort_by), reverse=True)
            for child in children:
                child['depth'] = root['depth'] + 1
                roots.insert(0, child)

    return items_sorted

def list_at_node(items, root):
    new_list = []
    found_root = False
    for node in items:
        if node['obj'] == root:
            found_root = True
            root_depth = node['depth']
        if found_root:
            if node['depth'] <= root_depth and node['obj'] != root:
                found_root = False
            else:
                new_list.append(node)
    return new_list

class PagesLink(object):

    def __init__(self, items_total, items_per_page, page_num, is_descending=True, base_url='', selection_type='text', query_dict={}):
        pages_nav = ''

        if items_total <= items_per_page:
            num_pages = int((items_total - 1) / items_per_page)
            if selection_type in ['text', 'ajax']:
                pages_nav = '<div class="pageslink"></div>'
        else:
            if selection_type in ['text', 'ajax']:
                pages_nav = '<div class="pageslink">Page: '
            elif selection_type == 'menu':
                pages_nav = '<select name="pagenum">\n'
            num_pages = int((items_total - 1) / items_per_page)
            if page_num == 0:
                page_num = num_pages + 1

        prev_page = page_num - 1
        next_page = page_num + 1
        last_page = num_pages + 1
        new_query_dict = query_dict.copy()
        new_query_dict.pop('page', None)
        new_query_str = '&'.join([k + '=' + str(v) for k, v in new_query_dict.items()])

        if selection_type == 'text':
            if page_num > 3:
                pages_nav = '{0} <a href="{1}?{2}&page=1">&laquo; 1</a> '.format(pages_nav, base_url, new_query_str)
                if page_num > 4:
                    pages_nav = '{0}&hellip; '.format(pages_nav)
            elif page_num > 2:
                pages_nav = '{0} <a href="{1}?{2}&page={3}">Prev</a> '.format(pages_nav, base_url, new_query_str, prev_page)
        elif selection_type == 'ajax':
            if page_num > 3:
                pages_nav = '{0} <a href="javascript:nop()" onClick="turnPage(1,\'{1}\')">&laquo; 1</a> '.format(pages_nav, new_query_str)
                if page_num > 4:
                    pages_nav = '{0}&hellip; '.format(pages_nav)
            elif page_num > 2:
                pages_nav = '{0} <a href="javascript:nop()" onClick="turnPage({1},\'{2}\')">Prev</a> '.format(pages_nav, prev_page, new_query_str)

        for i in xrange(page_num - 2, page_num + 3):
            if i > 0 and i < num_pages + 2:
                if page_num == i:
                    if selection_type in ['text', 'ajax']:
                        pages_nav = '{0} <span class="thispage">{1}</span> '.format(pages_nav, i)
                    elif selection_type == 'menu':
                        pages_nav = '{0}<option value="{1}" selected>{2}</option>\n'.format(pages_nav, i, i)
                else:
                    pre_arrow = ''
                    post_arrow = ''
                    if i == 1:
                        pre_arrow = '&laquo; '
                    if i == num_pages + 1:
                        post_arrow = ' &raquo;'
                    if selection_type == 'text':
                        pages_nav = '{0} <a href="{1}?{2}&page={3}">{4}{5}{6}</a> '.format(pages_nav, base_url, new_query_str, i, pre_arrow, i, post_arrow)
                    elif selection_type == 'ajax':
                        pages_nav = '{0} <a href="javascript:nop()" onClick="turnPage({1},\'{2}\')">{3}{4}{5}</a> '.format(pages_nav, i, new_query_str, pre_arrow, i, post_arrow)
                    elif selection_type == 'menu':
                        pages_nav = '{0}<option value="{1}">{2}</option>\n'.format(pages_nav, i, i)

        if selection_type == 'text':
            if page_num < num_pages - 1:
                if page_num < num_pages - 2:
                    pages_nav = '{0} &hellip;'.format(pages_nav)
                pages_nav = '{0} <a href="{1}?{2}&page={3}">{4} &raquo;</a> '.format(pages_nav, base_url, new_query_str, last_page, last_page)
            if page_num < num_pages:
                pages_nav = '{0} <a href="{1}?{2}&page={3}">Next</a> '.format(pages_nav, base_url, new_query_str, next_page)
        elif selection_type == 'ajax':
            if page_num < num_pages - 1:
                if page_num < num_pages - 2:
                    pages_nav = '{0} &hellip;'.format(pages_nav)
                pages_nav = '{0} <a href="javascript:nop()" onClick="turnPage({1},\'{2}\')">{3} &raquo;</a> '.format(pages_nav, last_page, new_query_str, last_page)
            if page_num < num_pages:
                pages_nav = '{0} <a href="javascript:nop()" onClick="turnPage({1},\'{2}\')">Next</a> '.format(pages_nav, next_page, new_query_str)

        if selection_type in ['text', 'ajax']:
            pages_nav = '{0}</div>'.format(pages_nav)
        elif selection_type == 'menu':
            pages_nav = '{0}</select>'.format(pages_nav)

        self.pages_nav = pages_nav
        self.items_per_page = items_per_page
