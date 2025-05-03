import streamlit as st
import deepl

# Streamlit 페이지 설정
st.set_page_config(page_title="단어 학습 TTS 및 번역 애플리케이션", layout="wide")

# 제목
st.title("단어별 읽기 및 번역 애플리케이션")
st.write("텍스트를 입력하면 단어별로 클릭하여 발음을 듣고 번역을 확인할 수 있습니다.")

# DeepL API 초기화
try:
    auth_key = st.secrets["DeepL_API_Key"]
    translator = deepl.Translator(auth_key)
    deepl_available = True
except Exception as e:
    st.sidebar.error(f"DeepL API 연결 오류: {e}")
    deepl_available = False

# 단어 번역 함수
def translate_word(word):
    if not deepl_available:
        return "DeepL API 연결 오류"
    
    try:
        result = translator.translate_text(word, source_lang="EN", target_lang="KO")
        return result.text
    except Exception as e:
        return f"번역 오류: {e}"

# 캐싱을 사용한 번역 결과 저장
@st.cache_data(ttl=3600)
def get_cached_translation(word):
    return translate_word(word)

# 사이드바에 번역 결과 표시를 위한 상태 변수
if 'selected_word' not in st.session_state:
    st.session_state.selected_word = ""
    st.session_state.translation = ""

# HTML 코드 삽입
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
    
    <div id='word-container' style='margin-top: 20px; padding: 15px; border: 1px solid #eee; border-radius: 5px; min-height: 100px; line-height: 2;'>
        <!-- 여기에 단어 버튼이 동적으로 추가됩니다 -->
    </div>
    
    <script>
        // 전역 변수
        let voices = [];
        let selectedVoice = null;
        
        // 음성 목록 로드
        function loadVoices() {
            voices = window.speechSynthesis.getVoices();
            const voiceSelect = document.getElementById('voice-select');
            
            voiceSelect.innerHTML = '';
            
            // 영어 음성과 기타 음성 분류
            const englishVoices = voices.filter(voice => voice.lang.includes('en'));
            const otherVoices = voices.filter(voice => !voice.lang.includes('en'));
            
            // 영어 음성 먼저 추가
            englishVoices.forEach(voice => {
                const option = document.createElement('option');
                option.value = voice.name;
                option.textContent = voice.name + ' (' + voice.lang + ')';
                voiceSelect.appendChild(option);
            });
            
            // 구분선 추가
            if (englishVoices.length > 0 && otherVoices.length > 0) {
                const separator = document.createElement('option');
                separator.disabled = true;
                separator.textContent = '──────────';
                voiceSelect.appendChild(separator);
            }
            
            // 기타 음성 추가
            otherVoices.forEach(voice => {
                const option = document.createElement('option');
                option.value = voice.name;
                option.textContent = voice.name + ' (' + voice.lang + ')';
                voiceSelect.appendChild(option);
            });
            
            // 영어 음성 자동 선택
            if (englishVoices.length > 0) {
                selectedVoice = englishVoices[0];
                voiceSelect.value = englishVoices[0].name;
            } else if (voices.length > 0) {
                selectedVoice = voices[0];
                voiceSelect.value = voices[0].name;
            }
        }
        
        // 단어별로 분리
        function processText() {
            const text = document.getElementById('text-to-speak').value.trim();
            const wordContainer = document.getElementById('word-container');
            
            if (!text) {
                alert('텍스트를 입력해주세요.');
                return;
            }
            
            // 단어 컨테이너 초기화
            wordContainer.innerHTML = '';
            
            // 텍스트를 단어로 분리
            const words = text.split(/\\s+/);
            
            // 각 단어에 대한 버튼 생성
            words.forEach((word, index) => {
                const wordButton = document.createElement('span');
                
                // 단어에서 구두점 제거한 깨끗한 단어
                const cleanWord = word.replace(/[^a-zA-Z0-9\\u00C0-\\u017F]/g, '');
                
                wordButton.textContent = word;
                wordButton.style.display = 'inline-block';
                wordButton.style.margin = '0 5px 5px 0';
                wordButton.style.padding = '5px 10px';
                wordButton.style.backgroundColor = '#e0e0e0';
                wordButton.style.borderRadius = '3px';
                wordButton.style.cursor = 'pointer';
                wordButton.dataset.originalWord = word;
                wordButton.dataset.cleanWord = cleanWord;
                
                // 클릭 이벤트 추가
                wordButton.addEventListener('click', function() {
                    speakWord(this.dataset.originalWord);
                    highlightWord(this);
                    updateSelectedWord(this.dataset.cleanWord);
                });
                
                wordContainer.appendChild(wordButton);
                
                // 단어 사이에 공백 추가
                if (index < words.length - 1) {
                    const space = document.createTextNode(' ');
                    wordContainer.appendChild(space);
                }
            });
        }
        
        // 선택된 단어 강조 표시
        function highlightWord(element) {
            // 이전에 선택된 단어의 스타일 초기화
            const allWordButtons = document.querySelectorAll('#word-container span');
            allWordButtons.forEach(btn => {
                btn.style.backgroundColor = '#e0e0e0';
                btn.style.color = 'black';
            });
            
            // 현재 선택된 단어 강조
            element.style.backgroundColor = '#2196F3';
            element.style.color = 'white';
        }
        
        // Streamlit 세션 상태 업데이트
        function updateSelectedWord(word) {
            if (word && word.trim() !== '') {
                // Streamlit의 세션 상태 업데이트를 위한 URL 파라미터
                const url = new URL(window.location.href);
                url.searchParams.set('selected_word', word);
                
                // 페이지 새로고침 없이 URL 파라미터 업데이트
                fetch(url.toString(), {
                    method: 'GET',
                    headers: {
                        'Accept': 'application/json'
                    }
                });
                
                // 현재 URL 업데이트 (페이지 새로고침 없이)
                window.history.replaceState({}, '', url.toString());
            }
        }
        
        // 단어 발음
        function speakWord(word) {
            if ('speechSynthesis' in window) {
                window.speechSynthesis.cancel();
                
                if (word.trim() !== '') {
                    const utterance = new SpeechSynthesisUtterance(word);
                    
                    utterance.rate = parseFloat(document.getElementById('speed').value);
                    
                    if (selectedVoice) {
                        utterance.voice = selectedVoice;
                    }
                    
                    window.speechSynthesis.speak(utterance);
                }
            }
        }
        
        // 전체 텍스트 읽기
        function speakAll() {
            if ('speechSynthesis' in window) {
                window.speechSynthesis.cancel();
                
                const text = document.getElementById('text-to-speak').value;
                
                if (text.trim() !== '') {
                    const utterance = new SpeechSynthesisUtterance(text);
                    
                    utterance.rate = parseFloat(document.getElementById('speed').value);
                    
                    if (selectedVoice) {
                        utterance.voice = selectedVoice;
                    }
                    
                    window.speechSynthesis.speak(utterance);
                } else {
                    alert('텍스트를 입력해주세요.');
                }
            }
        }
        
        // 이벤트 리스너 설정
        document.getElementById('voice-select').addEventListener('change', function() {
            const selectedName = this.value;
            selectedVoice = voices.find(voice => voice.name === selectedName);
        });
        
        document.getElementById('speed').addEventListener('input', function() {
            document.getElementById('speed-value').textContent = this.value;
        });
        
        document.getElementById('process-button').addEventListener('click', processText);
        document.getElementById('speak-all-button').addEventListener('click', speakAll);
        document.getElementById('stop-button').addEventListener('click', function() {
            if ('speechSynthesis' in window) {
                window.speechSynthesis.cancel();
            }
        });
        
        // 초기화
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

# 선택된 단어 처리
selected_word = st.query_params.get("selected_word", "")
if selected_word and selected_word != st.session_state.selected_word:
    st.session_state.selected_word = selected_word
    st.session_state.translation = get_cached_translation(selected_word)

# HTML 삽입
st.components.v1.html(html_code, height=600)

# 선택한 단어와 번역 결과 표시
if st.session_state.selected_word:
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"### 선택한 단어")
        st.markdown(f"### **{st.session_state.selected_word}**")
    with col2:
        st.markdown(f"### 번역 결과")
        st.markdown(f"### **{st.session_state.translation}**")

# 사용 안내
st.info("""
이 애플리케이션은 단어별 학습을 돕기 위한 도구입니다.
텍스트를 입력하고 '단어 분리' 버튼을 클릭하면 각 단어를 클릭하여 발음을 듣고 한국어 번역을 확인할 수 있습니다.
DeepL API를 통해 영어 단어의 한국어 번역을 제공합니다.
Google Chrome에서 가장 잘 작동합니다.
""")

# 사용 방법
with st.expander("사용 방법"):
    st.write("""
    1. 텍스트 입력 영역에 영어 텍스트를 입력합니다.
    2. '단어 분리' 버튼을 클릭하여 텍스트를 단어별로 분리합니다.
    3. 개별 단어를 클릭하면 해당 단어의 발음을 듣고 한국어 번역을 확인할 수 있습니다.
    4. '전체 읽기' 버튼을 클릭하면 전체 텍스트를 읽습니다.
    5. '중지' 버튼을 클릭하여 음성을 중단합니다.
    6. 드롭다운 메뉴에서 다른 음성을 선택하거나 슬라이더로 속도를 조절할 수 있습니다.
    """)