document.getElementById("downloaded").onclick = function () {
    window.location.href = "/dwn";
};
document.getElementById("yt_btn").onclick = function () {
    window.location.href = "/";
};

var dwn_btn = document.getElementById("btn_dwn");
var statoElement = document.getElementById("stato");

dwn_btn.addEventListener('click', function() {
    var link = document.getElementById("url").value.trim();
    var urlInput = document.getElementById("url");

    if(!link) {
        urlInput.placeholder = "Please provide a link";
        urlInput.value = "";
        statoElement.textContent = "Error: No link provided";
        statoElement.style.color = "red";
        return;
    }

    // Update status
    statoElement.textContent = "Starting download...";
    statoElement.style.color = "blue";

    fetch('/link', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({link: link})
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.message) {
            statoElement.textContent = "Download ended successfully!";
            statoElement.style.color = "green";
            urlInput.value = ""; // Clear the input
        } else if (data.error) {
            statoElement.textContent = "Error: " + data.error;
            statoElement.style.color = "red";
        }
    })
    .catch(error => {
        console.error("Error:", error);
        statoElement.textContent = "Error: " + error.message;
        statoElement.style.color = "red";
    });
});
