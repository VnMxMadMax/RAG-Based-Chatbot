// Handle PDF or URL upload
const uploadForm = document.getElementById("upload-form");
const fileInput = document.getElementById("myfile");
const urlInput = document.getElementById("url");

uploadForm.addEventListener("submit", async function(event) {
    event.preventDefault();

    const file = fileInput.files[0];
    const url = urlInput.value.trim();

    if (!file && !url) {
        alert("Please upload a PDF or enter a URL.");
        return;
    }

    if (file && url) {
        alert("Please only upload a PDF or enter a URL, not both.");
        return;
    }

    const formData = new FormData();
    if (file) formData.append("myfile", file);
    if (url) formData.append("url", url);

    const uploadButton = uploadForm.querySelector("input[type='submit']");
    uploadButton.disabled = true;
    uploadButton.value = "Uploading...";

    try {
        const res = await fetch("http://localhost:8000/upload", {
            method: "POST",
            body: formData,
        });

        const data = await res.json();
        console.log("Upload response:", data);

        if (res.ok) {
            alert(data.message);
            fileInput.value = "";
            urlInput.value = "";
        } else {
            alert(data.error || "Upload failed. Check server logs.");
        }
    } catch (err) {
        console.error("Upload failed:", err);
        alert("Error uploading file or URL.");
    } finally {
        uploadButton.disabled = false;
        uploadButton.value = "Submit";
    }
});

// Handle chat form submission
const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");
const chatBox = document.getElementById("chat-box");

chatForm.addEventListener("submit", function(event) {
    event.preventDefault();

    const message = chatInput.value.trim();
    if (message === "") return;

    addMessage("user", message);
    chatInput.value = "";

    (async () => {
        addMessage("bot", "Thinking...");
        const response = await getBotReply(message);
        const botMessages = document.querySelectorAll("#chat-box .message.bot");
        botMessages[botMessages.length - 1].textContent = response;
    })();
});

// Add chat messages to UI
function addMessage(sender, text) {
    const msgDiv = document.createElement("div");
    msgDiv.className = `message ${sender}`;
    msgDiv.textContent = text;
    chatBox.appendChild(msgDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Communicate with the backend's /chat endpoint
async function getBotReply(userMessage) {
    try {
        const res = await fetch("http://localhost:8000/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ question: userMessage })
        });

        if (!res.ok) {
            const errData = await res.json();
            return errData.error || "Something went wrong.";
        }

        const data = await res.json();

        if (!data.answer || data.answer.trim() === "") {
            return "Sorry, I couldn't find a good answer.";
        }

        return data.answer;
    } catch (err) {
        console.error("Chat error:", err);
        return "Error contacting server.";
    }
}


