

def join_url(prefix, path):
    """
    连接url path和前缀
    :param prefix:
    :param path:
    :return:
    """
    if prefix:
        if not path.startswith('/'):
            path = '/'+path
        if not prefix.startswith('/'):
            prefix = '/' + prefix
        path = prefix+path
        return path
    return path
