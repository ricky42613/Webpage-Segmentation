chrome.storage.onChanged.addListener((changes, namespace) => {
    for (let [key, { oldValue, newValue }] of Object.entries(changes)) {
        chrome.storage.local.get([key]).then((result) => {   
            let current_entries = result[key]
            console.log(`storage monitor: ${key} is updated ~ `, current_entries)
            if (key == 'entry'){
                if (!Object.keys(current_entries).length){
                    return
                }
                chrome.runtime.sendMessage({
                    type: "entries updated", 
                    msg: {
                        'entries': current_entries
                    }
                }, function(response){
                    console.log('entries updated: response=', response)
                });
            }
        })
    }
  });