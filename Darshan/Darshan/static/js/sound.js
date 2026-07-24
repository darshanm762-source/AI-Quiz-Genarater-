/**
 * Sound Synthesizer Module (Web Audio API)
 * Plays UI audio effects without external MP3 dependencies.
 */
const SoundFx = (function () {
    let audioCtx = null;
    let isMuted = localStorage.getItem('ai_quiz_muted') === 'true';

    function getAudioContext() {
        if (!audioCtx) {
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            if (AudioContext) {
                audioCtx = new AudioContext();
            }
        }
        if (audioCtx && audioCtx.state === 'suspended') {
            audioCtx.resume();
        }
        return audioCtx;
    }

    function playTone(freq, type, duration, gainValue = 0.1) {
        if (isMuted) return;
        try {
            const ctx = getAudioContext();
            if (!ctx) return;

            const osc = ctx.createOscillator();
            const gain = ctx.createGain();

            osc.type = type;
            osc.frequency.setValueAtTime(freq, ctx.currentTime);

            gain.gain.setValueAtTime(gainValue, ctx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + duration);

            osc.connect(gain);
            gain.connect(ctx.destination);

            osc.start();
            osc.stop(ctx.currentTime + duration);
        } catch (e) {
            // Audio context failed or blocked by browser
        }
    }

    return {
        isMuted: () => isMuted,
        toggleMute: function () {
            isMuted = !isMuted;
            localStorage.setItem('ai_quiz_muted', isMuted);
            return isMuted;
        },
        playSelect: function () {
            playTone(440, 'sine', 0.08, 0.1);
        },
        playTimerTick: function () {
            playTone(600, 'triangle', 0.05, 0.05);
        },
        playTimerWarning: function () {
            playTone(880, 'sawtooth', 0.15, 0.15);
        },
        playSuccess: function () {
            if (isMuted) return;
            try {
                const ctx = getAudioContext();
                if (!ctx) return;
                [523.25, 659.25, 783.99, 1046.50].forEach((freq, idx) => {
                    setTimeout(() => playTone(freq, 'sine', 0.25, 0.15), idx * 100);
                });
            } catch (e) {}
        }
    };
})();
