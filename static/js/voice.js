const voiceBtn = document.getElementById('voice-btn');
const voiceStatus = document.getElementById('voice-status');
let recognition;

if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.lang = 'he-IL';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onstart = function() {
        voiceBtn.classList.add('recording');
        voiceStatus.classList.remove('hidden');
        voiceStatus.textContent = 'מאזין... (דבר עכשיו)';
    };

    recognition.onresult = async function(event) {
        const text = event.results[0][0].transcript;
        voiceStatus.textContent = 'מעבד: "' + text + '"...';
        
        try {
            const response = await fetch('/api/voice_transaction', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ text: text })
            });
            
            const result = await response.json();
            
            if (result.success) {
                voiceStatus.textContent = 'נוספו ' + result.added + ' פעולות!';
                setTimeout(() => location.reload(), 1500);
            } else {
                voiceStatus.textContent = 'שגיאה: ' + (result.error || 'לא הצלחנו לפענח');
                setTimeout(() => voiceStatus.classList.add('hidden'), 3000);
            }
        } catch (e) {
            voiceStatus.textContent = 'שגיאת רשת';
            setTimeout(() => voiceStatus.classList.add('hidden'), 3000);
        }
        
        voiceBtn.classList.remove('recording');
    };

    recognition.onerror = function(event) {
        voiceBtn.classList.remove('recording');
        voiceStatus.textContent = 'שגיאת שמיעה: ' + event.error;
        setTimeout(() => voiceStatus.classList.add('hidden'), 3000);
    };

    recognition.onend = function() {
        voiceBtn.classList.remove('recording');
    };

    voiceBtn.addEventListener('click', () => {
        if (voiceBtn.classList.contains('recording')) {
            recognition.stop();
        } else {
            recognition.start();
        }
    });
} else {
    voiceBtn.style.display = 'none'; // Hide if not supported
    console.warn('Speech recognition not supported in this browser.');
}
