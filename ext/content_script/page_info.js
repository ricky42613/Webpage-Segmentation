(function(){
    $(document).ready(function () {
        console.log('start to get seed from ',window.location.href)
        let last_fragment_idx = window.location.href.indexOf('#')
        let depth_info = window.location.href.slice(last_fragment_idx+1).split(',')
        let body = document.querySelector('html').outerHTML
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
        let msg = {
            'url': window.location.origin + window.location.pathname + window.location.search,
            'new_seed': new_seed,
            'domain': window.location.hostname,
            'depth': depth_info[0]
        }
        // Todo: fetch to web segmentor
        chrome.runtime.sendMessage({
            type: 'segment_body',
            msg: {
                'url': msg.url,
                'body': body
            }
        }, function(response){
            if (chrome.runtime.lastError || response.status == 500){
                msg.new_seed = []
            }
            else if (response.status == 200){
                let max_size_block = null
                let max_size = 0
                response.msg.blocks.forEach((path, idx) => {
                    let element = document.evaluate(path, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue
                    if (element.clientWidth > window.innerWidth * 0.4) {
                        if (max_size < element.clientWidth * element.clientHeight) {
                            max_size = element.clientWidth * element.clientHeight
                            max_size_block = element
                        }
                    }
                    element.style['border-color'] = "#aaaaee";
                    element.style['border-width'] = "3px";
                    element.style['border-style'] = "solid";
                    element.className += " pageeng_mainblock";
                });
                if (max_size_block != null) {
                    max_size_block.className += " pageeng_largestblock";
                }
            }
            chrome.runtime.sendMessage({
                type: 'add_new_seed',
                msg: msg
            }, function (response) {
                console.log(response)
                // setTimeout(function(){
                //     window.close()
                // }, 5000)
            })  

        })
    })
})()