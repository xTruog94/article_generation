import streamlit as st
from crawler import DomainCrawler, SitemapCrawler

st.header("WSS Web Scraper")

method = st.sidebar.selectbox(
    "Phương án lấy URL",
    ("Sitemap", "Auto generate"),
    index = 0
)

num_articles = st.sidebar.text_input(
    "Số URL tối đa (để trống nếu lấy toàn bộ)",
)

domain = None
sitemap = None
store_type = None
index_name = None

if method.lower() == "sitemap":
    st.markdown("### URL lấy từ sitemap")
    input_str = st.text_input("Sitemap")
    domain = None
    crawler = SitemapCrawler(input_str)
else:
    st.markdown("### URL được tự động generate")
    input_str = st.text_input("Domain")
    sitemap = None
    crawler = DomainCrawler(input_str)

if input_str != "":
    store_type = st.radio(
    "Lưu bài viết vào:",
    ["Elasticsearch", 
     "File CSV",
     "Đếu cần lưu"
     ]
    )
    
if store_type == "Elasticsearch":
    index_name = st.text_input("index store")

if store_type == "File CSV" or \
    store_type == "Đếu cần lưu" or \
    (index_name != "" and index_name is not None) :
    if st.button("Run"):
        crawler.run()

