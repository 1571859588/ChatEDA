import os
os.environ["HF_HOME"] = "D:\\Research"
import streamlit as st
from openai import OpenAI
from PyPDF2 import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import torch

# Initialize the embeddings model
@st.cache_resource
def get_embeddings_model():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cuda' if torch.cuda.is_available() else 'cpu'}
    )

# Initialize the vector store
@st.cache_resource
def get_vector_store(_text_chunks, _embeddings):
    return FAISS.from_texts(texts=_text_chunks, embedding=_embeddings)

# Text splitting function
def split_text(text):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    return text_splitter.split_text(text)

# Initialize the client based on the selected API endpoint
def get_client():
    if api_endpoint == "远程API":
        return OpenAI(
            api_key="xxx",
            base_url="xxxx",
        )
    else:
        return OpenAI(
            api_key="not-needed",
            base_url="http://localhost:8000/v1"
        )

with st.sidebar:
    st.markdown (f"""
    <center>
    <img src='https://vip.helloimg.com/i/2024/07/02/66841f6f4a3a5.png' width='100'/>
    <h1> ChatEDA <sup></sup><h1/>
    </center>
    """,unsafe_allow_html=True)
    
    # Add PDF file uploader
    uploaded_files = st.file_uploader("上传PDF文件", type=['pdf'], accept_multiple_files=True)
    
    if uploaded_files:
        st.write(f"已上传 {len(uploaded_files)} 个文件")
        
        # Process uploaded PDFs
        all_text = ""
        with st.spinner("正在处理PDF文件..."):
            for uploaded_file in uploaded_files:
                try:
                    pdf_reader = PdfReader(uploaded_file)
                    for page in pdf_reader.pages:
                        all_text += page.extract_text() + "\n"
                    st.success(f"成功读取文件: {uploaded_file.name}")
                except Exception as e:
                    st.error(f"读取文件 {uploaded_file.name} 时出错: {str(e)}")
            
            if all_text:
                # Split text into chunks
                text_chunks = split_text(all_text)
                st.write(f"文档已分割成 {len(text_chunks)} 个片段")
                
                # Create vector store
                embeddings = get_embeddings_model()
                vector_store = get_vector_store(text_chunks, embeddings)
                st.session_state['vector_store'] = vector_store
                st.success("文档向量化完成！")

    api_endpoint = st.selectbox(
        "API端点",
        ["远程API", "本地API"],
        help="选择使用远程还是本地API"
    )
    
    model_option = st.selectbox(
        "选择模型",
        ["qwen-vl-max", "qwen-2.5-32k", "qwen-2.5-32b", "local-model"] if api_endpoint == "远程API" else ["local-model"],
        help="选择要使用的AI模型"
    )
    
    #角色定义输人框System Message
    system_message=st.text_area("角色定义","你是一个EDA领域的专家，能够理解EDA工具的使用以及EDA工具涉及的专业词汇，如芯片、针脚等等。")
    #创造力程度Temperature
    temperature=st.slider("创造力调节",min_value=0.0,max_value=2.0,value=1.0,step=0.1,help='值越大越具有创遁力',format="%.1f")



#初始化界面的聊天列表
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
        "role":"assistant",
        "content":"使用说明：\n 1.请上传EDA工具PDF文档\n 2.请输入您的问题\n 3.请等待片刻，ChatEDA将为您解答"
        },
        {
        "role":"user",
        "content":"OpenRoad工具是什么？它有哪些功能和应用场景？"
        },
        {
        "role":"assistant",
        "content":"""
            OpenRoad是一个开源的数字设计自动化工具，旨在通过自动化流程实现从寄存器传输级（RTL）到GDSII的完整设计流程。它是DARPA IDEA计划的一部分，目标是提供一个无需人工干预（No-Human-In-Loop, NHIL）的数字版图生成工具链，能够在24小时内完成芯片设计。
            OpenRoad的主要功能包括：
            1. 逻辑综合：使用Yosys等工具将RTL代码转换为门级网表。
            2. 布局规划：包括芯片布局初始化、I/O引脚放置、宏单元放置和电源网络生成。
            3. 全局和详细布局：优化标准单元和宏单元的布局，确保设计规则和时序要求。
            4. 时钟树综合：插入缓冲器并优化高扇出网络。
            5. 全局和详细布线：生成布线指南并确保DRC和时序约束。
            6. 芯片完成：包括寄生参数提取、最终时序和物理验证，以及金属填充。

            ![openroad](https://img.picui.cn/free/2025/02/20/67b70fd9c6ccb.png)
            OpenRoad还提供了一个强大的图形用户界面（GUI），用于可视化、分析和调试设计流程中的各个阶段。此外，它支持多种工艺设计套件（PDK），包括SkyWater 130nm、GlobalFoundries 180nm、Nangate 45nm等，适用于快速原型设计和流片。
            OpenRoad的应用场景主要包括：
            - 快速原型设计：帮助工程师快速探索架构和设计空间。
            - 低成本IC设计：降低硬件设计的时间和成本。
            - 教育和研究：为学术界和开源社区提供一个完整的数字设计工具链。
            OpenRoad的开源特性和强大的自动化能力使其成为半导体设计领域的一个重要工具。"""
        }
    ]


# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

client = OpenAI(
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
    api_key="xxx",
    base_url="xxx",
)
# base_url = os.getenv("OPENAI_BASE_URL")

if "messagesHistory" not in st.session_state:
    messagesHistory = []

def get_relevant_chunks(query, top_k=3):
    if 'vector_store' in st.session_state:
        results = st.session_state['vector_store'].similarity_search(query, k=top_k)
        return "\n".join([doc.page_content for doc in results])
    return None

def chat_stream(query, system_message=None, temperature=1):
    client = get_client()
    
    if system_message:
        messagesHistory.append({"role":"system","content":system_message})
    
    # Get relevant chunks instead of using entire PDF
    relevant_context = get_relevant_chunks(query)
    if relevant_context:
        context_message = f"以下是相关文档的内容，请基于这些内容回答用户的问题：\n\n{relevant_context}\n\n用户问题：{query}"
        messagesHistory.append({"role":"user","content":context_message})
    else:
        messagesHistory.append({"role":"user","content":query})
    
    try:
        response = client.chat.completions.create(
            model=model_option,
            messages=messagesHistory,
            stream=True,
            temperature=temperature
        )
        return response
    except Exception as e:
        st.error(f"API调用错误: {str(e)}")
        return None



#用户输入
user_query=st.chat_input("说点什么..")
if user_query:
    #显示用户输入的内容到聊天窗口
    with st.chat_message("user"):
        st.write(user_query)
    #在聊天窗口输出用户输入的问题
    st.session_state.messages.append({"role":"user","content":user_query})

    with st.chat_message("assistant"):
        with st.spinner(""):
            response = chat_stream(user_query, system_message, temperature)

            # 创建显示消息的容器
            message_placeholder=st.empty()
            # AI的答案
            ai_response = ""
            for chunk in response:
                # 获取AI的内容
                if chunk.choices and chunk.choices[0].delta.content:
                    ai_response += chunk.choices[0].delta.content
                    # 显示
                    message_placeholder.markdown(ai_response + " ")
            # 在聊天窗口输出完整的AI对话
            message_placeholder.markdown(ai_response)

    # 加入聊天列表
    st.session_state.messages.append({"role": "assistant", "content": ai_response})