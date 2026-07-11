chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
  if (request.action === "getSelection") {
    sendResponse({ text: window.getSelection().toString() });
  }
});

// Floating widget logic
let floatBtn = null;

document.addEventListener('mouseup', function(e) {
  const selectedText = window.getSelection().toString().trim();
  
  if (selectedText.length > 5) {
    if (!floatBtn) {
      floatBtn = document.createElement('div');
      floatBtn.id = 'vidhi-float-btn';
      floatBtn.innerHTML = 'V';
      document.body.appendChild(floatBtn);
      
      floatBtn.addEventListener('mousedown', function(ev) {
        ev.preventDefault();
        ev.stopPropagation();
        alert("VIDHI is installed! Click the extension icon in your toolbar to scan this text with the 8-Agent Pipeline.");
      });
    }
    floatBtn.style.top = (e.pageY + 10) + 'px';
    floatBtn.style.left = (e.pageX + 10) + 'px';
    floatBtn.style.display = 'flex';
  } else {
    if (floatBtn) {
      floatBtn.style.display = 'none';
    }
  }
});

document.addEventListener('mousedown', function(e) {
  if (floatBtn && e.target !== floatBtn) {
    floatBtn.style.display = 'none';
  }
});
