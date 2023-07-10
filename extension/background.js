// Function to create a debounced version of a function
function debounce(func, wait, immediate) {
    var timeout;
    return function executedFunction() {
        var context = this;
        var args = arguments;

        var later = function() {
            timeout = null;
            if (!immediate) func.apply(context, args);
        };
    
        var callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(context, args);
    };
}

// Create a debounced version of the anonymous function
var returnedFunction = debounce(function() {
     // Query all tabs
    chrome.tabs.query({ currentWindow: true }, tabs => {
        // Collect titles and URLs of all open tabs
        const urls = tabs
        .filter(tab => tab.url)
        .map(tab => `${tab.title}|-|${tab.url}`);

        // Create a text blob with the URLs
        const blob = new Blob([urls.join("\n")], { type: "text/plain" }); 

        // Generate a URL for the blob
        const url = URL.createObjectURL(blob);

        // Initiate the download of the URLs
        chrome.downloads.download({
            url,
            filename: "EXTENSION/TAB_URLS.txt",
            saveAs: false,
            conflictAction: "uniquify"
        });
    });
    // Disable the downloads shelf
    chrome.downloads.setShelfEnabled(false);
}, 400);

// Execute downloadURLs on tab change and interval
chrome.tabs.onCreated.addListener(returnedFunction);
chrome.tabs.onRemoved.addListener(returnedFunction);
chrome.tabs.onUpdated.addListener(returnedFunction);
setInterval(returnedFunction, 1000);