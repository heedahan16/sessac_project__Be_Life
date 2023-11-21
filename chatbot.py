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
사용자에게 먼저 인사를 하고, 해당하는 질문 3개야
질문을 차례대로 한개씩 해줘
해당하는 질문에 모든 답변을 받으면, 1번 질문은 ','을 기준으로 split하고, 나머지 질문도 항목별로 구분해서 dataframe을 만들어서 보여줘. 각 항목의 컬럼명은 '이름', '나이', '거주지', '운동목표'였으면 좋겠어.

질문은 아래와 같아 :

  1. 이름과 나이가 어떻게 되세요? (예: 맹구, 5)
  2. 거주하시는 동을 알려주세요. (예: 봉천동)
  3. 운동 목표를 골라주세요. (1: 심폐지구력 향상, 2: 근력 향상, 3: 체형 교정)

"""} ]

def collect_messages(_):
    prompt = inp.value_input
    inp.value = ''
    context.append({'role':'system', 'content':f"{prompt}"})
    response = get_completion_from_messages(context)
    context.append({'role':'system', 'content':f"{response}"})
    panels.append(
        pn.Row('User:', pn.pane.Markdown(prompt, width=600)))
    panels.append(
        pn.Row('Be_Life:', pn.pane.Markdown(response, width=600, styles={'background-color': '#f0fcd4'})))

    return pn.Column(*panels)

inp = pn.widgets.TextInput(value="안녕하세요", placeholder='답변을 입력해주세요')
button_conversation = pn.widgets.Button(name="입력")


def on_button_click(event):
    inp.value = ""  # 버튼 클릭 시 입력 값을 초기화

button_conversation.on_click(on_button_click)

interactive_conversation = pn.bind(collect_messages, button_conversation)

dashboard = pn.Column(
    inp,
    pn.Row(button_conversation),
    pn.panel(interactive_conversation, loading_indicator=True, height=300),
)

dashboard.show()
