document.addEventListener('DOMContentLoaded', () => {
  // If user highlighted text, prepopulate it
  chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
    chrome.tabs.sendMessage(tabs[0].id, {action: "getSelection"}, function(response) {
      if (response && response.text) {
        document.getElementById('query').value = response.text;
      }
    });
  });

  document.getElementById('scanBtn').addEventListener('click', () => {
    const q = document.getElementById('query').value.trim();
    if(!q) return;
    
    document.getElementById('statusBox').style.display = 'block';
    document.getElementById('resCard').style.display = 'none';
    document.getElementById('statusText').innerText = 'Connecting to VIDHI Pipeline...';
    document.getElementById('scanBtn').innerText = 'Analyzing...';
    document.getElementById('scanBtn').disabled = true;
    
    // Connect to the local backend since they are demoing locally
    const ws = new WebSocket("ws://localhost:8000/ws/analyze");
    
    ws.onopen = () => {
      ws.send(JSON.stringify({query: q, lang: 'en', lat: 0, lng: 0}));
    };
    
    ws.onmessage = (e) => {
      const m = JSON.parse(e.data);
      if(m.event === 'node_start') {
        document.getElementById('currentAgent').innerText = 'AGENT: ' + m.node.toUpperCase().replace('_', ' ');
      }
      else if(m.event === 'thought') {
        document.getElementById('statusText').innerText = '> ' + m.text;
      }
      else if(m.event === 'node_done') {
        if(m.node === 'win_scorer') {
          document.getElementById('winProb').innerText = m.data.win_prob + '%';
        }
        if(m.node === 'strategic_advisor') {
          document.getElementById('strategyText').innerText = m.data.plan || m.data.risk || 'Plan computed.';
        }
      }
      else if(m.event === 'complete') {
        document.getElementById('statusBox').style.display = 'none';
        document.getElementById('resCard').style.display = 'block';
        document.getElementById('scanBtn').innerText = 'Scan Completed';
      }
    };
    
    ws.onerror = () => {
      document.getElementById('statusText').innerText = 'Error: Make sure the local VIDHI backend is running on port 8000.';
      document.getElementById('scanBtn').innerText = 'Try Again';
      document.getElementById('scanBtn').disabled = false;
    };
  });
});
