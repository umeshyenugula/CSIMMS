let qrScanner = null;
let scannerActive = false;

// Start scanner
function startScanner() {
    if (scannerActive) return;

    scannerActive = true;

    qrScanner = new Html5Qrcode("qr-reader");

    const config = { fps: 10, qrbox: 250 };

    qrScanner.start(
        { facingMode: "environment" },
        config,
        (decodedText) => {
            // STOP SCANNING IMMEDIATELY
            stopScanner();

            // Lock UI
            document.getElementById("status").innerText = "Processing...";
            document.getElementById("status").style.color = "blue";

            // Verify QR code
            verifyCode(decodedText);
        },
        (error) => {
            // ignore scan errors
        }
    );
}

function stopScanner() {
    if (!qrScanner) return;
    qrScanner.stop().then(() => {
        scannerActive = false;
        qrScanner.clear();
    }).catch(err => {
        console.log("Scanner stop error:", err);
    });
}

// API Call
async function verifyCode(code) {
    try {
        let res = await fetch(`http://localhost:8000/verify/${code}`);
        let data = await res.json();

        handleResponse(data);

    } catch (err) {
        document.getElementById("status").innerText = "Server Error";
        document.getElementById("status").style.color = "red";
    }
}

function handleResponse(data) {
    // RESPONSE HANDLING
    if (data.status === "success") {
        document.getElementById("status").style.color = "green";
        document.getElementById("status").innerText =
            `✔ ${data.participant.name} → ${data.meal.toUpperCase()} Granted`;
    }
    else if (data.status === "already_taken") {
        document.getElementById("status").style.color = "orange";
        document.getElementById("status").innerText =
            `⚠ Already Taken Earlier`;
    }
    else if (data.status === "invalid_time") {
        document.getElementById("status").style.color = "red";
        document.getElementById("status").innerText =
            `❌ Not meal time currently`;
    }
    else {
        document.getElementById("status").style.color = "red";
        document.getElementById("status").innerText =
            "❌ Unknown Error";
    }

    // After showing result, enable "Scan Again" button
    document.getElementById("scanAgainBtn").style.display = "block";
}

// Button to restart scanning
function scanAgain() {
    document.getElementById("scanAgainBtn").style.display = "none";
    document.getElementById("status").innerText = "";
    startScanner();
}
