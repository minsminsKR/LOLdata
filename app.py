import streamlit as st
import requests
import time
import random
import json
import pandas as pd
from typing import List, Dict
from io import BytesIO

class LOLDataCollector:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://kr.api.riotgames.com"
        self.headers = {
            "X-Riot-Token": api_key
        }
    
    def get_tier_entries(self, tier: str) -> List[Dict]:
        """티어별 소환사 목록을 가져옵니다."""
        try:
            if tier == "CHALLENGER":
                url = f"{self.base_url}/lol/league/v4/challengerleagues/by-queue/RANKED_SOLO_5x5"
                response = requests.get(url, headers=self.headers)
                if response.status_code != 200:
                    st.error(f"Tier data lookup failed: {response.status_code} - {response.text}")
                    return []
                return response.json().get("entries", [])
            elif tier == "GRANDMASTER":
                url = f"{self.base_url}/lol/league/v4/grandmasterleagues/by-queue/RANKED_SOLO_5x5"
                response = requests.get(url, headers=self.headers)
                if response.status_code != 200:
                    st.error(f"Tier data lookup failed: {response.status_code} - {response.text}")
                    return []
                return response.json().get("entries", [])
            elif tier == "MASTER":
                url = f"{self.base_url}/lol/league/v4/masterleagues/by-queue/RANKED_SOLO_5x5"
                response = requests.get(url, headers=self.headers)
                if response.status_code != 200:
                    st.error(f"Tier data lookup failed: {response.status_code} - {response.text}")
                    return []
                return response.json().get("entries", [])
            else:
                all_entries = []
                for division in ["I", "II", "III", "IV"]:
                    url = f"{self.base_url}/lol/league/v4/entries/RANKED_SOLO_5x5/{tier}/{division}"
                    response = requests.get(url, headers=self.headers)
                    if response.status_code != 200:
                        st.error(f"{tier} {division} Tier data lookup failed: {response.status_code} - {response.text}")
                        continue
                    all_entries.extend(response.json())
                return all_entries
        except Exception as e:
            st.error(f"Error encountered during tier data query: {str(e)}")
            return []

    def get_summoner_by_id(self, summoner_id: str) -> Dict:
        """소환사 ID로 소환사 정보를 가져옵니다."""
        try:
            url = f"{self.base_url}/lol/summoner/v4/summoners/{summoner_id}"
            response = requests.get(url, headers=self.headers)
            if response.status_code != 200:
                st.error(f"Summoner information inquiry failed: {response.status_code} - {response.text}")
                return {}
            return response.json()
        except Exception as e:
            st.error(f"Error retrieving summoner information: {str(e)}")
            return {}

    def get_matches_by_puuid(self, puuid: str, count: int = 5) -> List[str]:
        """소환사의 최근 매치 ID 목록을 가져옵니다."""
        try:
            url = f"https://asia.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"
            params = {"count": count}
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code != 200:
                st.error(f"Match list lookup failed: {response.status_code} - {response.text}")
                return []
            return response.json()
        except Exception as e:
            st.error(f"Error looking up match list: {str(e)}")
            return []

    def get_match_detail(self, match_id: str) -> Dict:
        """매치 상세 정보를 가져옵니다."""
        try:
            url = f"https://asia.api.riotgames.com/lol/match/v5/matches/{match_id}"
            response = requests.get(url, headers=self.headers)
            if response.status_code != 200:
                st.error(f"Error looking up match list: {response.status_code} - {response.text}")
                return {}
            return response.json()
        except Exception as e:
            st.error(f"Error looking up match list: {str(e)}")
            return {}

    def extract_match_data(self, match_detail: Dict, selected_features: List[str]) -> Dict:
        """매치 데이터에서 선택된 특성들을 추출합니다."""
        try:
            if not match_detail or "info" not in match_detail:
                st.warning("Match details are invalid.")
                return None

            match_data = {
                "match_id": match_detail["metadata"]["matchId"],
                "game_duration": match_detail["info"]["gameDuration"],
                "game_version": match_detail["info"]["gameVersion"],
                "players": []
            }

            teams_data = {100: {"kills": 0, "deaths": 0, "assists": 0},
                         200: {"kills": 0, "deaths": 0, "assists": 0}}

            # 각 플레이어 데이터 추출
            for participant in match_detail["info"]["participants"]:
                player_data = {feature: participant.get(feature) for feature in selected_features}
                player_data.update({
                    "teamId": participant["teamId"],
                    "win": participant["win"],
                    "position": participant.get("teamPosition", "UNKNOWN")
                })
                
                # 팀 통계 업데이트
                team_id = participant["teamId"]
                teams_data[team_id]["kills"] += participant.get("kills", 0)
                teams_data[team_id]["deaths"] += participant.get("deaths", 0)
                teams_data[team_id]["assists"] += participant.get("assists", 0)
                
                match_data["players"].append(player_data)

            # 팀 데이터 추가
            match_data["blue_team"] = teams_data[100]
            match_data["red_team"] = teams_data[200]
            match_data["blue_team_win"] = match_detail["info"]["teams"][0]["win"]

            return match_data

        except Exception as e:
            st.error(f"Error extracting match data: {str(e)}")
            return None

def save_as_json(data: List[Dict]) -> BytesIO:
    """데이터를 JSON 형식의 BytesIO 객체로 변환합니다."""
    json_string = json.dumps(data, ensure_ascii=False, indent=4)
    return BytesIO(json_string.encode())

def convert_to_excel(data: List[Dict]) -> BytesIO:
    """데이터를 Excel 형식의 BytesIO 객체로 변환합니다."""
    # 데이터 구조 평탄화
    flattened_data = []
    for match in data:
        base_info = {
            "match_id": match["match_id"],
            "game_duration": match["game_duration"],
            "game_version": match["game_version"],
            "tier": match["tier"],
            "blue_team_kills": match["blue_team"]["kills"],
            "blue_team_deaths": match["blue_team"]["deaths"],
            "blue_team_assists": match["blue_team"]["assists"],
            "blue_team_win": match["blue_team_win"],
            "red_team_kills": match["red_team"]["kills"],
            "red_team_deaths": match["red_team"]["deaths"],
            "red_team_assists": match["red_team"]["assists"]
        }
        
        # 각 플레이어 데이터를 개별 행으로 변환
        for player in match["players"]:
            player_data = base_info.copy()
            player_data.update(player)
            flattened_data.append(player_data)
    
    df = pd.DataFrame(flattened_data)
    excel_buffer = BytesIO()
    df.to_excel(excel_buffer, index=False)
    excel_buffer.seek(0)
    return excel_buffer

def collect_tier_data(collector: LOLDataCollector, tier: str, num_matches: int, 
                     selection_method: str, selected_features: List[str]) -> List[Dict]:
    """특정 티어의 데이터를 수집합니다."""
    unique_matches = set()
    match_data_list = []
    
    # 티어별 소환사 목록 가져오기
    summoners = collector.get_tier_entries(tier)
    if not summoners:
        st.error(f"{tier} Failed to get tier summoner list.")
        return []

    # 소환사 선택 방법에 따라 처리
    if selection_method == "랜덤":
        selected_summoners = random.sample(summoners, min(20, len(summoners)))
    else:  # "상위" 선택
        selected_summoners = summoners[:20]

    # 목표한 매치 수에 도달할 때까지 데이터 수집
    for summoner in selected_summoners:
        if len(match_data_list) >= num_matches:
            break
            
        summoner_info = collector.get_summoner_by_id(summoner.get("summonerId"))
        if not summoner_info or "puuid" not in summoner_info:
            st.warning(f"Failed to get summoner information: {summoner.get('summonerName', 'Unknown')}")
            continue

        # 매치 ID 목록 가져오기
        match_ids = collector.get_matches_by_puuid(summoner_info["puuid"], 5)
        if not match_ids:
            st.warning(f"Summoner with no match history: {summoner.get('summonerName', 'Unknown')}")
            continue
            
        for match_id in match_ids:
            if match_id in unique_matches:
                continue
            
            if len(match_data_list) >= num_matches:
                break
                
            unique_matches.add(match_id)
            match_detail = collector.get_match_detail(match_id)
            
            if match_detail:
                match_data = collector.extract_match_data(match_detail, selected_features)
                if match_data:
                    match_data["tier"] = tier
                    match_data_list.append(match_data)
                    st.info(f"Match data collection completed: {len(match_data_list)}/{num_matches}")
            
            time.sleep(0.5)  # API 제한 준수

    return match_data_list

def main():
    st.title("League of Legends Data Collector")

    # API 키 입력
    api_key = st.text_input("Riot Games API", type="password")
    if not api_key:
        st.warning("Input the API key.")
        return

    collector = LOLDataCollector(api_key)

    # 다운로드 버튼을 표시할 컨테이너 생성
    download_container = st.container()

    # 사이드바에 설정 옵션 추가
    st.sidebar.header("Data Collection Settings")
    
    # 티어 선택
    tiers = ["CHALLENGER", "GRANDMASTER", "MASTER", "DIAMOND", "EMERALD", 
             "PLATINUM", "GOLD", "SILVER", "BRONZE", "IRON"]
    selected_tiers = st.sidebar.multiselect("Select tier to collect", tiers, default=["CHALLENGER"])
    
    # 티어별 설정
    tier_configs = {}
    for tier in selected_tiers:
        with st.sidebar.expander(f"{tier} Setting"):
            tier_configs[tier] = {
                "matches": st.number_input(f"{tier} Match count", 1, 50, 3, key=f"matches_{tier}"),
                "selection": st.radio(f"{tier} selection method", ["Top", "Random"], key=f"selection_{tier}")
            }

    # 수집할 데이터 필드 선택
    available_features = [
        "championId", "championName", "kills", "deaths", "assists",
        "totalDamageDealt", "totalDamageTaken", "goldEarned",
        "wardsPlaced", "wardsKilled", "visionScore",
        "totalMinionsKilled", "neutralMinionsKilled"
    ]
    selected_features = st.multiselect(
        "Data Fields to Collect",
        available_features,
        default=["championName", "kills", "deaths", "assists"]
    )

    if st.button("Start Data Collection"):
        with st.spinner("Collecting data..."):
            all_match_data = []
            progress_bar = st.progress(0)
            
            for i, tier in enumerate(selected_tiers):
                st.write(f"{tier} Collecting tier data...")
                config = tier_configs[tier]
                
                tier_matches = collect_tier_data(
                    collector, 
                    tier,
                    config["matches"],
                    config["selection"],
                    selected_features
                )
                all_match_data.extend(tier_matches)
                progress_bar.progress((i + 1) / len(selected_tiers))

            if all_match_data:
                st.success("Data collection completed!")
                
                # 다운로드 버튼들을 미리 만들어둔 컨테이너에 표시
                with download_container:
                    st.subheader("Download Collected Data")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        json_buffer = save_as_json(all_match_data)
                        st.download_button(
                            label="Download JSON",
                            data=json_buffer,
                            file_name="lol_matches_data.json",
                            mime="application/json"
                        )
                    
                    with col2:
                        excel_buffer = convert_to_excel(all_match_data)
                        st.download_button(
                            label="Download Excel",
                            data=excel_buffer,
                            file_name="lol_matches_data.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                
                st.subheader("Collected data statistics")
                st.write(f"Total number of matches collected: {len(all_match_data)}")
                
                # JSON 데이터 미리보기
                st.subheader("Data Preview")
                st.json(all_match_data[:5])
            else:
                st.error("Data collection failed.")

if __name__ == "__main__":
    main()