import streamlit as st
import requests
import time
import random
import json
from typing import List, Dict

class LOLDataCollector:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://kr.api.riotgames.com"
        self.headers = {
            "X-Riot-Token": api_key
        }
    
    def get_tier_entries(self, tier: str) -> List[Dict]:
        """티어별 소환사 목록을 가져옵니다."""
        if tier == "CHALLENGER":
            url = f"{self.base_url}/lol/league/v4/challengerleagues/by-queue/RANKED_SOLO_5x5"
            response = requests.get(url, headers=self.headers)
            return response.json().get("entries", []) if response.status_code == 200 else []
        elif tier == "GRANDMASTER":
            url = f"{self.base_url}/lol/league/v4/grandmasterleagues/by-queue/RANKED_SOLO_5x5"
            response = requests.get(url, headers=self.headers)
            return response.json().get("entries", []) if response.status_code == 200 else []
        elif tier == "MASTER":
            url = f"{self.base_url}/lol/league/v4/masterleagues/by-queue/RANKED_SOLO_5x5"
            response = requests.get(url, headers=self.headers)
            return response.json().get("entries", []) if response.status_code == 200 else []
        else:
            all_entries = []
            for division in ["I", "II", "III", "IV"]:
                url = f"{self.base_url}/lol/league/v4/entries/RANKED_SOLO_5x5/{tier}/{division}"
                response = requests.get(url, headers=self.headers)
                if response.status_code == 200:
                    all_entries.extend(response.json())
            return all_entries

    def get_summoner_by_id(self, summoner_id: str) -> Dict:
        """소환사 ID로 소환사 정보를 가져옵니다."""
        url = f"{self.base_url}/lol/summoner/v4/summoners/{summoner_id}"
        response = requests.get(url, headers=self.headers)
        return response.json() if response.status_code == 200 else {}

    def get_matches_by_puuid(self, puuid: str, count: int = 5) -> List[str]:
        """소환사의 최근 매치 ID 목록을 가져옵니다."""
        url = f"https://asia.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"
        params = {"count": count}
        response = requests.get(url, headers=self.headers, params=params)
        return response.json() if response.status_code == 200 else []

    def get_match_detail(self, match_id: str) -> Dict:
        """매치 상세 정보를 가져옵니다."""
        url = f"https://asia.api.riotgames.com/lol/match/v5/matches/{match_id}"
        response = requests.get(url, headers=self.headers)
        return response.json() if response.status_code == 200 else {}

    def extract_match_data(self, match_detail: Dict, selected_features: List[str]) -> Dict:
        """매치 데이터에서 선택된 특성들을 추출합니다."""
        if not match_detail or "info" not in match_detail:
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

def collect_tier_data(collector: LOLDataCollector, tier: str, num_matches: int, 
                     selection_method: str, selected_features: List[str]) -> List[Dict]:
    """특정 티어의 데이터를 수집합니다."""
    unique_matches = set()
    match_data_list = []
    
    # 티어별 소환사 목록 가져오기
    summoners = collector.get_tier_entries(tier)
    if not summoners:
        return []

    # 소환사 선택 방법에 따라 처리
    if selection_method == "랜덤":
        selected_summoners = random.sample(summoners, min(20, len(summoners)))  # 충분한 수의 소환사를 선택
    else:  # "상위" 선택
        selected_summoners = summoners[:20]  # 상위 20명의 소환사 선택

    # 목표한 매치 수에 도달할 때까지 데이터 수집
    while len(match_data_list) < num_matches and selected_summoners:
        summoner = selected_summoners.pop(0)  # 소환사 목록에서 하나씩 처리
        
        summoner_info = collector.get_summoner_by_id(summoner.get("summonerId"))
        if not summoner_info or "puuid" not in summoner_info:
            continue

        # 매치 ID 목록 가져오기
        match_ids = collector.get_matches_by_puuid(summoner_info["puuid"], 5)  # 각 소환사당 5개의 매치만 확인
        
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
            
            time.sleep(1.2)  # API 제한 준수

    return match_data_list

def save_as_json(data: List[Dict], filename: str):
    """데이터를 JSON 파일로 저장합니다."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def main():
    st.title("League of Legends 데이터 수집기")

    # API 키 입력
    api_key = st.text_input("Riot Games API 키를 입력하세요", type="password")
    if not api_key:
        st.warning("API 키를 입력해주세요.")
        return

    collector = LOLDataCollector(api_key)

    # 사이드바에 설정 옵션 추가
    st.sidebar.header("데이터 수집 설정")
    
    # 티어 선택
    tiers = ["CHALLENGER", "GRANDMASTER", "MASTER", "DIAMOND", "EMERALD", 
             "PLATINUM", "GOLD", "SILVER", "BRONZE", "IRON"]
    selected_tiers = st.sidebar.multiselect("수집할 티어 선택", tiers, default=["CHALLENGER"])
    
    # 티어별 설정
    tier_configs = {}
    for tier in selected_tiers:
        with st.sidebar.expander(f"{tier} 설정"):
            tier_configs[tier] = {
                "matches": st.number_input(f"{tier} 매치 수", 1, 50, 3, key=f"matches_{tier}"),
                "selection": st.radio(f"{tier} 선택 방식", ["상위", "랜덤"], key=f"selection_{tier}")
            }

    # 수집할 데이터 필드 선택
    available_features = [
        "championId", "championName", "kills", "deaths", "assists",
        "totalDamageDealt", "totalDamageTaken", "goldEarned",
        "wardsPlaced", "wardsKilled", "visionScore",
        "totalMinionsKilled", "neutralMinionsKilled"
    ]
    selected_features = st.multiselect(
        "수집할 데이터 필드",
        available_features,
        default=["championName", "kills", "deaths", "assists"]
    )

    if st.button("데이터 수집 시작"):
        with st.spinner("데이터 수집 중..."):
            all_match_data = []
            progress_bar = st.progress(0)
            
            for i, tier in enumerate(selected_tiers):
                st.write(f"{tier} 티어 데이터 수집 중...")
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
                # JSON 파일로 저장
                save_as_json(all_match_data, "lol_matches_data.json")
                st.success("데이터를 JSON 파일로 저장했습니다.")
                
                st.subheader("수집된 데이터 통계")
                st.write(f"총 수집된 매치 수: {len(all_match_data)}")
                
                # JSON 데이터 미리보기
                st.subheader("데이터 미리보기")
                st.json(all_match_data[:5])
            else:
                st.error("데이터 수집에 실패했습니다.")

if __name__ == "__main__":
    main()