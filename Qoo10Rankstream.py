import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

st.title("Qoo10 브랜드 순위 추적기")

# 브랜드 입력 받기
brands_input = st.text_input("찾고 싶은 브랜드명을 입력하세요 (여러 개는 ,로 구분)", "muhav")

if st.button("검색 시작"):
    TARGET_BRANDS = [b.strip() for b in brands_input.split(",")]
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

            for brand in TARGET_BRANDS:
                items = soup.find_all("a", class_="txt_brand", title=brand)

                for item in items:
                    parent = item.find_parent()
                    rank_tag = parent.find_previous("span", class_="rank")
                    if rank_tag:
                        rank = rank_tag.text.strip()
                        results.append({
                            "category_g": g,
                            "category_name": category_name,
                            "brand": brand,
                            "rank": rank
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
