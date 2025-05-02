import streamlit as st
import requests
import json

# # 네이버 API 인증 정보 (실제 사용 시 보안을 위해 환경 변수나 Streamlit secrets로 관리해야 함)
# NCLIENT_ID = "S7bLv8C9wwpmIoiFiZdA"
# NCLIENT_SECRET = "hRovxhJF7Q"

# Streamlit 페이지 설정
st.set_page_config(page_title="단어 학습 TTS 애플리케이션", layout="wide", initial_sidebar_state="collapsed")

# 제목
st.title("단어별 읽기 및 의미 확인 애플리케이션")
st.write("텍스트를 입력하면 단어별로 클릭하여 발음을 듣고 의미를 확인할 수 있습니다.")

# 네이버 사전 API 호출 함수
def get_word_meaning(word):
    url = "https://openapi.naver.com/v1/search/dictionary.json"
    headers = {
        "X-Naver-Client-Id": NCLIENT_ID,
        "X-Naver-Client-Secret": NCLIENT_SECRET
    }
    params = {
        "query": word,
        "display": 1  # 결과 개수
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            if data.get('items') and len(data['items']) > 0:
                return data['items'][0]
            return None
        else:
            st.error(f"API 오류: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"API 호출 오류: {str(e)}")
        return None

# HTML 코드에 API 호출 로직 추가
html_code = f"""
<div style="padding: 15px; border: 1px solid #ddd; border-radius: 5px;">
    <textarea id="text-to-speak" style="width: 100%; height: 150px; padding: 10px; margin-bottom: 15px;" placeholder="텍스트를 입력하고 '단어 분리' 버튼을 클릭하세요..."></textarea>
    
    <!-- 버튼 및 컨트롤 -->
    <div style="margin-bottom: 15px;">
        <button id="process-button" style="background-color: #2196F3; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; margin-right: 10px;">단어 분리</button>
        <button id="speak-all-button" style="background-color: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; margin-right: 10px;">전체 읽기</button>
        <button id="stop-button" style="background-color: #f44336; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer;">중지</button>
    </div>
    
    <div style="margin-bottom: 15px;">
        <label for="voice-select">음성 선택:</label>
        <select id="voice-select" style="padding: 5px; margin: 0 10px;"></select>
        
        <label for="speed">속도:</label>
        <input type="range" id="speed" min="0.5" max="2" value="1" step="0.1" style="vertical-align: middle;">
        <span id="speed-value">1.0</span>
    </div>
    
    <!-- 단어 컨테이너 -->
    <div id="word-container" style="margin-top: 20px; padding: 15px; border: 1px solid #eee; border-radius: 5px; min-height: 100px; line-height: 2;">
        <!-- 여기에 단어 버튼이 동적으로 추가됩니다 -->
    </div>
    
    <!-- 선택된 단어 정보 -->
    <div id="word-info" style="margin-top: 20px; display: none; padding: 15px; background-color: #f9f9f9; border-radius: 5px;">
        <h3 id="selected-word" style="margin-top: 0; color: #333;"></h3>
        <div id="word-meaning"></div>
        <div id="loading-translation" style="display: none; margin-top: 10px;">검색 중...</div>
    </div>
    
    <script>
        // 전역 변수
        let voices = [];
        let selectedVoice = null;
        let currentUtterance = null;
        
        // 음성 목록 로드
        function loadVoices() {
            voices = window.speechSynthesis.getVoices();
            const voiceSelect = document.getElementById('voice-select');
            
            voiceSelect.innerHTML = '';
            
            const googleVoices = voices.filter(voice => voice.name.includes('Google') || voice.name.includes('Chrome'));
            const otherVoices = voices.filter(voice => !voice.name.includes('Google') && !voice.name.includes('Chrome'));
            
            googleVoices.forEach(voice => {
                const option = document.createElement('option');
                option.value = voice.name;
                option.textContent = `${{voice.name}} (${{voice.lang}})`;
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
                option.textContent = `${{voice.name}} (${{voice.lang}})`;
                voiceSelect.appendChild(option);
            });
            
            let englishVoice = voices.find(voice => voice.lang.includes('en'));
            
            if (englishVoice) {
                selectedVoice = englishVoice;
                voiceSelect.value = englishVoice.name;
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
                
                // 단어에서 구두점 제거 (검색용)
                const cleanWord = word.replace(/[^a-zA-Z0-9\\u00C0-\\u017F]/g, '');
                
                wordButton.textContent = word;
                wordButton.style.display = 'inline-block';
                wordButton.style.margin = '0 5px 5px 0';
                wordButton.style.padding = '5px 10px';
                wordButton.style.backgroundColor = '#e0e0e0';
                wordButton.style.borderRadius = '3px';
                wordButton.style.cursor = 'pointer';
                wordButton.dataset.word = cleanWord;  // 원래 단어 저장
                
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
                window.speechSynthesis.cancel();  // 이전 음성 취소
                
                if (word.trim() !== "") {
                    const utterance = new SpeechSynthesisUtterance(word);
                    currentUtterance = utterance;
                    
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
                window.speechSynthesis.cancel();  // 이전 음성 취소
                
                const text = document.getElementById('text-to-speak').value;
                
                if (text.trim() !== "") {
                    const utterance = new SpeechSynthesisUtterance(text);
                    currentUtterance = utterance;
                    
                    utterance.rate = parseFloat(document.getElementById('speed').value);
                    
                    if (selectedVoice) {
                        utterance.voice = selectedVoice;
                    }
                    
                    window.speechSynthesis.speak(utterance);
                } else {
                    alert("텍스트를 입력해주세요.");
                }
            }
        }
        
        // 단어 정보 표시
        async function showWordInfo(word, element) {
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
            
            // 네이버 API를 통해 단어 의미 가져오기
            try {
                const response = await fetch(`/search_word?word=${{encodeURIComponent(word)}}`);
                const data = await response.json();
                
                loadingDiv.style.display = 'none';
                
                if (data && data.items && data.items.length > 0) {
                    const item = data.items[0];
                    wordMeaningDiv.innerHTML = `
                        <p style="font-size: 16px; margin-bottom: 5px;"><strong>품사:</strong> ${{item.pos || '정보 없음'}}</p>
                        <p style="font-size: 16px; margin-bottom: 5px;"><strong>의미:</strong></p>
                        <p style="font-size: 15px;">${{item.meaning || '정보 없음'}}</p>
                    `;
                } else {
                    wordMeaningDiv.innerHTML = `
                        <p>이 단어에 대한 정보를 찾을 수 없습니다.</p>
                        <p style="font-size: 14px; color: #666;">다른 단어를 시도해보세요.</p>
                    `;
                }
            } catch (error) {
                loadingDiv.style.display = 'none';
                wordMeaningDiv.innerHTML = `
                    <p>단어 검색 중 오류가 발생했습니다.</p>
                    <p style="font-size: 14px; color: #666;">나중에 다시 시도해주세요.</p>
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
            alert("이 브라우저는 음성 합성을 지원하지 않습니다.");
        }
    </script>
</div>
"""

# 단어 검색 API 엔드포인트
@st.cache_data(ttl=3600)  # 1시간 캐싱
def search_word(word):
    return get_word_meaning(word)

# Streamlit 엔드포인트 설정
st.markdown("## API 엔드포인트")
word_param = st.experimental_get_query_params().get("word", [""])[0]
if word_param:
    result = search_word(word_param)
    st.json(result)

# HTML 삽입 (높이를 적절히 조정)
st.components.v1.html(html_code, height=700)

# 사용 안내
st.info("""
이 애플리케이션은 단어별 학습을 돕기 위한 도구입니다.
텍스트를 입력하고 '단어 분리' 버튼을 클릭하면 각 단어를 클릭하여 발음을 듣고 의미를 확인할 수 있습니다.
네이버 사전 API를 사용하여 영어 단어의 한국어 의미를 제공합니다.
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

# 데모용 예제 텍스트
st.subheader("예제 텍스트")
st.code("""The cat and dog are good friends. They love to play in the sun. 
When it rains, they use an umbrella. They drink water and eat apples and bananas.
Students learn English at school. Teachers help them read and write.
""", language="text")