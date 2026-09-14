document.addEventListener("DOMContentLoaded", () => {
    // 1. Get HTML elements by exact IDs
    const btnStart = document.getElementById("btn-start");
    const btnStop = document.getElementById("btn-stop");
    
    const statusSystem = document.getElementById("status-system");
    const statusCamera = document.getElementById("status-camera");
    const statusGesture = document.getElementById("status-gesture");
    
    const currentGesture = document.getElementById("current-gesture");
    const currentAction = document.getElementById("current-action");
    
    const videoFeed = document.getElementById("videofeed");

    /**
     * Safe helper to set text content without throwing errors if element is missing.
     */
    function safeSetText(element, text) {
        if (element) {
            element.textContent = text;
        }
    }

    /**
     * Updates all UI elements according to the backend system state.
     * @param {boolean} isActive - System operational state from Flask.
     */
    function updateUIState(isActive) {
        if (isActive) {
            // Status Updates
            safeSetText(statusSystem, "ACTIVE");
            safeSetText(statusCamera, "ON");
            safeSetText(statusGesture, "DETECTING");

            if (statusSystem) statusSystem.className = "status-active";

            // Button States
            if (btnStart) btnStart.disabled = true;
            if (btnStop) btnStop.disabled = false;

            // Video Feed Activation
            if (videoFeed) {
                videoFeed.src = "/video_feed?" + new Date().getTime();
                videoFeed.style.display = "block";
            }
        } else {
            // Status Updates
            safeSetText(statusSystem, "INACTIVE");
            safeSetText(statusCamera, "OFF");
            safeSetText(statusGesture, "WAITING");

            safeSetText(currentGesture, "None");
            safeSetText(currentAction, "None");

            if (statusSystem) statusSystem.className = "status-inactive";

            // Button States
            if (btnStart) btnStart.disabled = false;
            if (btnStop) btnStop.disabled = true;

            // Video Feed Deactivation
            if (videoFeed) {
                videoFeed.src = "";
                videoFeed.style.display = "none";
            }
        }
    }

    /**
     * Checks current backend state on page load.
     */
    async function checkBackendStatus() {
        try {
            const response = await fetch("/status");
            if (!response.ok) {
                throw new Error(`HTTP Error Status: ${response.status}`);
            }
            const data = await response.json();
            updateUIState(data.status === "active");
        } catch (error) {
            console.error("Error connecting to Flask backend /status:", error);
            updateUIState(false);
        }
    }

    /**
     * Triggers START gesture control via Flask POST /start.
     */
    async function handleStart() {
        try {
            const response = await fetch("/start", { method: "POST" });
            if (!response.ok) {
                throw new Error(`HTTP Error Status: ${response.status}`);
            }
            const data = await response.json();
            updateUIState(data.status === "active");
        } catch (error) {
            console.error("Error calling /start endpoint:", error);
            alert("Cannot communicate with Flask server. Ensure app.py is running on your machine.");
            updateUIState(false);
        }
    }

    /**
     * Triggers STOP gesture control via Flask POST /stop.
     */
    async function handleStop() {
        try {
            const response = await fetch("/stop", { method: "POST" });
            if (!response.ok) {
                throw new Error(`HTTP Error Status: ${response.status}`);
            }
            const data = await response.json();
            updateUIState(false);
        } catch (error) {
            console.error("Error calling /stop endpoint:", error);
            alert("Failed to send stop signal to server.");
            updateUIState(false);
        }
    }

    // 2. Attach Event Listeners
    if (btnStart) {
        btnStart.addEventListener("click", handleStart);
    }

    if (btnStop) {
        btnStop.addEventListener("click", handleStop);
    }

    // 3. Check system status when DOM is loaded
    checkBackendStatus();
});