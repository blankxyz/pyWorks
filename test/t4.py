# coding=utf-8
from django_datatables_view.base_datatable_view import BaseDatatableView


def proxyAdmin(req):
    # rows=Proxy.objects.all()[:100]
    return render_to_response('data/proxyadmin.html')


class ProxyListJson(BaseDatatableView):
    # The model we're going to show
    model = Proxy  # 要分页的类

    # define the columns that will be returned
    columns = ['ip', 'description', 'score', 'logdate']  # 需要显示的字段

    # define column names that will be used in sorting
    # order is important and should be same as order of columns
    # displayed by datatables. For non sortable columns use empty
    # value like ''
    order_columns = ['ip', 'description', 'score', 'logdate']  # 排序

    # set max limit of records returned, this is used to protect our site if someone tries to attack our site
    # and make it return huge amount of data
    max_display_length = 500

    def render_column(self, row, column):
        return super(ProxyListJson, self).render_column(row, column)

    def filter_queryset(self, qs):
        # use parameters passed in GET request to filter queryset
        qs_params = None
        search = self.request.GET.get(u'sSearch', None)
        if search:  # 模糊搜索
            q = Q(ip__contains=search) | Q(description__contains=search)
            qs_params = qs_params | q if qs_params else q

            qs = qs.filter(qs_params)

        return qs
