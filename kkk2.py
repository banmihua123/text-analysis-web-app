import streamlit as st
import requests
from bs4 import BeautifulSoup
import jieba
from collections import Counter
from pyecharts.charts import WordCloud, Bar
from pyecharts import options as opts
from pyecharts.globals import ThemeType
from streamlit_echarts import st_pyecharts

def fetch_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text()
        return text
    except Exception as e:
        st.error(f"内容抓取失败: {e}")
        return None

def analyze_text(text):
    words = jieba.lcut(text)
    word_counts = Counter(words)
    return word_counts

def filter_words(word_counts, threshold):
    filtered_counts = {word: count for word, count in word_counts.items() if count >= threshold}
    return Counter(filtered_counts)

def plot_wordcloud(word_counts, top_n=20):
    top_words = word_counts.most_common(top_n)
    words, freqs = zip(*top_words) if top_words else ([], [])
    wordcloud = (
        WordCloud(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
        .add("", list(zip(words, freqs)), word_size_range=[20, 100])
        .set_global_opts(title_opts=opts.TitleOpts(title="WordCloud"))
    )
    return wordcloud

url = st.text_input("请输入文章URL:")

if url:
    content = fetch_content(url)
    if content:
        word_counts = analyze_text(content)
        threshold = st.sidebar.slider("过滤低频词阈值:", 1, max(word_counts.values(), default=1), value=1)
        filtered_words = filter_words(word_counts, threshold)

        chart_type = st.sidebar.radio("选择图表类型:", ["词云", "柱状图","折线图","散点图","雷达图","饼图","箱线图"])
        if chart_type == "词云":
            wc = plot_wordcloud(filtered_words)  # Pass the Counter object
            st_pyecharts(wc)
        elif chart_type == "柱状图":
            words, counts = zip(*filtered_words.most_common(20))
            bar_chart = (
                Bar(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
                .add_xaxis(list(words))
                .add_yaxis("词频", list(counts))
                .set_global_opts(title_opts=opts.TitleOpts(title="词频柱状图"))
            )
            st_pyecharts(bar_chart)
    else:
        st.warning("无法从提供的URL抓取内容，请检查URL是否有效。")
else:
    st.warning("请输入一个有效的文章URL")