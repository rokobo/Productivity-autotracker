// Function to download the URLs
function downloadURLs() {
    chrome.tabs.query({}, tabs => {
        const urls = tabs
        .filter(tab => tab.url)
        .map(tab => `${tab.title}|-|${tab.url}`); // Collect titles and URLs of all open tabs
        const blob = new Blob([urls.join("\n")], { type: "text/plain" }); // Create a text blob with the URLs
        const url = URL.createObjectURL(blob); // Generate a URL for the blob
        
        chrome.downloads.download({
            url,
            filename: "EXTENSION/TAB_URLS.txt",
            saveAs: false,
            conflictAction: "uniquify"
        });
    });
    chrome.downloads.setShelfEnabled(false);
}

// Event listener for tab open
chrome.tabs.onCreated.addListener(() => {
    downloadURLs();
});

// Event listener for tab close
chrome.tabs.onRemoved.addListener(() => {
    downloadURLs();
});

// Event listener for tab update (URL change)
chrome.tabs.onUpdated.addListener(() => {
    downloadURLs();
});

// Execute downloadURLs every 2.5 seconds
setInterval(downloadURLs, 2500);