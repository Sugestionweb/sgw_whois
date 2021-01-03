from . import sgw_net, sgw_parse


def whois(domain, normalized=None):
    if normalized is None:
        normalized = [] 
    raw_data, server_list = sgw_net.get_whois_raw(domain, with_server_list=True)
    return sgw_parse.parse_raw_whois(
        raw_data,
        normalized=normalized,
        never_query_handles=False,
        handle_server=server_list[-1],
    )
