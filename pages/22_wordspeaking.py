import streamlit as st

# Streamlit 페이지 설정
st.set_page_config(page_title="단어 학습 TTS 애플리케이션", layout="wide")

# 제목
st.title("단어별 읽기 및 의미 확인 애플리케이션")
st.write("텍스트를 입력하면 단어별로 클릭하여 발음을 듣고 의미를 확인할 수 있습니다.")

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
            
            // 단어 뜻 찾기 (API 요청)
            try {
                // API 요청 (Streamlit에 구현된 API 호출)
                const response = await fetch('/?word=' + encodeURIComponent(word));
                const data = await response.json();
                
                loadingDiv.style.display = 'none';
                
                if (data && data.translation) {
                    wordMeaningDiv.innerHTML = `
                        <p style='font-size: 16px; margin-bottom: 5px;'><strong>의미:</strong></p>
                        <p style='font-size: 15px;'>${data.translation}</p>
                        <p style='font-size: 12px; color: #666;'>(DeepL API로 번역된 결과입니다)</p>
                    `;
                } else {
                    wordMeaningDiv.innerHTML = `
                        <p>이 단어에 대한 정보를 찾을 수 없습니다.</p>
                        <p style='font-size: 14px; color: #666;'>DeepL API 연결을 확인하거나 다른 단어를 시도해보세요.</p>
                    `;
                }
            } catch (error) {
                loadingDiv.style.display = 'none';
                wordMeaningDiv.innerHTML = `
                    <p>단어 검색 중 오류가 발생했습니다.</p>
                    <p style='font-size: 14px; color: #666;'>나중에 다시 시도해주세요.</p>
                `;
                console.error('API 호출 오류:', error);
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

# HTML 삽입
st.components.v1.html(html_code, height=700)

# 단어 번역 API 엔드포인트 처리
word_param = st.query_params.get("word", "")
if word_param:
    try:
        # 환경 변수에서 DeepL API 키 가져오기
        auth_key = st.secrets["DeepL_API_Key"]
        
        # 번역 요청을 위한 URL과 헤더 구성
        import urllib.request
        import urllib.parse
        import json
        
        # API 엔드포인트 URL (DeepL API Free)
        url = "https://api-free.deepl.com/v2/translate"
        
        # 요청 데이터 구성
        data = {
            "text": [f"The word '{word_param}' means"],
            "target_lang": "KO",
            "source_lang": "EN"
        }
        
        # JSON 데이터로 변환
        data = json.dumps(data).encode('utf8')
        
        # 요청 헤더 설정
        headers = {
            "Authorization": f"DeepL-Auth-Key {auth_key}",
            "Content-Type": "application/json"
        }
        
        # 요청 객체 생성
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        
        # API 호출 및 응답 처리
        try:
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf8'))
                
                if "translations" in result and len(result["translations"]) > 0:
                    translation = result["translations"][0]["text"]
                    st.json({"word": word_param, "translation": translation})
                else:
                    st.json({"word": word_param, "translation": None, "error": "번역 결과가 없습니다."})
        except urllib.error.HTTPError as e:
            if e.code == 456:
                st.json({"word": word_param, "translation": None, "error": "DeepL API 사용량 한도 초과"})
            else:
                st.json({"word": word_param, "translation": None, "error": f"HTTP 오류: {e.code}"})
        except Exception as e:
            st.json({"word": word_param, "translation": None, "error": f"API 호출 중 오류 발생: {str(e)}"})
    except Exception as e:
        st.json({"word": word_param, "translation": None, "error": f"API 키 설정 오류: {str(e)}"})

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

# 환경 설정 안내
with st.expander("API 설정 방법"):
    st.write("""
    DeepL API를 사용하려면 다음 단계를 따르세요:
    
    1. [DeepL API](https://www.deepl.com/pro#developer)에서 계정을 생성합니다.
    2. "API Keys & Limits" 탭에서 API 키를 확인하거나 새 키를 생성합니다.
    3. 발급받은 API 키를 Streamlit의 secrets.toml 파일에 다음과 같이 추가합니다:
    
    ```toml
    DeepL_API_Key = "발급받은 API 키"
    ```
    
    4. Streamlit Cloud를 사용하는 경우, 앱 설정의 Secrets 섹션에 위 내용을 추가합니다.
    5. DeepL Free API는 월 500,000자까지 무료로 사용할 수 있습니다.
    """)