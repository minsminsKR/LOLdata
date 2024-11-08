# LOLdata

---

# 🏆 리그 오브 레전드 데이터 수집기 🏆 
https://league-of-legends-data-collector.streamlit.app/

리그 오브 레전드의 랭크 매치 데이터를 쉽고 빠르게 수집하고 분석하세요!

## 📋 프로젝트 개요

**리그 오브 레전드 데이터 수집기**는 **Riot Games API**를 통해 다양한 티어의 매치 데이터를 수집하고 JSON 파일로 저장할 수 있도록 도와주는 도구입니다. 원하는 티어, 통계 데이터 필드, 소환사 선택 방법을 지정하여 매치 데이터를 손쉽게 수집하세요!

## 🎮 주요 기능

- **티어별 소환사 목록 수집**: **챌린저**, **그랜드마스터**, **마스터** 등 다양한 티어의 데이터를 수집할 수 있습니다.
- **매치 데이터 수집**: 챔피언 통계, 킬, 어시스트, 데미지, 시야 점수 등 다양한 매치 데이터를 수집하고 저장합니다.
- **데이터 필드 맞춤 선택**: 원하는 통계 데이터 필드를 선택하여 불필요한 정보를 줄이고 필요한 정보만 수집할 수 있습니다.
- **JSON 파일 저장**: 수집한 데이터를 JSON 파일로 저장해 분석에 활용할 수 있습니다.
- **Streamlit 통합**: **Streamlit** 기반의 직관적인 인터페이스로 손쉽게 데이터 수집을 진행할 수 있습니다.

## 🛠️ 사용 방법

1. **API 키 입력**: Riot Games API 키를 입력하여 데이터 수집을 시작합니다.
2. **티어 선택**: 수집하고자 하는 랭크 티어를 선택하고 각 티어의 매치 수와 소환사 선택 방법을 설정합니다.
3. **데이터 필드 선택**: 각 매치에서 수집할 통계 데이터를 선택합니다 (킬, 데미지, 시야 점수 등).
4. **수집 시작 및 저장**: "데이터 수집 시작" 버튼을 클릭하여 데이터 수집을 시작합니다. 완료 후 데이터는 `lol_matches_data.json` 파일로 저장됩니다.

## 📥 설치 및 설정

1. 레포지토리를 클론합니다:
    ```bash
    git clone https://github.com/minsminsKR/LOLdata.git
    cd LOLdata
    ```
2. 필요한 패키지를 설치합니다:
    ```bash
    pip install -r requirements.txt
    ```
3. Streamlit 앱을 실행합니다:
    ```bash
    streamlit run app.py
    ```

## 🔑 Riot Games API 키

이 애플리케이션을 사용하려면 유효한 **Riot Games API 키**가 필요합니다. Riot Games 개발자 포털에서 [API 키를 발급받으세요](https://developer.riotgames.com/).

## 📚 자세한 사용 방법

### 티어 설정
각 선택된 티어에 대해 다음을 지정할 수 있습니다:
- **매치 수**: 티어별 수집할 매치 수를 설정합니다.
- **소환사 선택 방식**:
  - **상위 소환사**: 티어 내 랭킹 상위 소환사를 선택합니다.
  - **랜덤 선택**: 선택된 티어 내 소환사를 랜덤으로 선택합니다.

### 데이터 필드
다음 데이터 필드 중 원하는 항목을 선택할 수 있습니다:
- `championId`, `championName`, `kills`, `deaths`, `assists`, `totalDamageDealt`, `totalDamageTaken`, `goldEarned`, `wardsPlaced`, `wardsKilled`, `visionScore`, `totalMinionsKilled`, `neutralMinionsKilled`
- 그 이외의 변수를 자유롭게 추가해보세요!

## 📊 데이터 시각화 및 미리보기

데이터 수집이 완료되면 JSON 데이터를 미리보기로 확인할 수 있으며, 수집된 매치 수 통계도 제공됩니다. JSON 데이터 미리보기는 첫 다섯 개의 항목을 표시하여 수집된 데이터를 빠르게 확인할 수 있습니다.

## 📝 예시 사용법

**챌린저**와 **그랜드마스터** 티어의 데이터를 수집하고, 필요한 **데이터 필드**를 설정하여 상위 랭크의 고수 플레이어들의 경기 데이터를 분석할 수 있습니다.

![image](https://github.com/user-attachments/assets/9ca4c5af-16b5-447c-bdf5-5be9c5637c0a)


---
