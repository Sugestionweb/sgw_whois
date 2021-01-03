
# Set a bool value that indicates whether the domain is already registered. 
    list_free_domain = ['free','available','not found','no match']
    data['is_taken'] = True
    if "status" in data:
        data['is_taken'] = not data['status'][0] in list_free_domain
    else:
        set_flag_is_taken(data)
    
    return data

def set_flag_is_taken(data):
    whois_raw_txt = data['raw'][0]
    list_regexs = [
        r"The registration of this domain is restricted",
        ]
    
    for line in whois_raw_txt.splitlines():
        for regex in list_regexs.items():
            result = re.search(regex, line)
            if result is not None:
                data['is_taken'] = True
                break;
    return


