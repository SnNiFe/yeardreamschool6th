# 1. 프로젝트 생성
# 2. uv 설치
# pip install uv
# uv pip list
import pandas as pd

# 3. 현재 프로젝트(bare)를 uv 로 초기화
# uv init --bare

# 4. 패키지(라이브러리) 추가
# pip install pandas
# uv add pandas

# dic:{} list:[] tuple:()
# '' <- 싱글쿼터 / "" <- 더블쿼터
df = pd.DataFrame({
    '이름':['김분석', '이명랑', '박운영'],
    '부서':['분석팀', '개발팀', '운영팀'],
    '연차':[3, 5, 2]
})

print(f'data frame : \n{df}')
# uv run main.py