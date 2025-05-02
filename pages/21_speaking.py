import streamlit as st

# Streamlit 페이지 설정
st.set_page_config(page_title="TTS 애플리케이션", layout="wide")

# 제목
st.title("텍스트 음성 변환 애플리케이션")

# HTML 코드 삽입
html_code = """
<div style="padding: 15px; border: 1px solid #ddd; border-radius: 5px;">
    <textarea id="text-to-speak" style="width: 100%; height: 150px; padding: 10px; margin-bottom: 15px;" placeholder="읽을 텍스트를 입력하세요..."></textarea>
    
    <!-- 버튼 및 컨트롤 -->
    <div style="margin-bottom: 15px;">
        <button id="speak-button" style="background-color: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; margin-right: 10px;">말하기</button>
        <button id="stop-button" style="background-color: #f44336; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer;">중지</button>
    </div>
    
    <div style="margin-bottom: 15px;">
        <label for="voice-select">음성 선택:</label>
        <select id="voice-select" style="padding: 5px; margin: 0 10px;"></select>
        
        <label for="speed">속도:</label>
        <input type="range" id="speed" min="0.5" max="2" value="1" step="0.1" style="vertical-align: middle;">
        <span id="speed-value">1.0</span>
    </div>
    
    <script>
        // JavaScript 코드 (앞서 제공한 HTML 파일의 스크립트와 동일)
        let voices = [];
        let selectedVoice = null;
        
        function loadVoices() {
            voices = window.speechSynthesis.getVoices();
            const voiceSelect = document.getElementById('voice-select');
            
            voiceSelect.innerHTML = '';
            
            const googleVoices = voices.filter(voice => voice.name.includes('Google') || voice.name.includes('Chrome'));
            const otherVoices = voices.filter(voice => !voice.name.includes('Google') && !voice.name.includes('Chrome'));
            
            googleVoices.forEach(voice => {
                const option = document.createElement('option');
                option.value = voice.name;
                option.textContent = `${voice.name} (${voice.lang})`;
                voiceSelect.appendChild(option);
            });
            
            if (googleVoices.length > 0 && otherVoices.length > 0) {
                const separator = document.createElement('option');
                separator.disabled = true;
                separator.textContent = '──────────';
                voiceSelect.appendChild(separator);
            }
            
            otherVoices.forEach(voice => {
                const option = document.createElement('option');
                option.value = voice.name;
                option.textContent = `${voice.name} (${voice.lang})`;
                voiceSelect.appendChild(option);
            });
            
            let koreanVoice = voices.find(voice => voice.lang.includes('ko'));
            let englishVoice = voices.find(voice => voice.lang.includes('en'));
            
            if (koreanVoice) {
                selectedVoice = koreanVoice;
                voiceSelect.value = koreanVoice.name;
            } else if (englishVoice) {
                selectedVoice = englishVoice;
                voiceSelect.value = englishVoice.name;
            } else if (voices.length > 0) {
                selectedVoice = voices[0];
                voiceSelect.value = voices[0].name;
            }
        }
        
        document.getElementById('voice-select').addEventListener('change', function() {
            const selectedName = this.value;
            selectedVoice = voices.find(voice => voice.name === selectedName);
        });
        
        document.getElementById('speed').addEventListener('input', function() {
            document.getElementById('speed-value').textContent = this.value;
        });
        
        document.getElementById('speak-button').addEventListener('click', function() {
            if ('speechSynthesis' in window) {
                window.speechSynthesis.cancel();
                
                const text = document.getElementById('text-to-speak').value;
                
                if (text.trim() !== "") {
                    const utterance = new SpeechSynthesisUtterance(text);
                    
                    utterance.rate = parseFloat(document.getElementById('speed').value);
                    
                    if (selectedVoice) {
                        utterance.voice = selectedVoice;
                    }
                    
                    window.speechSynthesis.speak(utterance);
                } else {
                    alert("텍스트를 입력해주세요.");
                }
            } else {
                alert("이 브라우저는 음성 합성을 지원하지 않습니다.");
            }
        });
        
        document.getElementById('stop-button').addEventListener('click', function() {
            if ('speechSynthesis' in window) {
                window.speechSynthesis.cancel();
            }
        });
        
        if ('speechSynthesis' in window) {
            if (speechSynthesis.onvoiceschanged !== undefined) {
                speechSynthesis.onvoiceschanged = loadVoices;
            }
            
            setTimeout(loadVoices, 500);
        } else {
            alert("이 브라우저는 음성 합성을 지원하지 않습니다.");
        }
    </script>
</div>
"""

# HTML 삽입 (높이를 적절히 조정)
st.components.v1.html(html_code, height=400)

# 사용 안내
st.info("""
이 애플리케이션은 브라우저의 Web Speech API를 사용합니다.
음성 품질과 사용 가능한 음성은 브라우저와 운영 체제에 따라 다릅니다.
Google Chrome에서 가장 잘 작동합니다.
""")

# 사용 방법
with st.expander("사용 방법"):
    st.write("""
    1. 텍스트 입력 영역에 변환할 텍스트를 입력합니다.
    2. 원하는 음성을 선택합니다 (한국어 음성이 있는 경우 자동으로 선택됩니다).
    3. 속도 슬라이더로 말하기 속도를 조절합니다.
    4. '말하기' 버튼을 클릭하여 음성을 재생합니다.
    5. '중지' 버튼을 클릭하여 재생을 중단합니다.
    """)