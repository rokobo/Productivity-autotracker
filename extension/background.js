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
    while (true) {
        await delay(1500);

        const { titles, urls } = await getTabsInfo();
        const queryParams = new URLSearchParams({ titles: titles.join('|-|'), urls: urls.join('|-|') }).toString();
        const url = `http://localhost:8050/urldata?${queryParams}`;
        try {
            await fetch(url)
            .then(function(response) {
                if (response.status !== 200) {
                    console.log('Error, status Code: ' + response.status);
                }
            })
            console.log("GET request sent")
        }
        catch (error) {
            console.log("Error");
        }
    }
}

sendURLs();
