import streamlit as st
import pyttsx3
import tempfile
import os
import base64

def text_to_speech(text, voice_id=None, rate=150):
    """
    텍스트를 음성으로 변환하고 오디오 파일을 반환합니다.
    """
    # 임시 파일 생성
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
    temp_filename = temp_file.name
    temp_file.close()
    
    # TTS 엔진 초기화
    engine = pyttsx3.init()
    
    # 음성 속성 설정
    if voice_id:
        engine.setProperty('voice', voice_id)
    
    # 말하기 속도 설정 (기본값: 200)
    engine.setProperty('rate', rate)
    
    # 음성 파일 저장
    engine.save_to_file(text, temp_filename)
    engine.runAndWait()
    
    # 파일 읽기 및 base64로 인코딩
    with open(temp_filename, 'rb') as f:
        audio_bytes = f.read()
    
    # 임시 파일 삭제
    os.unlink(temp_filename)
    
    # base64로 인코딩하여 HTML 오디오 태그 생성
    audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
    audio_tag = f'<audio autoplay controls><source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3"></audio>'
    
    return audio_tag

def get_available_voices():
    """
    사용 가능한 음성 목록을 반환합니다.
    """
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    
    voice_dict = {}
    for voice in voices:
        # 음성 ID와 이름 저장
        voice_dict[f"{voice.name} ({voice.languages[0] if voice.languages else 'Unknown'})"] = voice.id
    
    return voice_dict

# 페이지 설정
st.set_page_config(page_title="TTS 애플리케이션", layout="wide")

# 제목 및 설명
st.title("텍스트 음성 변환 (TTS) 애플리케이션")
st.write("텍스트를 입력하고 음성으로 변환하세요.")

# 텍스트 입력 영역
text_input = st.text_area("읽을 텍스트를 입력하세요:", height=150)

# 음성 선택
try:
    voices = get_available_voices()
    voice_name = st.selectbox("음성 선택:", list(voices.keys()))
    voice_id = voices[voice_name]
except:
    st.warning("음성 목록을 가져오는 데 문제가 발생했습니다. 기본 음성이 사용됩니다.")
    voice_id = None
    voice_name = "기본 음성"

# 속도 조절
rate = st.slider("속도:", min_value=50, max_value=300, value=150, step=10)
st.write(f"현재 속도: {rate}")

# 버튼 행 생성
col1, col2 = st.columns(2)

# 말하기 버튼
if col1.button("말하기"):
    if text_input.strip():
        with st.spinner("음성을 생성하는 중..."):
            try:
                audio_html = text_to_speech(text_input, voice_id, rate)
                st.markdown(audio_html, unsafe_allow_html=True)
                
                # 세션 상태에 저장
                st.session_state['last_text'] = text_input
                st.session_state['last_voice'] = voice_id
                st.session_state['last_rate'] = rate
            except Exception as e:
                st.error(f"음성 생성 중 오류가 발생했습니다: {e}")
    else:
        st.error("말할 텍스트를 입력해주세요.")

# 중지 버튼 (Streamlit에서는 제한적으로 작동)
if col2.button("중지"):
    st.warning("오디오 재생이 중지되었습니다.")
    st.markdown('<audio controls></audio>', unsafe_allow_html=True)

# 정보 표시
st.subheader("사용 가능한 음성 정보")
st.info(f"""
현재 선택된 음성: {voice_name}
이 애플리케이션은 컴퓨터에 설치된 TTS 엔진을 사용합니다.
다른 음성이 필요한 경우 운영 체제 설정에서 추가 음성 팩을 설치할 수 있습니다.
인터넷 연결이 필요하지 않으며 로컬에서 모든 변환이 이루어집니다.
""")

# 사용 방법
with st.expander("사용 방법"):
    st.write("""
    1. 변환할 텍스트를 위의 텍스트 영역에 입력하세요.
    2. 드롭다운 메뉴에서 원하는 음성을 선택하세요.
    3. 슬라이더를 사용하여 말하기 속도를 조절하세요.
    4. '말하기' 버튼을 클릭하여 음성을 생성하고 재생하세요.
    5. '중지' 버튼을 클릭하여 현재 재생을 중지하세요.
    """)