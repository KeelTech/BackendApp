def sort_case_chat_list(list):
    """
    Remove item with empty sent_date and sort descending by sent_date
    """

    new = [i for i in list if i["chat_details"]["sent_date"] != ""]

    sorted_by_sent_date = sorted(
        new,
        key=lambda e: (e["chat_details"]["sent_date"],),
        reverse=True,
    )

    return sorted_by_sent_date
