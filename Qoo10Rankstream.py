import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

st.title("Qoo10 브랜드 순위 추적기 PC")

# 브랜드 입력 받기
brands_input = st.text_input("찾고 싶은 브랜드명을 입력하세요 (여러 개는 ,로 구분)", "TEST")

if st.button("검색 시작"):
    TARGET_BRANDS = [b.strip().lower() for b in brands_input.split(",")]
    results = []

    for g in range(0, 11):
        url = f"https://www.qoo10.jp/gmkt.inc/Bestsellers/?g={g}"
        try:
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            category_tag = soup.find("h3")
            if category_tag:
                category_text = category_tag.text.strip()
                if "(" in category_text and ")" in category_text:
                    category_name = category_text.split("(")[-1].split(")")[0]
                else:
                    category_name = f"g={g}"
            else:
                category_name = f"g={g}"

            lis = soup.find_all('li')
            for li in lis:
                brand_tag = li.find('a', class_='txt_brand')
                if not brand_tag:
                    continue

                brand_actual = brand_tag.get('title', '').strip()
                brand_actual_lower = brand_actual.lower()

                for target in TARGET_BRANDS:
                    if target in brand_actual_lower:
                        rank_tag = li.find('span', class_='rank')
                        title_tag = li.find('a', class_='tt')
                        li_id = li.get('id', '')

                        product_id = li_id.replace('g_', '') if li_id.startswith('g_') else li_id

                        results.append({
                            'category_g': g,
                            'category_name': category_name,
                            'searched_brand': target,
                            'matched_brand': brand_actual,
                            'rank': rank_tag.text.strip() if rank_tag else '',
                            'product_title': title_tag.get('title', '').strip() if title_tag else '',
                            'product_id': product_id
                        })

        except Exception as e:
            st.error(f"g={g} 페이지 로드 실패: {e}")

    if results:
        df = pd.DataFrame(results)
        st.success(f"총 {len(df)}개 항목을 찾았습니다!")
        st.dataframe(df)

        # 파일 다운로드
        csv = df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="CSV 파일 다운로드",
            data=csv,
            file_name='brand_rank_results.csv',
            mime='text/csv',
        )
    else:
        st.warning("해당 브랜드를 찾을 수 없습니다.")
