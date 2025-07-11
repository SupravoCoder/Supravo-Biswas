// Enhanced alert sound functionality for Bhukamp earthquake app

class EarthquakeAlert {
    constructor() {
        this.audioContext = null;
        this.isPlaying = false;
    }

    // Initialize audio context
    initAudio() {
        try {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        } catch (e) {
            console.warn("Web Audio API not supported");
        }
    }

    // Create earthquake alert sound using Web Audio API
    createAlertTone(frequency = 800, duration = 2000) {
        if (!this.audioContext) {
            this.initAudio();
        }

        if (this.audioContext && !this.isPlaying) {
            this.isPlaying = true;
            
            // Create oscillator for the main alert tone
            const oscillator = this.audioContext.createOscillator();
            const gainNode = this.audioContext.createGain();
            
            // Connect nodes
            oscillator.connect(gainNode);
            gainNode.connect(this.audioContext.destination);
            
            // Set up the alert pattern (emergency-like)
            oscillator.frequency.setValueAtTime(frequency, this.audioContext.currentTime);
            oscillator.frequency.exponentialRampToValueAtTime(frequency * 1.5, this.audioContext.currentTime + 0.1);
            oscillator.frequency.exponentialRampToValueAtTime(frequency, this.audioContext.currentTime + 0.2);
            
            // Volume envelope
            gainNode.gain.setValueAtTime(0, this.audioContext.currentTime);
            gainNode.gain.linearRampToValueAtTime(0.3, this.audioContext.currentTime + 0.01);
            gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + duration / 1000);
            
            // Start and stop
            oscillator.start(this.audioContext.currentTime);
            oscillator.stop(this.audioContext.currentTime + duration / 1000);
            
            // Reset playing state
            setTimeout(() => {
                this.isPlaying = false;
            }, duration);
        }
    }

    // Play multiple alert tones for high magnitude earthquakes
    playEmergencyAlert(magnitude = 5.0) {
        const alertCount = Math.min(Math.floor(magnitude), 8);
        
        for (let i = 0; i < alertCount; i++) {
            setTimeout(() => {
                this.createAlertTone(800 + (i * 100), 500);
            }, i * 600);
        }
    }

    // Simple beep for lower magnitude earthquakes
    playSimpleAlert() {
        this.createAlertTone(600, 1000);
    }
}

// Global alert instance
window.earthquakeAlert = new EarthquakeAlert();

// Function to be called from Streamlit
function playEarthquakeAlert(magnitude) {
    if (magnitude >= 6.0) {
        window.earthquakeAlert.playEmergencyAlert(magnitude);
    } else {
        window.earthquakeAlert.playSimpleAlert();
    }
}

// Auto-initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    window.earthquakeAlert.initAudio();
});
