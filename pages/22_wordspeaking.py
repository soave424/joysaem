import streamlit as st
import deepl
from streamlit.components.v1 import html

# Streamlit 설정
st.set_page_config(page_title="단어 학습 TTS + 번역", layout="wide")

# DeepL API 초기화
auth_key = st.secrets["DeepL_API_Key"]
translator = deepl.Translator(auth_key)

# 번역 함수 정의
def translate_word(word, target_lang="KO"):
    try:
        result = translator.translate_text(word, target_lang=target_lang)
        return result.text
    except Exception as e:
        return f"오류: {str(e)}"

# 상태 초기화
if "input_word" not in st.session_state:
    st.session_state.input_word = ""
    st.session_state.translated = ""
if "word_history" not in st.session_state:
    st.session_state.word_history = []

# 제목
st.title("📘 단어 학습 TTS + 번역 애플리케이션")

# 좌우로 화면 분할
col_left, col_right = st.columns(2, gap="large")

# 왼쪽: HTML + JS 삽입 (단어 분리 및 TTS 기능 포함)
with col_left:
    html_code = """
    <div style='padding: 15px; border: 1px solid #ddd; border-radius: 5px;'>
        <textarea id='text-to-speak' style='width: 100%; height: 150px; padding: 10px; margin-bottom: 15px;' placeholder='텍스트를 입력하고 단어 분리 버튼을 클릭하세요...'></textarea>

        <div style='margin-bottom: 15px;'>
            <button id='process-button' style='background-color: #2196F3; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; margin-right: 10px;'>단어 분리</button>
            <button id='speak-all-button' style='background-color: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; margin-right: 10px;'>전체 읽기</button>
            <button id='stop-button' style='background-color: #f44336; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer;'>중지</button>
        </div>

        <div style='margin-bottom: 15px;'>
            <label for='voice-select'>음성 선택:</label>
            <select id='voice-select' style='padding: 5px; margin: 0 10px;'></select>

            <label for='speed'>속도:</label>
            <input type='range' id='speed' min='0.5' max='2' value='1' step='0.1' style='vertical-align: middle;'>
            <span id='speed-value'>1.0</span>
        </div>

        <div id='word-container' style='margin-top: 20px; padding: 15px; border: 1px solid #eee; border-radius: 5px; min-height: 100px; line-height: 2;'></div>

        <script>
            let voices = [];
            let selectedVoice = null;

            function loadVoices() {
                voices = window.speechSynthesis.getVoices();
                const voiceSelect = document.getElementById('voice-select');
                voiceSelect.innerHTML = '';
                const englishVoices = voices.filter(voice => voice.lang.includes('en'));
                const otherVoices = voices.filter(voice => !voice.lang.includes('en'));

                englishVoices.forEach(voice => {
                    const option = document.createElement('option');
                    option.value = voice.name;
                    option.textContent = voice.name + ' (' + voice.lang + ')';
                    voiceSelect.appendChild(option);
                });

                if (englishVoices.length > 0 && otherVoices.length > 0) {
                    const separator = document.createElement('option');
                    separator.disabled = true;
                    separator.textContent = '──────────';
                    voiceSelect.appendChild(separator);
                }

                otherVoices.forEach(voice => {
                    const option = document.createElement('option');
                    option.value = voice.name;
                    option.textContent = voice.name + ' (' + voice.lang + ')';
                    voiceSelect.appendChild(option);
                });

                if (englishVoices.length > 0) {
                    selectedVoice = englishVoices[0];
                    voiceSelect.value = englishVoices[0].name;
                } else if (voices.length > 0) {
                    selectedVoice = voices[0];
                    voiceSelect.value = voices[0].name;
                }
            }

            function processText() {
                const text = document.getElementById('text-to-speak').value.trim();
                const wordContainer = document.getElementById('word-container');
                if (!text) {
                    alert('텍스트를 입력해주세요.');
                    return;
                }
                wordContainer.innerHTML = '';
                const words = text.split(/\s+/);
                words.forEach((word, index) => {
                    const wordButton = document.createElement('span');
                    const cleanWord = word.replace(/[^a-zA-Z0-9\u00C0-\u017F]/g, '');
                    wordButton.textContent = word;
                    wordButton.style.cssText = 'display:inline-block;margin:0 5px 5px 0;padding:5px 10px;background:#e0e0e0;border-radius:3px;cursor:pointer;';
                    wordButton.dataset.originalWord = cleanWord;
                    wordButton.addEventListener('click', function() {
                        speakWord(this.dataset.originalWord);
                        highlightWord(this);
                    });
                    wordContainer.appendChild(wordButton);
                    if (index < words.length - 1) wordContainer.appendChild(document.createTextNode(' '));
                });
            }

            function highlightWord(element) {
                document.querySelectorAll('#word-container span').forEach(btn => {
                    btn.style.backgroundColor = '#e0e0e0';
                    btn.style.color = 'black';
                });
                element.style.backgroundColor = '#2196F3';
                element.style.color = 'white';
            }

            function speakWord(word) {
                if ('speechSynthesis' in window) {
                    window.speechSynthesis.cancel();
                    if (word.trim() !== '') {
                        const utterance = new SpeechSynthesisUtterance(word);
                        utterance.rate = parseFloat(document.getElementById('speed').value);
                        if (selectedVoice) utterance.voice = selectedVoice;
                        window.speechSynthesis.speak(utterance);
                    }
                }
            }

            function speakAll() {
                if ('speechSynthesis' in window) {
                    window.speechSynthesis.cancel();
                    const text = document.getElementById('text-to-speak').value;
                    if (text.trim() !== '') {
                        const utterance = new SpeechSynthesisUtterance(text);
                        utterance.rate = parseFloat(document.getElementById('speed').value);
                        if (selectedVoice) utterance.voice = selectedVoice;
                        window.speechSynthesis.speak(utterance);
                    } else {
                        alert('텍스트를 입력해주세요.');
                    }
                }
            }

            document.getElementById('voice-select').addEventListener('change', function() {
                selectedVoice = voices.find(voice => voice.name === this.value);
            });

            document.getElementById('speed').addEventListener('input', function() {
                document.getElementById('speed-value').textContent = this.value;
            });

            document.getElementById('process-button').addEventListener('click', processText);
            document.getElementById('speak-all-button').addEventListener('click', speakAll);
            document.getElementById('stop-button').addEventListener('click', function() {
                window.speechSynthesis.cancel();
            });

            if ('speechSynthesis' in window) {
                if (speechSynthesis.onvoiceschanged !== undefined) {
                    speechSynthesis.onvoiceschanged = loadVoices;
                }
                setTimeout(loadVoices, 500);
            } else {
                alert('이 브라우저는 음성 합성을 지원하지 않습니다.');
            }
        </script>
    </div>
    """
    html(html_code, height=750)

# 오른쪽: 단어 학습 인터페이스
with col_right:
    st.markdown("### 📚 단어 학습")
    col1, col2 = st.columns([1, 2], gap="medium")
    with col1:
        st.markdown("<div style='margin-bottom: 10px'><b>단어 입력</b></div>", unsafe_allow_html=True)
        input_word = st.text_input("", key="input_word_field")
        if input_word and input_word != st.session_state.input_word:
            st.session_state.input_word = input_word
            st.session_state.translated = translate_word(input_word)
            if input_word not in st.session_state.word_history:
                st.session_state.word_history.append(input_word)

    with col2:
        st.markdown("<div style='margin-bottom: 10px'><b>번역 결과</b></div>", unsafe_allow_html=True)
        st.code("\n" + (st.session_state.translated or "(단어를 입력하면 번역이 표시됩니다)"), language="text")

    if st.session_state.word_history:
        st.markdown("### 🗂️ 학습한 단어 목록")
        for word in st.session_state.word_history:
            translated = translate_word(word)
            st.markdown(f"- `{word}` → {translated}")
        if st.button("🔄 목록 초기화"):
            st.session_state.word_history = []

    st.info("단어를 입력하거나 텍스트를 입력 후 단어를 분리해 발음할 수 있습니다. 번역은 직접 입력창을 통해 확인하세요. Chrome에서 최적 작동합니다.")