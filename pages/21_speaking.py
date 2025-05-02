import streamlit as st

# 페이지 설정
st.set_page_config(page_title="브라우저 TTS 애플리케이션", layout="wide")

# 제목
st.title("텍스트 음성 변환 (TTS) 애플리케이션")
st.write("브라우저의 Web Speech API를 사용하여 텍스트를 음성으로 변환합니다.")

# 텍스트 입력 영역
text_input = st.text_area("읽을 텍스트를 입력하세요:", height=150)

# 속도 조절
speed = st.slider("속도:", min_value=0.5, max_value=2.0, value=1.0, step=0.1)

# HTML 코드 생성
html_code = f"""
<div style="margin-top: 20px;">
    <button id="speak-button" style="background-color: #4CAF50; color: white; padding: 10px 20px; 
        border: none; border-radius: 4px; cursor: pointer; margin-right: 10px;">
        말하기
    </button>
    
    <button id="stop-button" style="background-color: #f44336; color: white; padding: 10px 20px; 
        border: none; border-radius: 4px; cursor: pointer;">
        중지
    </button>
    
    <div id="voice-selection" style="margin-top: 15px;">
        <label for="voice-select">음성 선택:</label>
        <select id="voice-select" style="padding: 5px; margin-left: 10px;"></select>
    </div>
</div>

<script>
    // 음성 목록
    let voices = [];
    let selectedVoice = null;
    
    // 음성 목록 로드
    function loadVoices() {{
        voices = window.speechSynthesis.getVoices();
        const voiceSelect = document.getElementById('voice-select');
        
        // 기존 옵션 제거
        voiceSelect.innerHTML = '';
        
        // 모든 음성 추가
        voices.forEach(voice => {{
            const option = document.createElement('option');
            option.value = voice.name;
            option.textContent = `${{voice.name}} (${{voice.lang}})`;
            voiceSelect.appendChild(option);
        }});
        
        // 한국어 또는 영어 음성 자동 선택
        let koreanVoice = voices.find(voice => voice.lang.includes('ko'));
        let englishVoice = voices.find(voice => voice.lang.includes('en'));
        
        if (koreanVoice) {{
            selectedVoice = koreanVoice;
            voiceSelect.value = koreanVoice.name;
        }} else if (englishVoice) {{
            selectedVoice = englishVoice;
            voiceSelect.value = englishVoice.name;
        }} else if (voices.length > 0) {{
            selectedVoice = voices[0];
            voiceSelect.value = voices[0].name;
        }}
    }}
    
    // 음성 변경 이벤트
    document.getElementById('voice-select').addEventListener('change', function() {{
        const selectedName = this.value;
        selectedVoice = voices.find(voice => voice.name === selectedName);
    }});
    
    // 말하기 버튼 클릭 이벤트
    document.getElementById('speak-button').addEventListener('click', function() {{
        if ('speechSynthesis' in window) {{
            // 이전 음성 취소
            window.speechSynthesis.cancel();
            
            // 텍스트 가져오기 - Streamlit에서 전달된 값 사용
            const text = {text_input!r};
            
            if (text.trim() !== "") {{
                // 음성 합성 객체 생성
                const utterance = new SpeechSynthesisUtterance(text);
                
                // 속도 설정 - Streamlit에서 전달된 값 사용
                utterance.rate = {speed};
                
                // 음성 설정
                if (selectedVoice) {{
                    utterance.voice = selectedVoice;
                }}
                
                // 음성 합성 시작
                window.speechSynthesis.speak(utterance);
            }} else {{
                alert("텍스트를 입력해주세요.");
            }}
        }} else {{
            alert("이 브라우저는 음성 합성을 지원하지 않습니다.");
        }}
    }});
    
    // 중지 버튼 클릭 이벤트
    document.getElementById('stop-button').addEventListener('click', function() {{
        if ('speechSynthesis' in window) {{
            window.speechSynthesis.cancel();
        }}
    }});
    
    // 페이지 로드 시 음성 목록 초기화
    if ('speechSynthesis' in window) {{
        // 일부 브라우저에서는 onvoiceschanged 이벤트가 발생하지 않을 수 있음
        if (speechSynthesis.onvoiceschanged !== undefined) {{
            speechSynthesis.onvoiceschanged = loadVoices;
        }}
        
        // onvoiceschanged 이벤트가 없는 경우를 대비해 직접 호출
        setTimeout(loadVoices, 500);
    }}
</script>
"""

# HTML 코드 삽입
st.components.v1.html(html_code, height=200)

# 정보 표시
st.info("""
이 애플리케이션은 브라우저의 Web Speech API를 사용합니다.
음성 품질과 사용 가능한 음성은 브라우저와 운영 체제에 따라 다릅니다.
Google Chrome에서 가장 잘 작동합니다.
""")

# 도움말
with st.expander("사용 방법"):
    st.write("""
    1. 텍스트 입력 영역에 변환할 텍스트를 입력합니다.
    2. 원하는 음성을 선택합니다 (한국어 음성이 있는 경우 자동으로 선택됩니다).
    3. 속도 슬라이더로 말하기 속도를 조절합니다.
    4. '말하기' 버튼을 클릭하여 음성을 재생합니다.
    5. '중지' 버튼을 클릭하여 재생을 중단합니다.
    """)