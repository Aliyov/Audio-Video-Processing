function showAudioSettings() {
    const audioOption = document.getElementById("audioOptions")?.value;
    const settingsDiv = document.getElementById("audioSettings");
    const addButton = document.getElementById("addButton");

    if (!settingsDiv || !addButton) {
        console.error("Required elements are missing from the DOM!");
        return;
    }

    // Clear previous settings
    settingsDiv.innerHTML = "";

    if (audioOption) {
        addButton.style.display = "inline";
        addButton.onclick = addAudioSetting;
    } else {
        addButton.style.display = "none";
    }

    if (audioOption === "phoneLikeFiltering") {
        addSettingInput("Side Gain (dB)");
        addSettingInput("Filter Order");

    } else if (audioOption === "gainCompressor") {
        addSettingInput("Compressor Threshold (start of non-linear region) (dB)");
        addSettingInput("Limiter Threshold (dB)");

    } else if (audioOption === "voiceEnhance") {
        addSettingInput("Pre-emphasis Alpha:");
        addSettingInput("High pass filter order:");

    } else if (audioOption === "denoiseDelay"){
        addSettingInput("Noise Power db:");
        addSettingInput("Delay ms:");
        addSettingInput("Delay gain (%):");
    
    } else if (audioOption === "carLikeFiltering") {
        addSettingInput("Side Gain (dB): ");
        addSettingInput("Filter Order:");
    }
}

function showVideoSettings() {
    const videoOption = document.getElementById("videoOptions").value;
    const settingsDiv = document.getElementById("audioSettings");
    const addButton = document.getElementById("addButton");

    settingsDiv.innerHTML = "";

    if (videoOption) {
        addButton.style.display = "inline";
        addButton.onclick = addVideoSetting; // Set handler for video
    } else {
        addButton.style.display = "none";
    }

    const addSettingInput = (labelText) => {
        const container = document.createElement("div");
        container.className = "setting-container";

        const label = document.createElement("label");
        label.textContent = labelText + ": ";
        container.appendChild(label);

        const input = document.createElement("input");
        input.type = "text";
        input.className = "video-setting";
        container.appendChild(input);

        settingsDiv.appendChild(container);
    };

    if (videoOption === "frameIncrease") {
        addSettingInput("Target FPS");
    } else if (videoOption === "upscale") {
        addSettingInput("Height");
        addSettingInput("Width");
    }
}

function addSettingInput(labelText) {
    const container = document.createElement("div");
    container.style.marginBottom = "10px";

    const label = document.createElement("label");
    label.textContent = labelText + ": ";
    container.appendChild(label);

    const input = document.createElement("input");
    input.type = "text";
    input.className = "audio-setting";
    container.appendChild(input);

    document.getElementById("audioSettings").appendChild(container);
}

function updateFileName() {
    const input = document.getElementById('videoFile');
    const fileName = document.getElementById('fileName');
    fileName.textContent = input.files.length > 0 ? input.files[0].name : 'No file chosen';
}

function addAudioSetting() {
    const audioOption = document.getElementById("audioOptions").value;
    const settingsInputs = document.querySelectorAll(".audio-setting");
    const values = [];

    settingsInputs.forEach((input) => {
        values.push(input.value);
    });

    // Format for the list item
    let listItemText = `${audioOption.toUpperCase()} | Settings: ${values.join(", ")}`;

    // Add to the list
    const listItem = document.createElement("li");
    listItem.textContent = listItemText;
    document.getElementById("processingList").appendChild(listItem);

    // Clear the settings and reset selection
    document.getElementById("audioOptions").value = "";
    document.getElementById("audioSettings").innerHTML = "";
    document.getElementById("addButton").style.display = "none";

    updateAddButtonVisibility();
}

function addVideoSetting(){
    const videoOption = document.getElementById("videoOptions").value;
    const settingsInputs = document.querySelectorAll(".video-setting");
    const values = [];

    settingsInputs.forEach((input) => {
        values.push(input.value);
    });

    // Format for the list item
    let listItemText = `${videoOption.toUpperCase()} | Settings: ${values.join(", ")}`;

    // Add to the list
    const listItem = document.createElement("li");
    listItem.textContent = listItemText;
    document.getElementById("processingList").appendChild(listItem);

    // Clear the settings and reset selection
    document.getElementById("audioOptions").value = "";
    document.getElementById("audioSettings").innerHTML = "";
    document.getElementById("addButton").style.display = "none";

    updateAddButtonVisibility();
}

function cleanProcessingList() {
    // Clear the processing list
    const processingList = document.getElementById("processingList");
    processingList.innerHTML = "";

    // Update button visibility
    updateAddButtonVisibility();
}

function updateAddButtonVisibility() {
    const processingList = document.getElementById("processingList");
    const addButton = document.getElementById("addButton");
    const cleanButton = document.getElementById("cleanButton");

    // Show the "Add" button only if there is at least one item in the list
    if (processingList.children.length > 0) {
        addButton.style.display = "inline";
        cleanButton.style.display = "inline";  // Show the "Clean" button
    } else {
        addButton.style.display = "none";
        cleanButton.style.display = "none";  // Hide the "Clean" button
    }
}

function deleteFile() {
    fetch("/delete", {
        method: "POST"
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            alert(data.message);
            // Clear file input
            const fileInput = document.getElementById("videoFile");
            if (fileInput) {
                fileInput.value = '';
            }
        } else {
            alert(data.error);
        }
    })
    .catch(error => {
        console.error("Error:", error);
        alert("An error occurred while deleting the file.");
    });
}

function processFile() {
    const fileInput = document.getElementById("videoFile");
    
    if (!fileInput || !fileInput.files.length) {
        alert("Please upload a file first!");
        return;
    }

    const file = fileInput.files[0];
    alert("Processing file: " + file.name);
    //sendVideoNameToBackEnd();
    sendSettingsToBackend();
}

function uploadButton() {
    const fileInput = document.getElementById("videoFile");
    const file = fileInput.files[0];

    if (!file) {
        alert("Please select a video file first.");
        return;
    }

    const formData = new FormData();
    formData.append("video", file); // key must match the Flask 'request.files' key

    fetch("/uploads", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            alert(data.message);
        } else if (data.error) {
            alert("Error: " + data.error);
        }
    })
    .catch(error => {
        console.error("Upload failed:", error);
        alert("An error occurred during upload.");
    });
}

function sendSettingsToBackend() {
    const listItems = document.querySelectorAll("#processingList li");
    const settingsData = [];

    // Collect list items text
    listItems.forEach(item => {
        settingsData.push(item.textContent);
    });

    // Get selected video filename
    const fileInput = document.getElementById("videoFile");
    const videoFile = fileInput.files[0];
    const videoName = videoFile ? videoFile.name : "";

    // Prepare data payload
    const dataToSend = {
        settings: settingsData,
        videoName: videoName
    };

    // Send JSON to backend
    fetch('/settingsSend', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(dataToSend),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('Success:', data);
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function playVideo() {
    var video = document.getElementById("finalVideo");
    video.load(); 
    video.play();
}




