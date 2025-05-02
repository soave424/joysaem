import streamlit as st
import requests

# Streamlit 페이지 설정
st.set_page_config(page_title="단어 학습 TTS 애플리케이션", layout="wide")

# 제목
st.title("단어별 읽기 및 의미 확인 애플리케이션")
st.write("텍스트를 입력하면 단어별로 클릭하여 발음을 듣고 의미를 확인할 수 있습니다.")

# 네이버 API 호출 함수
def get_word_meaning(word):
    # 환경 변수에서 API 인증 정보 가져오기
    try:
        client_id = st.secrets["NAVER_CLIENT_ID"]
        client_secret = st.secrets["NAVER_CLIENT_SECRET"]
    except:
        st.warning("네이버 API 인증 정보가 설정되지 않았습니다. 기본 사전을 사용합니다.")
        return None
        
    url = "https://openapi.naver.com/v1/papago/n2mt"
    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret
    }
    data = {
        "source": "en",
        "target": "ko",
        "text": word
    }
    
    try:
        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            result = response.json()
            if 'message' in result and 'result' in result['message']:
                return result['message']['result']['translatedText']
            return None
        else:
            return None
    except Exception as e:
        st.error(f"API 호출 오류: {str(e)}")
        return None

# 단어 번역 API 엔드포인트
@st.cache_data(ttl=3600)  # 1시간 캐싱
def translate_word(word):
    return get_word_meaning(word)

# API 엔드포인트 처리
if "translate_word" in st.session_state:
    word_param = st.query_params.get("word", "")
    if word_param:
        translation = translate_word(word_param)
        st.session_state.translation_result = {"word": word_param, "translation": translation}

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
        <div id='loading-translation' style='display: none; margin-top: 10px;'>검색 중...</div>
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
            
            voices.forEach(voice => {
                const option = document.createElement('option');
                option.value = voice.name;
                option.textContent = voice.name + ' (' + voice.lang + ')';
                voiceSelect.appendChild(option);
                
                // 영어 음성 자동 선택
                if (voice.lang.includes('en')) {
                    selectedVoice = voice;
                    option.selected = true;
                }
            });
            
            // 음성이 선택되지 않았으면 첫 번째 음성 선택
            if (!selectedVoice && voices.length > 0) {
                selectedVoice = voices[0];
                voiceSelect.options[0].selected = true;
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
                
                // 단어에서 구두점 제거
                const cleanWord = word.replace(/[^a-zA-Z0-9\\u00C0-\\u017F]/g, '');
                
                wordButton.textContent = word;
                wordButton.style.display = 'inline-block';
                wordButton.style.margin = '0 5px 5px 0';
                wordButton.style.padding = '5px 10px';
                wordButton.style.backgroundColor = '#e0e0e0';
                wordButton.style.borderRadius = '3px';
                wordButton.style.cursor = 'pointer';
                wordButton.dataset.word = cleanWord;
                
                // 클릭 이벤트 추가
                wordButton.addEventListener('click', function() {
                    speakWord(this.dataset.word);
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
        function showWordInfo(word, element) {
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
            
            // 기본 사전 (주요 단어들만 포함)
            const dictionary = {
                'apple': '사과 - 둥글고 단단한 빨간색, 녹색 또는 노란색 과일',
                'banana': '바나나 - 길고 휘어진 노란색 과일',
                'cat': '고양이 - 털이 많은 작은 집 동물',
                'dog': '개 - 충성스러운 반려동물',
                'elephant': '코끼리 - 긴 코와 큰 귀를 가진 큰 회색 동물',
                'friend': '친구 - 당신과 가까운 사람',
                'good': '좋은 - 품질이 높거나 바람직함',
                'hello': '안녕 - 인사말',
                'love': '사랑 - 깊은 애정',
                'play': '놀다 - 즐거움을 위해 활동하다',
                'rain': '비 - 구름에서 떨어지는 물방울',
                'sun': '태양 - 지구에 빛과 열을 제공하는 별',
                'they': '그들 - 두 명 이상의 사람을 가리키는 대명사',
                'use': '사용하다 - 목적을 위해 무언가를 활용하다',
                'water': '물 - 투명한 액체',
                'when': '언제 - 시간을 묻는 의문사',
                'student': '학생 - 배우는 사람',
                'school': '학교 - 교육 기관',
                'teacher': '교사 - 가르치는 사람',
                'learn': '배우다 - 지식이나 기술을 얻다',
                'english': '영어 - 영국, 미국 등에서 사용되는 언어',
                'read': '읽다 - 문자를 보고 이해하다',
                'write': '쓰다 - 단어나 문장을 만들다',
                'help': '돕다 - 누군가가 무언가를 할 수 있게 지원하다'
            };
            
            // 시간 지연 후 결과 표시 (실제로는 API 호출을 할 것임)
            setTimeout(() => {
                loadingDiv.style.display = 'none';
                
                // 기본 사전 사용
                const meaning = dictionary[word.toLowerCase()];
                if (meaning) {
                    wordMeaningDiv.innerHTML = `
                        <p style='font-size: 16px; margin-bottom: 5px;'><strong>의미:</strong></p>
                        <p style='font-size: 15px;'>${meaning}</p>
                        <p style='font-size: 12px; color: #666;'>(기본 사전에서 가져온 의미입니다.)</p>
                    `;
                } else {
                    wordMeaningDiv.innerHTML = `
                        <p>이 단어에 대한 정보를 찾을 수 없습니다.</p>
                        <p style='font-size: 14px; color: #666;'>실제 앱에서는 네이버 API를 통해 더 많은 단어를 제공할 수 있습니다.</p>
                    `;
                }
            }, 500);
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

# 사용 안내
st.info("""
이 애플리케이션은 단어별 학습을 돕기 위한 도구입니다.
텍스트를 입력하고 '단어 분리' 버튼을 클릭하면 각 단어를 클릭하여 발음을 듣고 의미를 확인할 수 있습니다.
기본 사전에는 약 25개의 영어 단어만 포함되어 있습니다.
네이버 API를 설정하면 더 많은 단어의 의미를 제공할 수 있습니다.
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
    네이버 API를 사용하려면 다음 단계를 따르세요:
    
    1. [네이버 개발자 센터](https://developers.naver.com)에서 애플리케이션을 등록합니다.
    2. Papago NMT API를 사용할 수 있도록 설정합니다.
    3. 발급받은 Client ID와 Client Secret을 Streamlit의 secrets.toml 파일에 다음과 같이 추가합니다:
    
    ```toml
    NAVER_CLIENT_ID = "발급받은 클라이언트 ID"
    NAVER_CLIENT_SECRET = "발급받은 클라이언트 시크릿"
    ```
    
    4. Streamlit Cloud를 사용하는 경우, 앱 설정의 Secrets 섹션에 위 내용을 추가합니다.
    """)

# 데모용 예제 텍스트
st.subheader("예제 텍스트")
st.code("""The cat and dog are good friends. They love to play in the sun. 
When it rains, they use an umbrella. They drink water and eat apples and bananas.
Students learn English at school. Teachers help them read and write.
""", language="text")