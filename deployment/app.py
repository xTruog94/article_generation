import streamlit as st
from deployment.backend import Majority, Generate


major_site = Majority()
generator = Generate()
categories = major_site.all_categories
st.header('')

category = st.selectbox('Lựa chọn chuyên mục',options = categories)

articles, urls = major_site.get_article_by_cate(category)
article_selected = st.selectbox('Lựa chọn bài viết mẫu',options = articles)
article_index = articles.index(article_selected)
article_url = urls[article_index]
print(article_url)
if st.button("Generate"):
    new_article, urls = generator.generate(article_url)
    if new_article is None:
        st.write("Việc xuất bản gặp chút vấn đề. Vui lòng thử với bài viết khác!")
    else:
        st.write("#### Link các bài viết liên quan")
        st.write(article_url)
        for url in urls:
            st.write(url)
        st.write(new_article)
