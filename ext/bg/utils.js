function url_normalize(url){
    let url_info = new URL(url)
    return url_info.origin + url_info.pathname + url_info.search
}