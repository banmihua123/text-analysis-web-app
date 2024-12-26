
import streamlit as st
import requests
from bs4 import BeautifulSoup
import jieba
from collections import Counter
from pyecharts.charts import WordCloud
from pyecharts import options as opts
from pyecharts.globals import ThemeType

# 定义一个函数来获取网页内容
def fetch_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text()
        return text
    except Exception as e:
        st.error(f"Failed to fetch content: {e}")
        return None

# 定义一个函数来分词并统计词频
def analyze_text(text):
    words = jieba.lcut(text)
    word_counts = Counter(words)
    return word_counts

# 定义一个函数来绘制词云
def plot_wordcloud(word_counts, top_n=20):
    top_words = word_counts.most_common(top_n)
    word_list = [(word, count) for word, count in top_words]
    wordcloud = (
        WordCloud(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
        .add("", word_list, word_size_range=[20, 100])
        .set_global_opts(title_opts=opts.TitleOpts(title="Word Cloud"))
    )
    return wordcloud

# 定义一个函数来过滤低频词
# 定义一个函数来过滤低频词
def filter_words(word_counts, threshold):
    # 注意这里不再将结果转换为字典
    filtered_counts = Counter({word: count for word, count in word_counts.items() if count >= threshold})
    return filtered_counts


# 输入文章URL
url = st.text_input("请输入文章URL:")

if url:
    # 抓取文本内容
    content = fetch_content(url)
    if content:
        # 对文本分词并统计词频
        word_counts = analyze_text(content)

        # 侧边栏：图形筛选
        chart_type = st.sidebar.radio("选择图表类型:", [
            "词云", "柱状图", "饼图", "折线图", "散点图", "雷达图", "箱线图"
        ])

        # 交互过滤低频词
        threshold = st.sidebar.slider("过滤低频词阈值:", 1, max(word_counts.values()), value=1)
        filtered_word_counts = filter_words(word_counts, threshold)

        # 展示词频排名前20的词汇
        top_words = filtered_word_counts.most_common(20)
        st.write("词频排名前20的词汇:")
        st.table(top_words)

        # 根据选择的图表类型绘制图表
        if chart_type == "词云":
            wordcloud = plot_wordcloud(filtered_word_counts)
            st.pyecharts(wordcloud)
        else:
            # 这里只实现了词云，其他图表类型可以根据需求进一步实现
            st.warning("当前只实现了词云图表，其他图表类型待实现")
else:
    st.warning("请输入一个有效的文章URL")