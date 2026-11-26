
chrome.runtime.onInstalled.addListener(() => {
    chrome.contextMenus.create({
        id: "phishguard-analyze",
        title: "Analyze with PhishGuard",
        contexts: ["selection"]
    });
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
    if (info.menuItemId === "phishguard-analyze" && info.selectionText) {
        chrome.storage.local.set({
            selectedMessage: info.selectionText
        }, () => {
            chrome.action.openPopup();
        });
    }
});
