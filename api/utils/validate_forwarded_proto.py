def validateHTTPS(url: str, schema: str = None):
    print (url,schema)
    if schema is None:
        return url
    else:
        if schema == "https":
            url = url.replace("http://","https://",1)
        return url
    