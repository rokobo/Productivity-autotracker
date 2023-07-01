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

// Execute downloadURLs every 1 seconds
setInterval(downloadURLs, 1000);