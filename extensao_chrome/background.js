let currentUrl = "";

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === "getCurrentUrl") {
    currentUrl = message.url;
  }
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === "getUrl") {
    sendResponse({ url: currentUrl });
  }
});
