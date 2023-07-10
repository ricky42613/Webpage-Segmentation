function get_page_info(url, depth, max_depth){
    return new Promise(async function(resolve, reject){
        let tab_info = await chrome.tabs.create({'url': `${url}#${depth},${max_depth}`, 'active': false})
        let tab_id = tab_info.id
        await chrome.scripting.executeScript({target : {tabId : tab_id}, files : ["js/jquery-3.4.1.js", "content_script/page_info.js" ]})
        chrome.tabs.onRemoved.addListener(function tab_close_handler(tid, rm_info){
            if (tab_id === tid){
                chrome.tabs.onRemoved.removeListener(tab_close_handler);
                console.log('get_page_info: remove tabId=', tab_id)
                resolve()
            }
        })
    })
}

function parse_site(domain, current_entries){
    return new Promise(async function(resolve, reject){
        while(current_entries[domain].wait_for_parse.length){
            let target = current_entries[domain].wait_for_parse.shift()
            await chrome.storage.local.set({'entry': current_entries})
            if (current_entries[domain].visited.indexOf(target) == -1){
                await get_page_info(target.url, target.depth, current_entries[domain].max_depth)
            }
            let storage = await chrome.storage.local.get(['entry'])
            current_entries = storage.entry
        }
        console.log('parse_site: finish domain=', domain)
        resolve()
    })
}

setInterval(function(){
    var p = new Promise(async function(resolve, reject){
        let status = await chrome.storage.local.get(['busy'])
        if (status.busy){
            resolve()
        } else {
            await chrome.storage.local.set({'busy': true})
            let storage = await chrome.storage.local.get(['entry'])
            console.log('site parser: current entries=', storage.entry)
            let current_entries = storage.entry
            let domain = ''
            Object.keys(current_entries).forEach(item=>{
                if (current_entries[item].wait_for_parse.length && domain.length == 0){
                    domain = item
                }
            })
            if (domain.length){
                console.log('site parser: parse domain=', domain)
                await parse_site(domain, current_entries)
            }
            await chrome.storage.local.set({'busy': false})
            resolve()
        }
    })
}, 15000)

chrome.runtime.onMessage.addListener(function (request, sender, sendResponse) {
    if ("add_new_seed" === request.type) {
        let url = request.msg.url
        let domain = request.msg.domain
        let new_seed = request.msg.new_seed
        let depth = parseInt(request.msg.depth)
        console.log('add_new_seed: msg=', request.msg)
        chrome.storage.local.get(['entry']).then((result) => {
            let current_entries = result.entry
            if (current_entries[domain] != undefined){
                current_entries[domain].visited.push(url)
                new_seed.forEach(item => {
                    if (current_entries[domain].visited.indexOf(item) == -1){
                        current_entries[domain].wait_for_parse.push({'depth': depth+1, 'url': url_normalize(item)})
                    }
                });
                chrome.storage.local.set({'entry': current_entries}).then(() => {
                    console.log("update local storage: entry=", current_entries);
                    sendResponse({'status': 200, 'msg': 'update entries domain=', domain})
                });

            }else{
                sendResponse({'status': 404, 'msg': 'Entry Not Found'})
            }
        });
    }
    else if ("segment_body" === request.type) {
        let post_data = {
            "page": request.msg.body,
            "url": request.msg.url
        }
        fetch('http://127.0.0.1:5000/segmentation', {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            body: JSON.stringify(post_data)
        })
        .then(response => response.json())
        .then(json => {
            console.log('segment_body: server response', json)
            sendResponse({'status': 200, msg: json})
        }).catch(error=>{
            console.log('segment_body: error when segmenting=', error)
            sendResponse({'status': 500, msg: error})
        })
    }
    return true
})