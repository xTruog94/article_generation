import streamlit as st
import requests
from deployment.backend import Generate

def get_review(data:dict):
    r = requests.post("http://172.22.0.52:8000/generate_article", json = data)
    if r.status_code == 200:
        return r.json()
    return None

st.header('King of Product Review')

temperature = st.slider("temparature", min_value = 0.0, max_value=1.0, value = 0.9, step = 0.1)
top_p = st.slider("top_p", min_value = 0.0, max_value=1.0, value = 0.9, step = 0.1)
top_k = st.slider("top_k", min_value = 0, max_value=10, value = 1, step = 1)

generator = Generate( 
                 policy = "gemini",
                 temperature = temperature,
                 top_p = top_p,
                 top_k = top_k,
                 max_output_tokens = 5000
                )
name = st.text_input("Tên sản phẩm")
code = st.text_input("Mã sản phẩm")
keywords = st.text_input("Từ khóa mong muốn xuất hiện trong bài")
domain = st.text_input("Tên miền lấy bài", value = "dienmayxanh.com")
type_article = st.selectbox("Loại bài", ["Thông tin sản phẩm","Review sản phẩm"])
if type_article == "Thông tin sản phẩm":
    type_article = "product_information"
else:
    type_article = "product_review"
    
data_json = {
    "name":name,
    "code": code,
    "keywords": keywords,
    "description": "",
    "domain":domain,
    "type_article": type_article
}

if st.button("Generate"):
    response = get_review(data_json)
    if response:
        new_article = response['data']['article']
        if new_article is None:
            st.write("Việc xuất bản gặp chút vấn đề. Vui lòng thử với bài viết khác!")
        else:
            new_article = new_article.get("content", "")
            st.write("#### Bài AI review")
            st.caption(f"Độ dài bài viết: {len(new_article.replace("\n",""))}")
            st.markdown(new_article)
    else:
        st.write("Việc xuất bản gặp chút vấn đề. Vui lòng thử với bài viết khác!")
