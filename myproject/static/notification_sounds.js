/**
 * 🔊 BHUKAMP EARTHQUAKE NOTIFICATION SOUNDS
 * Professional audio notification system for earthquake alerts
 * Supports multiple alert types with appropriate sound levels
 */

class EarthquakeNotificationSounds {
    constructor() {
        this.audioContext = null;
        this.sounds = {};
        this.volume = 0.7;
        this.isEnabled = true;
        
        // Initialize audio context
        this.initAudioContext();
        
        // Create notification sounds
        this.createSounds();
        
        // Load user preferences
        this.loadPreferences();
    }

    /**
     * Initialize Web Audio API context
     */
    initAudioContext() {
        try {
            // Create audio context (handles browser compatibility)
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            console.log('🔊 Audio context initialized for earthquake notifications');
        } catch (error) {
            console.warn('⚠️ Audio not supported in this browser:', error);
            this.isEnabled = false;
        }
    }

    /**
     * Create different notification sounds for different alert types
     */
    createSounds() {
        if (!this.audioContext) return;

        // 🚨 HIGH RISK - Urgent alarm sound
        this.sounds.highRisk = this.createUrgentAlarm();
        
        // ⚠️ MEDIUM RISK - Warning beep sequence  
        this.sounds.mediumRisk = this.createWarningBeeps();
        
        // ℹ️ LOW RISK - Gentle notification
        this.sounds.lowRisk = this.createGentleNotification();
        
        // 📅 DAILY SUMMARY - Soft chime
        this.sounds.dailySummary = this.createSoftChime();
        
        // ✅ SUCCESS - Confirmation sound
        this.sounds.success = this.createSuccessSound();
        
        // ❌ ERROR - Error sound
        this.sounds.error = this.createErrorSound();
        
        console.log('🎵 Earthquake notification sounds created');
    }

    /**
     * Create urgent alarm for high-risk earthquakes
     */
    createUrgentAlarm() {
        return (duration = 1.5) => {
            if (!this.audioContext || !this.isEnabled) return;

            const oscillator1 = this.audioContext.createOscillator();
            const oscillator2 = this.audioContext.createOscillator();
            const gainNode = this.audioContext.createGain();
            
            // Create siren-like effect with two frequencies
            oscillator1.frequency.setValueAtTime(800, this.audioContext.currentTime);
            oscillator1.frequency.exponentialRampToValueAtTime(1200, this.audioContext.currentTime + 0.5);
            oscillator1.frequency.exponentialRampToValueAtTime(800, this.audioContext.currentTime + 1.0);
            
            oscillator2.frequency.setValueAtTime(600, this.audioContext.currentTime);
            oscillator2.frequency.exponentialRampToValueAtTime(1000, this.audioContext.currentTime + 0.5);
            oscillator2.frequency.exponentialRampToValueAtTime(600, this.audioContext.currentTime + 1.0);
            
            // Volume envelope for urgency
            gainNode.gain.setValueAtTime(0, this.audioContext.currentTime);
            gainNode.gain.linearRampToValueAtTime(this.volume, this.audioContext.currentTime + 0.1);
            gainNode.gain.linearRampToValueAtTime(this.volume * 0.8, this.audioContext.currentTime + duration - 0.1);
            gainNode.gain.linearRampToValueAtTime(0, this.audioContext.currentTime + duration);
            
            oscillator1.connect(gainNode);
            oscillator2.connect(gainNode);
            gainNode.connect(this.audioContext.destination);
            
            oscillator1.start(this.audioContext.currentTime);
            oscillator2.start(this.audioContext.currentTime);
            oscillator1.stop(this.audioContext.currentTime + duration);
            oscillator2.stop(this.audioContext.currentTime + duration);
        };
    }

    /**
     * Create warning beeps for medium-risk earthquakes
     */
    createWarningBeeps() {
        return (duration = 1.0) => {
            if (!this.audioContext || !this.isEnabled) return;

            const beepCount = 3;
            const beepDuration = 0.15;
            const beepInterval = 0.25;
            
            for (let i = 0; i < beepCount; i++) {
                const startTime = this.audioContext.currentTime + (i * beepInterval);
                
                const oscillator = this.audioContext.createOscillator();
                const gainNode = this.audioContext.createGain();
                
                oscillator.frequency.setValueAtTime(750, startTime);
                oscillator.type = 'square';
                
                gainNode.gain.setValueAtTime(0, startTime);
                gainNode.gain.linearRampToValueAtTime(this.volume * 0.7, startTime + 0.02);
                gainNode.gain.linearRampToValueAtTime(0, startTime + beepDuration);
                
                oscillator.connect(gainNode);
                gainNode.connect(this.audioContext.destination);
                
                oscillator.start(startTime);
                oscillator.stop(startTime + beepDuration);
            }
        };
    }

    /**
     * Create gentle notification for low-risk earthquakes
     */
    createGentleNotification() {
        return (duration = 0.8) => {
            if (!this.audioContext || !this.isEnabled) return;

            const oscillator = this.audioContext.createOscillator();
            const gainNode = this.audioContext.createGain();
            
            oscillator.frequency.setValueAtTime(440, this.audioContext.currentTime);
            oscillator.frequency.exponentialRampToValueAtTime(550, this.audioContext.currentTime + duration / 2);
            oscillator.frequency.exponentialRampToValueAtTime(440, this.audioContext.currentTime + duration);
            oscillator.type = 'sine';
            
            gainNode.gain.setValueAtTime(0, this.audioContext.currentTime);
            gainNode.gain.linearRampToValueAtTime(this.volume * 0.4, this.audioContext.currentTime + 0.1);
            gainNode.gain.linearRampToValueAtTime(0, this.audioContext.currentTime + duration);
            
            oscillator.connect(gainNode);
            gainNode.connect(this.audioContext.destination);
            
            oscillator.start(this.audioContext.currentTime);
            oscillator.stop(this.audioContext.currentTime + duration);
        };
    }

    /**
     * Create soft chime for daily summaries
     */
    createSoftChime() {
        return (duration = 1.2) => {
            if (!this.audioContext || !this.isEnabled) return;

            const frequencies = [523.25, 659.25, 783.99]; // C5, E5, G5 chord
            
            frequencies.forEach((freq, index) => {
                const oscillator = this.audioContext.createOscillator();
                const gainNode = this.audioContext.createGain();
                
                oscillator.frequency.setValueAtTime(freq, this.audioContext.currentTime);
                oscillator.type = 'sine';
                
                const startTime = this.audioContext.currentTime + (index * 0.1);
                gainNode.gain.setValueAtTime(0, startTime);
                gainNode.gain.linearRampToValueAtTime(this.volume * 0.3, startTime + 0.1);
                gainNode.gain.exponentialRampToValueAtTime(0.001, startTime + duration);
                
                oscillator.connect(gainNode);
                gainNode.connect(this.audioContext.destination);
                
                oscillator.start(startTime);
                oscillator.stop(startTime + duration);
            });
        };
    }

    /**
     * Create success confirmation sound
     */
    createSuccessSound() {
        return (duration = 0.6) => {
            if (!this.audioContext || !this.isEnabled) return;

            const oscillator = this.audioContext.createOscillator();
            const gainNode = this.audioContext.createGain();
            
            oscillator.frequency.setValueAtTime(523.25, this.audioContext.currentTime); // C5
            oscillator.frequency.linearRampToValueAtTime(783.99, this.audioContext.currentTime + duration / 2); // G5
            oscillator.type = 'sine';
            
            gainNode.gain.setValueAtTime(0, this.audioContext.currentTime);
            gainNode.gain.linearRampToValueAtTime(this.volume * 0.5, this.audioContext.currentTime + 0.05);
            gainNode.gain.exponentialRampToValueAtTime(0.001, this.audioContext.currentTime + duration);
            
            oscillator.connect(gainNode);
            gainNode.connect(this.audioContext.destination);
            
            oscillator.start(this.audioContext.currentTime);
            oscillator.stop(this.audioContext.currentTime + duration);
        };
    }

    /**
     * Create error sound
     */
    createErrorSound() {
        return (duration = 0.5) => {
            if (!this.audioContext || !this.isEnabled) return;

            const oscillator = this.audioContext.createOscillator();
            const gainNode = this.audioContext.createGain();
            
            oscillator.frequency.setValueAtTime(200, this.audioContext.currentTime);
            oscillator.frequency.linearRampToValueAtTime(150, this.audioContext.currentTime + duration);
            oscillator.type = 'sawtooth';
            
            gainNode.gain.setValueAtTime(0, this.audioContext.currentTime);
            gainNode.gain.linearRampToValueAtTime(this.volume * 0.6, this.audioContext.currentTime + 0.05);
            gainNode.gain.linearRampToValueAtTime(0, this.audioContext.currentTime + duration);
            
            oscillator.connect(gainNode);
            gainNode.connect(this.audioContext.destination);
            
            oscillator.start(this.audioContext.currentTime);
            oscillator.stop(this.audioContext.currentTime + duration);
        };
    }

    /**
     * Play notification sound based on alert type
     */
    playNotification(alertType, customDuration = null) {
        if (!this.isEnabled) {
            console.log('🔇 Audio notifications disabled');
            return;
        }

        // Resume audio context if suspended (required by some browsers)
        if (this.audioContext && this.audioContext.state === 'suspended') {
            this.audioContext.resume();
        }

        const soundMap = {
            'high_risk': 'highRisk',
            'medium_risk': 'mediumRisk', 
            'low_risk': 'lowRisk',
            'daily_summary': 'dailySummary',
            'success': 'success',
            'error': 'error'
        };

        const soundKey = soundMap[alertType] || 'mediumRisk';
        
        if (this.sounds[soundKey]) {
            console.log(`🔊 Playing ${alertType} notification sound`);
            this.sounds[soundKey](customDuration);
        } else {
            console.warn(`⚠️ Sound not found for alert type: ${alertType}`);
        }
    }

    /**
     * Set volume (0.0 to 1.0)
     */
    setVolume(volume) {
        this.volume = Math.max(0, Math.min(1, volume));
        this.savePreferences();
        console.log(`🔊 Volume set to ${Math.round(this.volume * 100)}%`);
    }

    /**
     * Enable/disable sounds
     */
    setEnabled(enabled) {
        this.isEnabled = enabled;
        this.savePreferences();
        console.log(`🔊 Earthquake sounds ${enabled ? 'enabled' : 'disabled'}`);
    }

    /**
     * Test all notification sounds
     */
    testAllSounds() {
        console.log('🎵 Testing all earthquake notification sounds...');
        
        const tests = [
            { type: 'success', delay: 0, label: 'Success' },
            { type: 'low_risk', delay: 1000, label: 'Low Risk' },
            { type: 'medium_risk', delay: 2500, label: 'Medium Risk' },
            { type: 'high_risk', delay: 4000, label: 'High Risk (Urgent)' },
            { type: 'daily_summary', delay: 6000, label: 'Daily Summary' },
            { type: 'error', delay: 8000, label: 'Error' }
        ];

        tests.forEach(test => {
            setTimeout(() => {
                console.log(`🔊 Testing: ${test.label}`);
                this.playNotification(test.type);
            }, test.delay);
        });
    }

    /**
     * Save user preferences to localStorage
     */
    savePreferences() {
        try {
            const preferences = {
                volume: this.volume,
                enabled: this.isEnabled
            };
            localStorage.setItem('earthquakeSoundPreferences', JSON.stringify(preferences));
        } catch (error) {
            console.warn('⚠️ Could not save sound preferences:', error);
        }
    }

    /**
     * Load user preferences from localStorage
     */
    loadPreferences() {
        try {
            const stored = localStorage.getItem('earthquakeSoundPreferences');
            if (stored) {
                const preferences = JSON.parse(stored);
                this.volume = preferences.volume || 0.7;
                this.isEnabled = preferences.enabled !== false; // Default to enabled
            }
        } catch (error) {
            console.warn('⚠️ Could not load sound preferences:', error);
        }
    }

    /**
     * Show audio control panel
     */
    showControlPanel() {
        const panel = document.createElement('div');
        panel.className = 'earthquake-audio-controls';
        panel.innerHTML = `
            <div style="
                position: fixed; 
                top: 20px; 
                right: 20px; 
                background: #2c3e50; 
                color: white; 
                padding: 15px; 
                border-radius: 10px; 
                box-shadow: 0 4px 8px rgba(0,0,0,0.3);
                z-index: 10000;
                font-family: Arial, sans-serif;
                min-width: 250px;
            ">
                <h4 style="margin: 0 0 10px 0; color: #e74c3c;">🔊 Earthquake Audio Controls</h4>
                
                <div style="margin: 10px 0;">
                    <label style="display: block; margin-bottom: 5px;">
                        <input type="checkbox" ${this.isEnabled ? 'checked' : ''} onchange="earthquakeSounds.setEnabled(this.checked)">
                        Enable Notification Sounds
                    </label>
                </div>
                
                <div style="margin: 10px 0;">
                    <label style="display: block; margin-bottom: 5px;">Volume: ${Math.round(this.volume * 100)}%</label>
                    <input type="range" min="0" max="100" value="${this.volume * 100}" 
                           style="width: 100%;" 
                           oninput="earthquakeSounds.setVolume(this.value / 100)">
                </div>
                
                <div style="margin: 15px 0;">
                    <button onclick="earthquakeSounds.testAllSounds()" 
                            style="background: #3498db; color: white; border: none; padding: 8px 12px; border-radius: 5px; cursor: pointer; margin-right: 5px;">
                        🎵 Test Sounds
                    </button>
                    <button onclick="this.parentElement.parentElement.remove()" 
                            style="background: #e74c3c; color: white; border: none; padding: 8px 12px; border-radius: 5px; cursor: pointer;">
                        ✕ Close
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(panel);
        
        // Auto-remove after 30 seconds
        setTimeout(() => {
            if (panel.parentElement) {
                panel.remove();
            }
        }, 30000);
    }
}

// Create global instance
const earthquakeSounds = new EarthquakeNotificationSounds();

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = EarthquakeNotificationSounds;
}

// Add to window for global access
window.earthquakeSounds = earthquakeSounds;

console.log('🔊 Earthquake notification sound system loaded and ready!');
console.log('Usage: earthquakeSounds.playNotification("high_risk") or earthquakeSounds.showControlPanel()');
