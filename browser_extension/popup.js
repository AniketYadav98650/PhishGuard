
const messageInput = document.getElementById("message");
const analyzeButton = document.getElementById("analyzeButton");
const resultBox = document.getElementById("result");

const predictionText = document.getElementById("prediction");
const confidenceText = document.getElementById("confidence");
const explanationText = document.getElementById("explanation");

const urlRiskText = document.getElementById("urlRisk");
const urlFindingsList = document.getElementById("urlFindings");

// Load selected webpage text.
document.addEventListener("DOMContentLoaded", () => {
    chrome.storage.local.get(["selectedMessage"], (data) => {
        if (data.selectedMessage) {
            messageInput.value = data.selectedMessage;
            chrome.storage.local.remove("selectedMessage");
        }
    });
});

// Analyze using the existing Django ML API.
analyzeButton.addEventListener("click", async () => {
    const message = messageInput.value.trim();

    resultBox.classList.remove("hidden");

    if (!message) {
        predictionText.textContent = "Message required";
        confidenceText.textContent = "";
        explanationText.textContent = "Please enter a message.";
        urlRiskText.textContent = "";
        urlFindingsList.replaceChildren();
        return;
    }

    analyzeButton.disabled = true;
    analyzeButton.textContent = "Analyzing...";

    predictionText.textContent = "Analyzing...";
    confidenceText.textContent = "";
    explanationText.textContent = "";
    urlRiskText.textContent = "";
    urlFindingsList.replaceChildren();

    try {
        const response = await fetch(
            "http://127.0.0.1:8000/api/extension/analyze/",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ message })
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Analysis failed.");
        }

        // Display ML prediction.
        predictionText.textContent = data.label;
        confidenceText.textContent =
            `Confidence: ${data.confidence_percent}%`;

        predictionText.style.color =
            data.prediction === 1 ? "#dc2626" : "#16a34a";

        // Display LIME explanation.
        explanationText.textContent =
            data.lime_summary || "No explanation available.";

        // Display URL analysis.
        const urlAnalysis = data.url_analysis || {};

        if (urlAnalysis.urls_found) {
            urlRiskText.textContent =
                `Risk level: ${urlAnalysis.risk_level || "Not specified"}`;

            (urlAnalysis.findings || []).forEach((finding) => {
                const item = document.createElement("li");
                item.textContent = finding;
                urlFindingsList.appendChild(item);
            });

            if (!urlFindingsList.children.length) {
                urlFindingsList.textContent =
                    "No additional URL findings were returned.";
            }
        } else {
            urlRiskText.textContent = "No URL detected in this message.";
        }

    } catch (error) {
        predictionText.textContent = "Analysis error";
        confidenceText.textContent = "";
        explanationText.textContent = error.message;
        urlRiskText.textContent = "";
    } finally {
        analyzeButton.disabled = false;
        analyzeButton.textContent = "Analyze Message";
    }
});
