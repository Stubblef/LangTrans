function createMessageElement(content, isAi) {
    const messageRow = document.createElement('div');
    messageRow.className = `message-row ${isAi ? 'ai' : 'user'}`;

    const avatar = document.createElement('div');
    avatar.className = 'avatar';
    avatar.innerHTML = isAi ? '<i class="fas fa-robot"></i>' : '<i class="fas fa-user"></i>';

    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    messageContent.textContent = content;

    messageRow.appendChild(avatar);
    messageRow.appendChild(messageContent);
    return messageRow;
}

let selectedFile = null;

function handleFileSelect() {
    const fileInput = document.getElementById("file-upload");
    selectedFile = fileInput.files[0];
    
    if (selectedFile) {
        const textarea = document.getElementById("user-input");
        textarea.placeholder = `已选择文件: ${selectedFile.name}\n请输入处理提示...`;
    }
}

async function sendMessage() {
    const inputField = document.getElementById("user-input");
    const userMessage = inputField.value.trim();
    if (!userMessage && !selectedFile) return;

    const chatBox = document.getElementById("chat-box");
    chatBox.appendChild(createMessageElement(
        selectedFile ? `文件: ${selectedFile.name}\n提示: ${userMessage}` : userMessage, 
        false
    ));
    
    try {
        let response, data;
        if (selectedFile) {
            const formData = new FormData();
            formData.append("file", selectedFile);
            formData.append("prompt", userMessage);

            response = await fetch("http://98.84.180.120:8888/upload", {
                method: "POST",
                body: formData,
                timeout: 120000 // 60s
            });
        } else {
            response = await fetch("http://98.84.180.120:8888/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: userMessage })
            });
        }

        if (response.ok) {
            data = await response.json();
            chatBox.appendChild(createMessageElement(data.reply || data.summary, true));
        } else {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        // Reset file selection
        selectedFile = null;
        document.getElementById("file-upload").value = "";
    } catch (error) {
        console.error("请求失败:", error);
        chatBox.appendChild(createMessageElement("处理请求时出错", true));
    }
    
    inputField.value = "";
    inputField.placeholder = "输入消息或上传文件时的处理提示...";
    adjustTextareaHeight();
    chatBox.scrollTop = chatBox.scrollHeight;
}

function handleKeyPress(event) {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
        document.getElementById("user-input").value = ""; // Clear the input field
    }
}

function adjustTextareaHeight() {
    const textarea = document.getElementById("user-input");
    textarea.style.height = "auto";
    textarea.style.height = Math.min(textarea.scrollHeight, 200) + "px";
}

async function uploadFile() {
    const fileInput = document.getElementById("file-upload");
    if (!fileInput.files.length) return;

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    const statusElement = document.getElementById("upload-status");
    statusElement.textContent = "上传中...";

    try {
        const response = await fetch("http://98.84.180.120:8888/upload", {
            method: "POST",
            body: formData
        });

        const data = await response.json();
        statusElement.textContent = `✓ ${data.filename} 上传成功`;
    } catch (error) {
        statusElement.textContent = "上传失败";
        console.error("文件上传失败:", error);
    }
}

function startNewChat() {
    document.getElementById("chat-box").innerHTML = "";
}

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    const textarea = document.getElementById("user-input");
    textarea.addEventListener('input', adjustTextareaHeight);
});
