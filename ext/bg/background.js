chrome.runtime.onInstalled.addListener(() => {
    chrome.action.setBadgeText({
        text: "Beta",
    });
    chrome.storage.local.set({'entry': {}}).then(() => {
        console.log("initialize local storage: entry=", {});
    });
    chrome.storage.local.set({'busy': false}).then(() => {
        console.log("initialize local storage: busy=", false);
    });
});   

chrome.runtime.onMessage.addListener(function (request, sender, sendResponse) {
        if ("new_entry" === request.type) {
            chrome.storage.local.get(['entry']).then((result) => {
                let current_entries = result.entry
                let data = request.msg
                let url_info = new URL(data.entry)
                if (current_entries[url_info.hostname] == undefined){
                    current_entries[url_info.hostname] = {
                        'max_depth': data.depth,
                        'wait_for_parse': [{'depth': 0, 'url': data.entry}],
                        'visited': []
                    }
                    chrome.storage.local.set({'entry': current_entries}).then(() => {
                        console.log("update local storage: entry=", current_entries);
                        sendResponse({'status': 200, 'msg': 'add entry successful'})
                    });

                }else{
                    sendResponse({'status': 400, 'msg': 'Entry already existed'})
                }
            });
        }
        if ("get_entries" === request.type){
            chrome.storage.local.get(['entry']).then((result) => {
                let current_entries = result.entry
                sendResponse({'entries': current_entries})
            })
        }
        return true
    }
)