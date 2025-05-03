import streamlit as st
import urllib.request
import urllib.parse
import json
import time
import random
import deepl

# Streamlit 페이지 설정
st.set_page_config(page_title="단어 학습 TTS 애플리케이션", layout="wide")

# 제목
st.title("단어별 읽기 및 의미 확인 애플리케이션")
st.write("텍스트를 입력하면 단어별로 클릭하여 발음을 듣고 의미를 확인할 수 있습니다.")

# DeepL API를 사용한 단어 번역 함수
def translate_word(word, context=None):
    try:
        # 환경 변수에서 API 키 가져오기
        auth_key = st.secrets["DeepL_API_Key"]
        
        # DeepL 라이브러리 사용
        translator = deepl.Translator(auth_key)
        
        # 번역 요청
        result = translator.translate_text(
            word,
            source_lang="EN",
            target_lang="KO",
            context=context
        )
        
        return result.text
    except Exception as e:
        return f"오류 발생: {str(e)}"

# 캐싱을 사용한 번역 결과 저장
@st.cache_data(ttl=3600)
def get_cached_translation(word, context=None):
    return translate_word(word, context)

# 백엔드 API 엔드포인트 (단어 번역)
word_param = st.query_params.get("word", "")
context_param = st.query_params.get("context", "")

if word_param:
    translation = get_cached_translation(word_param, context_param)
    st.session_state.last_word = word_param
    st.session_state.last_translation = translation

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
    
    <div id='word-info' style='margin-top: 20px; display: none; padding: 15px; background-color: #f9f9f9; border-radius: 5px;'>
        <h3 id='selected-word' style='margin-top: 0; color: #333;'></h3>
        <div id='word-meaning'></div>
        <div id='loading-translation' style='display: none; margin-top: 10px;'>번역 중...</div>
    </div>
    
    <script>
        // 전역 변수
        let voices = [];
        let selectedVoice = null;
        let originalText = '';
        
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
            
            // 현재 텍스트 저장 (컨텍스트로 사용)
            originalText = text;
            
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
                wordButton.dataset.word = cleanWord;
                wordButton.dataset.originalWord = word;
                
                // 클릭 이벤트 추가
                wordButton.addEventListener('click', function() {
                    speakWord(this.dataset.originalWord);
                    showWordInfo(this.dataset.word, this);
                });
                
                wordContainer.appendChild(wordButton);
                
                // 단어 사이에 공백 추가
                if (index < words.length - 1) {
                    const space = document.createTextNode(' ');
                    wordContainer.appendChild(space);
                }
            });
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
        
        // 단어 정보 표시
        async function showWordInfo(word, element) {
            if (!word || word.trim() === '') return;
            
            const wordInfoDiv = document.getElementById('word-info');
            const selectedWordHeading = document.getElementById('selected-word');
            const wordMeaningDiv = document.getElementById('word-meaning');
            const loadingDiv = document.getElementById('loading-translation');
            
            // 이전에 선택된 단어의 스타일 초기화
            const allWordButtons = document.querySelectorAll('#word-container span');
            allWordButtons.forEach(btn => {
                btn.style.backgroundColor = '#e0e0e0';
                btn.style.color = 'black';
            });
            
            // 현재 선택된 단어 강조
            element.style.backgroundColor = '#2196F3';
            element.style.color = 'white';
            
            // 단어 정보 영역 표시
            wordInfoDiv.style.display = 'block';
            selectedWordHeading.textContent = word;
            
            // 로딩 표시
            wordMeaningDiv.innerHTML = '';
            loadingDiv.style.display = 'block';
            
            // 현재 URL에 쿼리 파라미터로 단어와 컨텍스트 추가
            const url = new URL(window.location.href);
            url.searchParams.set('word', word);
            url.searchParams.set('context', originalText);
            
            // Streamlit 앱 상태 업데이트 (페이지 새로고침 없이)
            try {
                const response = await fetch(url.toString(), {
                    method: 'GET',
                    headers: {
                        'Accept': 'application/json'
                    }
                });
                
                // 응답 확인
                if (response.ok) {
                    try {
                        const result = await response.json();
                        loadingDiv.style.display = 'none';
                        
                        if (result && result.translation) {
                            wordMeaningDiv.innerHTML = `
                                <p style='font-size: 16px; margin-bottom: 5px;'><strong>의미:</strong></p>
                                <p style='font-size: 15px;'>${result.translation}</p>
                                <p style='font-size: 12px; color: #666;'>(DeepL API로 번역된 결과입니다)</p>
                            `;
                        } else {
                            wordMeaningDiv.innerHTML = `
                                <p>단어의 의미를 찾을 수 없습니다.</p>
                                <p style='font-size: 14px; color: #666;'>다른 단어를 시도해보세요.</p>
                            `;
                        }
                    } catch (error) {
                        // JSON 파싱 오류
                        checkLastTranslation(word);
                    }
                } else {
                    // HTTP 오류
                    checkLastTranslation(word);
                }
            } catch (error) {
                // 네트워크 오류
                checkLastTranslation(word);
            }
        }
        
        // 마지막 번역 결과 확인 (세션 상태)
        function checkLastTranslation(word) {
            const loadingDiv = document.getElementById('loading-translation');
            const wordMeaningDiv = document.getElementById('word-meaning');
            
            loadingDiv.style.display = 'none';
            
            wordMeaningDiv.innerHTML = `
                <p>번역 서비스에 접근할 수 없습니다.</p>
                <p style='font-size: 14px; color: #666;'>잠시 후 다시 시도해보세요.</p>
            `;
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

# 세션 상태에 마지막 번역 결과가 있으면 사이드바에 표시
if 'last_word' in st.session_state and 'last_translation' in st.session_state:
    with st.sidebar:
        st.write(f"**마지막 검색 단어:** {st.session_state.last_word}")
        st.write(f"**번역 결과:** {st.session_state.last_translation}")

# HTML 삽입
st.components.v1.html(html_code, height=700)

# 사용 안내
st.info("""
이 애플리케이션은 단어별 학습을 돕기 위한 도구입니다.
텍스트를 입력하고 '단어 분리' 버튼을 클릭하면 각 단어를 클릭하여 발음을 듣고 의미를 확인할 수 있습니다.
DeepL API를 통해 영어 단어의 한국어 의미를 제공합니다.
Google Chrome에서 가장 잘 작동합니다.
""")

# 사용 방법
with st.expander("사용 방법"):
    st.write("""
    1. 텍스트 입력 영역에 영어 텍스트를 입력합니다.
    2. '단어 분리' 버튼을 클릭하여 텍스트를 단어별로 분리합니다.
    3. 개별 단어를 클릭하면 해당 단어의 발음을 듣고 의미를 확인할 수 있습니다.
    4. '전체 읽기' 버튼을 클릭하면 전체 텍스트를 읽습니다.
    5. '중지' 버튼을 클릭하여 음성을 중단합니다.
    6. 드롭다운 메뉴에서 다른 음성을 선택하거나 슬라이더로 속도를 조절할 수 있습니다.
    """)