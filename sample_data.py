# csv 파일 불러오기
import pandas as pd
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

sample = pd.read_csv('Data/Be_Life.csv')
# print(sample.head())

# 사용자 리스트 생성
user = []
for i in range(1, 1001):
    user.append(i)
# print(user)

# 전체 체육시설 리스트를 dataframe으로 변환
user = pd.DataFrame(user)

user.columns = ['사용자']
# print(user.head())

# df 합치기
data = pd.concat([user, sample], axis=1) 
# print(data)

# 인코딩 후 csv 파일로 저장
data.to_csv('Data/sample_data.csv', mode='w', encoding='cp949', index=False)
print(data.head())
