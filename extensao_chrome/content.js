console.log("content.js carregado!");

chrome.runtime.sendMessage({
    action: "getCurrentUrl",
    url: window.location.href
  });
  