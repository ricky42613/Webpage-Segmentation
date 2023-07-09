(function(){
    $(document).ready(function () {
        console.log('start to get seed from ',window.location.href)
        let last_fragment_idx = window.location.href.indexOf('#')
        let depth_info = window.location.href.slice(last_fragment_idx+1).split(',')
        let body = document.body.outerHTML
        let new_seed = []
        if (parseInt(depth_info[0]) < parseInt(depth_info[1])){
            document.querySelectorAll('a').forEach(item=>{
                let url_info = new URL(item.href)
                if (url_info.hostname == window.location.hostname){
                    let new_url = url_info.origin + url_info.pathname + url_info.search
                    if (new_seed.indexOf(new_url) == -1){
                        new_seed.push(new_url)   
                    }
                }
            })
        }
        // Todo: fetch to web segmentor
        chrome.runtime.sendMessage({
            type: 'add_new_seed',
            msg: {
                'url': window.location.origin + window.location.pathname + window.location.search,
                'new_seed': new_seed,
                'domain': window.location.hostname,
                'depth': depth_info[0]
            }
        }, function (response) {
            console.log(response)
            setTimeout(function(){
                window.close()
            }, 5000)
        })
    })
})()