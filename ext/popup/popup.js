function add_entry(domain, info){
    let new_elem = `
        <li class="list-group-item d-flex justify-content-between align-items-center">
        ${domain}
        <span class="badge">
            <span class="badge bg-primary rounded-pill">${info.visited.length}</span>
            <span class="badge bg-warning rounded-pill">${info.wait_for_parse.length}</span>
        </span>
        </li>
    ` 
    let entry_list = document.querySelector('.entry-list')
    entry_list.insertAdjacentHTML('beforeend', new_elem);
}

$(document).ready(function () {
    chrome.runtime.sendMessage({
        type: 'get_entries',
    }, function (response) {
        let new_entries = response.entries
        for(let domain in new_entries){
            add_entry(domain, new_entries[domain])
        }
    })
	$('.add').on('click', function () {
		let entry = $('.entry').val().trim();
		let depth = parseInt($('.depth').val().trim())
		chrome.runtime.sendMessage({
            type: 'new_entry',
            msg: {'entry': entry, 'depth': depth}
        }, function (response) {
            console.log('new_entry: response=', response)
        })
	})
    chrome.runtime.onMessage.addListener(
        function(request, sender, sendResponse) {
            if (request.type === "entries updated") {
                console.log(request.entries)
                let new_entries = request.msg.entries
                document.querySelector('.entry-list').innerHTML = ''
                for(let domain in new_entries){
                    add_entry(domain, new_entries[domain])
                }
                sendResponse('receive new entries')
            }
        }
    );
});
