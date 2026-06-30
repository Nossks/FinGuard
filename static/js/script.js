const chatForm = document.getElementById('chatForm');
const userInput = document.getElementById('userInput');
const chatbox = document.getElementById('chatbox');
const modeBadge = document.getElementById('mode-badge');

// Metrics Elements
const elCyborg = document.getElementById('cyborg-val');
const elFaiss = document.getElementById('faiss-val');
const elChroma = document.getElementById('chroma-val');
const elOverFaiss = document.getElementById('overhead-faiss');
const elOverChroma = document.getElementById('overhead-chroma');

chatForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    const text = userInput.value.trim();
    if(!text) return;

    // 1. UI Updates
    userInput.value = '';
    chatbox.innerHTML += `
        <div class="msg msg-user">
            <div class="bubble bubble-user">${text}</div>
        </div>`;
    chatbox.scrollTop = chatbox.scrollHeight;

    // 2. Send Data
    const formData = new FormData();
    formData.append("msg", text);

    try {
        const res = await fetch('/get_response', {
            method: 'POST',
            body: formData
        });
        const data = await res.json();

        // 3. Display Response
        const replyHtml = data.response.replace(/\n/g, "<br>");
        chatbox.innerHTML += `
            <div class="msg msg-bot">
                <div class="bubble bubble-bot">${replyHtml}</div>
            </div>`;
        chatbox.scrollTop = chatbox.scrollHeight;

        // 4. METRICS & ROUTER LOGIC
        if (data.mode_used === "search" && data.metrics) {
            // --- SEARCH MODE ---
            modeBadge.innerHTML = `<i class="fas fa-database me-1"></i> Router: SEARCH`;
            modeBadge.className = "badge bg-success border border-success p-2"; 

            // Extract Values
            const cyborg = data.metrics.cyborg || 0;
            const faiss = data.metrics.faiss || 0;
            const chroma = data.metrics.chroma || 0;

            // Update Raw Numbers
            elCyborg.innerText = cyborg.toFixed(4) + "s";
            elFaiss.innerText = faiss.toFixed(4) + "s";
            elChroma.innerText = chroma.toFixed(4) + "s";
            
            // --- CALCULATE OVERHEADS ---
            // vs FAISS
            if (faiss > 0) {
                const diff = ((cyborg - faiss) / faiss) * 100;
                if (diff > 0) {
                    elOverFaiss.innerText = diff.toFixed(0) + "% Slower";
                    elOverFaiss.className = "fw-bold text-warning";
                } else {
                    elOverFaiss.innerText = Math.abs(diff).toFixed(0) + "% Faster";
                    elOverFaiss.className = "fw-bold text-success";
                }
            } else { elOverFaiss.innerText = "N/A"; }

            // vs Chroma
            if (chroma > 0) {
                const diff = ((cyborg - chroma) / chroma) * 100;
                if (diff > 0) {
                    elOverChroma.innerText = diff.toFixed(0) + "% Slower";
                    elOverChroma.className = "fw-bold text-warning";
                } else {
                    elOverChroma.innerText = Math.abs(diff).toFixed(0) + "% Faster";
                    elOverChroma.className = "fw-bold text-success";
                }
            } else { elOverChroma.innerText = "N/A"; }

        } else {
            // --- CHAT MODE ---
            modeBadge.innerHTML = `<i class="fas fa-comments me-1"></i> Router: CHAT`;
            modeBadge.className = "badge bg-secondary border border-secondary p-2"; 

            // Reset Metrics to Zero / Dashes
            elCyborg.innerText = "0.000s";
            elFaiss.innerText = "--";
            elChroma.innerText = "--";
            elOverFaiss.innerText = "--";
            elOverChroma.innerText = "--";
            
            // Remove color classes from comparisons
            elOverFaiss.className = "fw-bold text-secondary";
            elOverChroma.className = "fw-bold text-secondary";
        }

    } catch (err) {
        console.error(err);
        chatbox.innerHTML += `<div class="msg msg-bot text-danger">Error connecting to server.</div>`;
    }
});