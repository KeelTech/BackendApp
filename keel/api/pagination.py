def paginate_queryset_refactored_consumer_app(queryset, request, page_size=20):
    if request.query_params.get('from_app', False) and not request.query_params.get('page'):
        return queryset
    return paginate_queryset(queryset, request, page_size)


def paginate_queryset(queryset, request, page_size=20):
    page = int(request.query_params.get('page', 1))

    if page_size < 0 or page_size > 100:
        page_size = 20

    if page < 1:
        page = 1

    offset = (page - 1) * page_size
    return queryset[offset:page * page_size]


def paginate_raw_query(request, query_string, page_size=20):
    page = int(request.query_params.get('page', 1))

    if page_size < 0 or page_size > 100:
        page_size = 20

    if page < 1:
        page = 1

    offset = (page - 1) * page_size
    return " {} offset {} limit {}".format(query_string, offset, page_size)
