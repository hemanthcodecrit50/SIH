async function getAdvisory() {
    const query = document.getElementById("query").value;
    const formData = new FormData();
    formData.append("query", query);
    const response = await fetch("http://127.0.0.1:8000/advisory", {
        method: "POST",
        body: formData
    });
    const data = await response.json();
    document.getElementById("response").innerText = data.response;
    document.getElementById("intent").innerText = "Intent: " + data.intent;
    document.getElementById("timestamp").innerText = "Time: " + data.timestamp;
    document.getElementById("audio").src = data.audio_url;
    document.getElementById("audio").style.display = "block";
}

document.addEventListener("DOMContentLoaded", function() {
    document.getElementById("submitBtn").onclick = getAdvisory;
});
