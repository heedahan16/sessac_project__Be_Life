import os
from dotenv import load_dotenv
import openai
from langchain.document_loaders import CSVLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.docstore.document import Document
import re
import gradio as gr

# OpenAI API Key 관리
load_dotenv()
openai.api_key = os.environ.get('OPENAI_API_KEY')

# 함수 이름 openAiGPT
def openAiGPT(message, chat_history) :

    # csv 불러오기
    loader = CSVLoader('Data/program_data.csv', encoding='cp949')     # 이용할 csv 파일 입력
    documents = loader.load()
    documents

    # csv 내용 전처리하기
    documents_pro = []      # 저장 리스트

    for page in documents:    ### pdf형식에 따라 다르게 전처리
        text = page.page_content
        text = re.sub(r"\n", " ", text.strip())
        documents_pro.append(text)      # documents_pro 에 추가

    # chunk split, list -> document
    doc_chunks = []

    for line in documents_pro:      # documents_pro의 각 문서를 반복
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=3000,    ### 최대청크의 최대 길이를 3000자로 제한(문서에 따라 다르게 기준을 잡음)
            separators=["\n\n", "\n", ".", ""],     ###  텍스트를 청크로 분할하는데 기준이 되는 문자 목록
            chunk_overlap=0,    # 청크 사이의 중첩, 현재는 없음
        )
        chunks = text_splitter.split_text(line)
        for i, chunk in enumerate(chunks):      # 분리된 청크를 document형식으로 변환
            doc = Document(
                page_content=chunk, metadata={"page": i, "source": "program_data.csv"}   # 페이지 메타데이터 정보, 정보의 근원이 되는 csv
            )
            doc_chunks.append(doc)      # doc_chunks 리스트에 추가


    # ChromaDB에 임베딩
    embeddings = OpenAIEmbeddings()
    vector_store = Chroma.from_documents(doc_chunks, embeddings)    # doc_chunks의 정보를 OpenAIEmbeddings()로 임베딩, doc_chunks의 내용을 수행
    retriever = vector_store.as_retriever(search_kwargs={"k": 2})       ### 검색을 진행할 때, kwargs 갯수 설정(현재 2, 0이하인 경우 수행 x)


    from langchain.prompts.chat import (
        ChatPromptTemplate,
        SystemMessagePromptTemplate,
        HumanMessagePromptTemplate,
    )

    ### 프롬프트 조절
    system_template="""
    마지막에 질문에 답하려면 다음과 같은 맥락을 사용합니다.
    답을 모르면 모른다고만 하고 답을 만들려고 하지 마세요.
    운동프로그램의 정확한 시설명, 종목명, 프로그래명, 연령, 성별, 장애, 주간횟수, 시간대, 시설주소를 알려주세요.
    운동프로그램 추천 전문가 역할을 해주셨으면 합니다.

    당신은 한국말로만 대답합니다

    {summaries}

    """

    messages = [
        SystemMessagePromptTemplate.from_template(system_template),     # 시스템 사전 설정
        HumanMessagePromptTemplate.from_template("{question}")      # 내 질문 설정
    ]

    prompt = ChatPromptTemplate.from_messages(messages)     # prompt 변수에 저장

    chain_type_kwargs = {"prompt": prompt}

    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)  ### 챗지피티 모델 설정(현재, gpt-3.5-turbo)

    chain = RetrievalQAWithSourcesChain.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever = retriever,
        return_source_documents=True,
        chain_type_kwargs=chain_type_kwargs,
        reduce_k_below_max_tokens=False  ### 토큰 제한 해제(지금은 X)
)

    # myAsk = """종로구에 있는 운동 프로그램을 찾아줘""" # 질문 내용 예시
    result = chain(message)
    gpt_message = result['answer']
    print(gpt_message)

    chat_history.append((message, gpt_message))
    return "", chat_history

with gr.Blocks() as demo:
    chatbot = gr.Chatbot()
    msg = gr.Textbox()
    clear = gr.ClearButton([msg, chatbot])

    msg.submit(openAiGPT, [msg, chatbot], [msg, chatbot])

if __name__ == "__main__":
    demo.launch()