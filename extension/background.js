console.log("Init")

function getTabsInfo() {
    return new Promise(resolve => {
        chrome.tabs.query({}, tabs => {
            const titles = tabs.map(tab => tab.title);
            const urls = tabs.map(tab => tab.url);
            resolve({ titles, urls });
        });
    });
}

const delay = ms => new Promise(res => setTimeout(res, ms));


// Gets titles and urls, then sends them through GET request to application
async function sendURLs()  {
    var errorStatus = false;
    while (true) {
        await delay(1500);

        const { titles, urls } = await getTabsInfo();
        const queryParams = new URLSearchParams({ titles: titles.join('|-|'), urls: urls.join('|-|') }).toString();
        const url = `http://localhost:8050/urldata?${queryParams}`;
    
        await fetch(url)
        .then(function(response) {
            if (response.status !== 200) {
                console.log('Error, status Code: ' + response.status);
                errorStatus = true;
            }
        })
        .catch(error => {
            errorStatus = true;
        })
        if (errorStatus) {
            errorStatus = false;
            console.log("Error, waiting 15 seconds to reconnect...");
            await delay(15000);
        }
        console.log("GET request sent")
    }
}

sendURLs();
