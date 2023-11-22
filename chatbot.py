import os
from openai import OpenAI
from dotenv import load_dotenv
import panel as pn

load_dotenv()

client = OpenAI(
    api_key = os.getenv('OPENAI_API_KEY')
)

def get_completion_from_messages(messages, model="gpt-3.5-turbo", temperature=0):
    response = client.chat.completions.create(
        model= model,
        messages = messages,
        temperature = temperature
    )

    return response.choices[0].message.content

pn.extension()

panels = []

context = [ {'role':'system', 'content':"""
너는 사용자에게 운동프로그램을 추천하기 위한 챗봇이야
사용자에게 먼저 인사를 하고, 해당하는 질문 9개야
너가 먼저 1번부터 질문을 차례대로 하고 질문에 맞는 답변을 받았을때만 다음 질문을 던져줘.
해당하는 질문에 모든 답변을 받으면, 항목별로 구분해서 dataframe을 만들어서 보여줘.

질문은 아래와 같아 :

1. 거주하시는 구와 동을 알려주세요. (예: 관악구 봉천동)
2. 연령대를 골라주세요. (1: 학생(초, 중, 고등), 2: 성인, 3: 노인)
3. 운동 목표를 골라주세요. (1: 심폐지구력 향상, 2: 근력 향상, 3: 체형 교정, 4: 무관)
4. 건강 상태를 골라주세요. (1: 디스크, 2: 관절 질환, 3: 혈압 질환, 4: 대사증후군, 5: 해당 없음)
5. 선호 시간대를 골라주세요. (1: 새벽, 2: 오전, 3: 오후, 4: 저녁, 5: 무관)
6. 선호 운동을 골라주세요. (1: 구기및라켓, 2: 레저, 3: 무도, 4: 무용, 5: 민속, 6: 재활, 7: 체력단련및생활운동)
7. 선호 인원수를 골라주세요. (1: 5명 이하, 2: 5명 이상, 3: 무관)
8. 선호 빈도를 골라주세요. (1: 주1회, 2: 주2회, 3: 주3회, 4: 주4회 이상)
9. 중요항목을 선택해주세요. (1: 거주지, 2: 연령대, 3: 운동목표, 4: 건강상태, 5: 선호시간대, 6: 선호운동, 7: 선호인원수, 8: 선호빈도, 9: 무관)

"""} ]

def collect_messages(_):
    # 텍스트 입력 위젯에서 사용자 입력 가져오기
    prompt = inp.value_input
    # 다음 입력에 대한 text input 지우기
    inp.value = ''
    # 사용자 입력을 시스템 역할과 함께 대화 context에 추가
    context.append({'role':'system', 'content':f"{prompt}"})
    # 현재 대화 내용을 기반으로 AI 응답 가져오기
    response = get_completion_from_messages(context)
    # AI의 응답을 시스템 역할과 함께 대화 context에  추가
    context.append({'role':'system', 'content':f"{response}"})
    # Be_Life 패널에 AI 응답 표시
    panels.append(pn.Row('Be_Life:', pn.pane.Markdown(prompt, width=800, styles={'background-color': '#f0fcd4'})))
    # User 패널에 사용자 입력 표시
    panels.append(pn.Row('User:', pn.pane.Markdown(prompt, width=800, styles={'background-color': '##FFA98F'})))
    # 패널들이 있는 열 반환
    return pn.Column(*panels)

    # if ' ' not in prompt or '동' not in prompt:
    #     response = '"관악구 봉천동"과 같이 구와 동을 정확히 입력해주세요.'
    #     panels.append(pn.Row('Be_Life:', pn.pane.Markdown(response, width=800, styles={'background-color': '#f0fcd4'})))
    #     return pn.Column(*panels)
    

    # context.append({'role': 'system', 'content': f"{prompt}"})
    # response = get_completion_from_messages(context)
    # context.append({'role':'system', 'content':f"{response}"})
    # panels.append(
    #     pn.Row('User:', pn.pane.Markdown(prompt, width=800, styles={'background-color': '#FF607F'})))
    # panels.append(
    #     pn.Row('Be_Life:', pn.pane.Markdown(response, width=800, styles={'background-color': '#18CCA8'})))

    # return pn.Column(*panels)

inp = pn.widgets.TextInput(value="안녕하세요", placeholder='답변을 입력해주세요')
button_conversation = pn.widgets.Button(name="입력")

# 버튼 클릭 시 입력 값을 초기화
def on_button_click(event):
    inp.value = ""  

button_conversation.on_click(on_button_click)

interactive_conversation = pn.bind(collect_messages, button_conversation)

dashboard = pn.Column(
    inp,
    pn.Row(button_conversation),
    pn.panel(interactive_conversation, loading_indicator=True, height=300),
)

dashboard.show()
