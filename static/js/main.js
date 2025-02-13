document.addEventListener('DOMContentLoaded', function() {
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    let mediaRecorder = null;
    let recordedChunks = [];

    function addMessage(message, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', 'p-4', 'rounded-lg', 'mb-4', 'text-sm', sender === 'user' ? 'user-message' : 'bot-message');
        messageDiv.textContent = message;
        
        if (sender === 'user') {
            messageDiv.classList.add('ml-auto', 'text-white');
        } else {
            messageDiv.classList.add('mr-auto', 'text-gray-800');
        }
        
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function sendMessage(message, isInitial = false) {
        if (!message && !isInitial) return;
        
        if (!isInitial) {
            addMessage(message, 'user');
        }
        
        fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        })
            .then(response => response.json())
            .then(data => {
                console.log("API Response:", data);
                addMessage(data.response, 'bot');
                
                // Handle file upload interface
                if (data.response.includes('upload your resume')) {
                    const uploadDiv = createFileUploadInterface();
                    chatMessages.appendChild(uploadDiv);
                }
                // Handle video recording interface
                else if (data.response.includes('record a short self-introduction video')) {
                    const videoDiv = createVideoInterface();
                    chatMessages.appendChild(videoDiv);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                addMessage('Error: Could not send message', 'bot');
            });
        
        userInput.value = '';
    }

    // Create file upload interface
    function createFileUploadInterface() {
        const uploadDiv = document.createElement('div');
        uploadDiv.classList.add('upload-interface');
        
        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.accept = '.pdf,.doc,.docx';
        
        const uploadButton = document.createElement('button');
        uploadButton.textContent = 'Upload Resume';
        uploadButton.classList.add('px-4', 'py-2', 'text-white', 'rounded');
        
        uploadButton.addEventListener('click', function() {
            const file = fileInput.files[0];
            if (!file) {
                addMessage('Please select a file first', 'bot');
                return;
            }
            
            const formData = new FormData();
            formData.append('resume', file);
            
            fetch('/api/upload-resume', {
                method: 'POST',
                body: formData
            })
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        addMessage(data.error, 'bot');
                    } else {
                        addMessage('Resume uploaded successfully', 'bot');
                        sendMessage('Resume uploaded');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    addMessage('Error uploading resume', 'bot');
                });
        });
        
        uploadDiv.appendChild(fileInput);
        uploadDiv.appendChild(uploadButton);
        return uploadDiv;
    }

    // Create video interface
    function createVideoInterface() {
        const videoDiv = document.createElement('div');
        videoDiv.classList.add('video-interface');
        
        const videoPreview = document.createElement('video');
        videoPreview.id = 'video-preview';
        videoPreview.width = 320;
        videoPreview.height = 240;
        
        const recordButton = document.createElement('button');
        recordButton.textContent = 'Start Recording';
        recordButton.classList.add('px-4', 'py-2', 'text-white', 'rounded');
        
        const uploadButton = document.createElement('button');
        uploadButton.textContent = 'Upload Video';
        uploadButton.style.display = 'none';
        uploadButton.classList.add('px-4', 'py-2', 'text-white', 'rounded', 'ml-2');

        let stream = null;
        
        recordButton.addEventListener('click', async function() {
            if (!mediaRecorder) {
                try {
                    stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
                    videoPreview.srcObject = stream;
                    videoPreview.play();
                    
                    mediaRecorder = new MediaRecorder(stream);
                    recordedChunks = [];
                    
                    mediaRecorder.ondataavailable = function(e) {
                        if (e.data.size > 0) {
                            recordedChunks.push(e.data);
                        }
                    };
                    
                    mediaRecorder.onstop = function() {
                        if (stream) {
                            stream.getTracks().forEach(track => track.stop());
                            stream = null;
                            videoPreview.srcObject = null;
                        }
                        uploadButton.style.display = 'inline-block';
                    };
                    
                    mediaRecorder.start();
                    recordButton.textContent = 'Stop Recording';
                    recordButton.classList.add('recording');
                    
                    // Auto-stop after 2 minutes
                    setTimeout(() => {
                        if (mediaRecorder && mediaRecorder.state === 'recording') {
                            mediaRecorder.stop();
                            recordButton.textContent = 'Start Recording';
                            recordButton.classList.remove('recording');
                            mediaRecorder = null;
                        }
                    }, 120000);
                    
                } catch (err) {
                    console.error('Error:', err);
                    addMessage('Error accessing camera: ' + err.message, 'bot');
                }
            } else {
                mediaRecorder.stop();
                recordButton.textContent = 'Start Recording';
                recordButton.classList.remove('recording');
                mediaRecorder = null;
            }
        });
        
        uploadButton.addEventListener('click', function() {
            if (recordedChunks.length === 0) {
                addMessage('No video recorded', 'bot');
                return;
            }
            
            const blob = new Blob(recordedChunks, { type: 'video/webm' });
            const formData = new FormData();
            formData.append('video', blob, 'recording.webm');
            
            fetch('/api/upload-video', {
                method: 'POST',
                body: formData
            })
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        addMessage(data.error, 'bot');
                    } else {
                        addMessage('Video uploaded successfully', 'bot');
                        sendMessage('Video uploaded');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    addMessage('Error uploading video', 'bot');
                });
        });
        
        videoDiv.appendChild(videoPreview);
        videoDiv.appendChild(recordButton);
        videoDiv.appendChild(uploadButton);
        return videoDiv;
    }

    sendButton.addEventListener('click', function() {
        sendMessage(userInput.value.trim());
    });

    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage(userInput.value.trim());
        }
    });

    // Start the conversation without showing user message
    sendMessage('', true);
});
