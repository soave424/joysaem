import requests
from bs4 import BeautifulSoup
import pandas as pd

def fetch_data(kldg_no):
    url = f"https://yeep.go.kr/noti/kldgChaEDetail.do?kldgNo={kldg_no}"
    try:
        response = requests.get(url, verify=False)  # SSL 인증서 검증 비활성화
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            title = soup.select_one('div:nth-of-type(1) > div:nth-of-type(3) > div:nth-of-type(2) > div:nth-of-type(2) > table > tbody > tr:nth-of-type(1) > td')
            link = soup.select_one('div:nth-of-type(1) > div:nth-of-type(3) > div:nth-of-type(2) > div:nth-of-type(2) > table > tbody > tr:nth-of-type(3) > td > a')
            content = soup.select_one('div:nth-of-type(1) > div:nth-of-type(3) > div:nth-of-type(2) > div:nth-of-type(2) > table > tbody > tr:nth-of-type(4) > td > div > p')
            
            title_text = title.text.strip() if title else "Title not found"
            link_href = link['href'] if link else "Link not found"
            content_text = content.text.strip() if content else "Content not found"
            return title_text, link_href, content_text
        else:
            return None, None, None
    except requests.exceptions.RequestException as e:
        print(e)
        return None, None, None

# 데이터 수집
data = []
for kldg_no in range(1, 401):  # 001부터 400까지
    title, link, content = fetch_data(f"{kldg_no:03d}")
    if title and link and content:
        data.append({"kldgNo": kldg_no, "Title": title, "Link": link, "Content": content})
    print(f"Processed {kldg_no:03d}")

# 데이터프레임 생성
df = pd.DataFrame(data)

# CSV 파일로 저장
df.to_csv('output.csv', index=False, encoding='utf-8-sig')
print("Data has been saved to 'output.csv'")
