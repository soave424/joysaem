import streamlit as st

# 페이지 설정
st.set_page_config(page_title="TTS 애플리케이션", layout="wide")

# 제목
st.title("텍스트 음성 변환 (TTS) 애플리케이션")
st.write("브라우저의 Web Speech API를 사용하여, 텍스트를 음성으로 변환합니다.")

# 텍스트 입력 영역
text_input = st.text_area("읽을 텍스트를 입력하세요:", height=150)

# 속도 조절
speed = st.slider("속도:", min_value=0.5, max_value=2.0, value=1.0, step=0.1)

# JavaScript 코드 생성
js_code = f"""
<script>
function speak() {{
    if ('speechSynthesis' in window) {{
        // 이전 음성 취소
        window.speechSynthesis.cancel();
        
        // 텍스트 가져오기
        var text = "{text_input.replace('"', '\\"')}";
        
        if (text.trim() !== "") {{
            // 음성 합성 객체 생성
            var utterance = new SpeechSynthesisUtterance(text);
            
            // 속도 설정
            utterance.rate = {speed};
            
            // 사용 가능한 음성 가져오기
            var voices = window.speechSynthesis.getVoices();
            
            // 음성 선택 (가능하면 한국어 또는 영어 음성)
            for (var i = 0; i < voices.length; i++) {{
                if (voices[i].lang.includes('ko')) {{
                    utterance.voice = voices[i];
                    break;
                }}
                if (voices[i].lang.includes('en')) {{
                    utterance.voice = voices[i];
                }}
            }}
            
            // 음성 합성 시작
            window.speechSynthesis.speak(utterance);
        }}
    }} else {{
        alert("죄송합니다, 이 브라우저는 음성 합성을 지원하지 않습니다.");
    }}
}}

function stopSpeaking() {{
    if ('speechSynthesis' in window) {{
        window.speechSynthesis.cancel();
    }}
}}

// 음성 목록 로드 대기
if ('speechSynthesis' in window) {{
    if (speechSynthesis.onvoiceschanged !== undefined) {{
        speechSynthesis.onvoiceschanged = function() {{
            // 음성 목록이 로드됨
        }};
    }}
}}
</script>

<button onclick="speak()" style="padding: 10px 20px; background-color: #4CAF50; color: white; border: none; border-radius: 5px; cursor: pointer; margin-right: 10px;">
    말하기
</button>

<button onclick="stopSpeaking()" style="padding: 10px 20px; background-color: #f44336; color: white; border: none; border-radius: 5px; cursor: pointer;">
    중지
</button>
"""

# JavaScript 코드 실행
st.markdown(js_code, unsafe_allow_html=True)

# 정보 표시
st.info("""
이 애플리케이션은 브라우저의 Web Speech API를 사용합니다. 
음성은 사용자의 브라우저와 운영 체제에 설치된 음성에 따라 달라집니다.
Google Chrome 브라우저에서 가장 잘 작동합니다.
""")

# 사용 방법
with st.expander("사용 방법"):
    st.write("""
    1. 변환할 텍스트를 위의 텍스트 영역에 입력하세요.
    2. 슬라이더를 사용하여 말하기 속도를 조절하세요.
    3. '말하기' 버튼을 클릭하여 음성을 생성하고 재생하세요.
    4. '중지' 버튼을 클릭하여 현재 재생을 중지하세요.
    
    참고: 이 애플리케이션은 브라우저의 내장 TTS 기능을 사용하므로, 
    브라우저와 운영 체제에 따라 사용 가능한 음성과 품질이 달라질 수 있습니다.
    """)