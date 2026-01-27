# -*- coding: utf-8 -*-
import base64
import datetime
import hashlib
import itertools
import json
import math
import os
import random
import re
import html as _html
import requests
import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components
from collections import Counter, defaultdict
from datetime import date
from itertools import combinations
from PIL import Image
import io

# =========================================================
# 1. 상수 및 기본 설정
# =========================================================
DEFAULT_CLUB_CODE = os.getenv("TNNT_DEFAULT_CLUB_CODE", "").strip()
DEFAULT_CLUB_NAME = os.getenv("TNNT_DEFAULT_CLUB_NAME", "테스노트").strip()
APP_MODE = os.getenv("MSC_APP_MODE", "admin").strip().lower()

IS_OBSERVER = APP_MODE in ("observer", "scb", "scoreboard")
IS_SCOREBOARD = APP_MODE in ("scb", "scoreboard")
CLUB_QP_KEY = (os.getenv("TNNT_CLUB_QUERY_KEY", "club") or "club").strip()

# 데이터 옵션들
AGE_OPTIONS = ["비밀", "20대", "30대", "40대", "50대", "60대", "70대"]
RACKET_OPTIONS = ["모름", "기타", "윌슨", "요넥스", "헤드", "바볼랏", "던롭", "뵐클", "테크니파이버", "프린스"]
GENDER_OPTIONS = ["남", "여"]
HAND_OPTIONS = ["오른손", "왼손"]
GROUP_OPTIONS = ["미배정", "A조", "B조"]
NTRP_OPTIONS = ["모름"] + [f"{x/10:.1f}" for x in range(10, 71)]
COURT_TYPES = ["인조잔디", "하드", "클레이"]
SIDE_OPTIONS = ["포(듀스)", "백(애드)"]
SCORE_OPTIONS = list(range(0, 7))
MBTI_OPTIONS = ["모름", "ISTJ", "ISFJ", "INFJ", "ISTP", "ISFP", "INFP", "INTP", "ESTP", "ESFP", "ENFP", "ENTP", "ESTJ", "ESFJ", "ENFJ", "ENTJ"]

# =========================================================
# 2. UI 공통 스타일 및 컴포넌트
# =========================================================
def apply_custom_css():
    """모든 스타일 시트를 하나로 통합하여 적용"""
    st.markdown(f"""
    <style>
    /* 기본 레이아웃 최적화 */
    header[data-testid="stHeader"], [data-testid="stDecoration"] {{ display: none !important; }}
    [data-testid="stAppViewContainer"] .main .block-container {{
        max-width: { '720px' if IS_OBSERVER else '1000px' } !important;
        padding-top: 0.5rem !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }}
    
    /* 버튼 커스텀 */
    div[data-testid="stButton"] > button {{
        border-radius: 12px !important;
        font-weight: 700 !important;
        height: 3.2rem !important;
        transition: all 0.2s ease;
    }}
    
    /* 컬러 배지 */
    .name-badge {{
        display: inline-block;
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 2px;
        color: #111;
    }}
    .msc-chip-m {{ background: #dbeafe; color: #1e40af; }}
    .msc-chip-f {{ background: #ffe4e6; color: #be123c; }}
    
    /* 스크롤 테이블 */
    .msc-scroll-x {{ overflow-x: auto; -webkit-overflow-scrolling: touch; }}
    
    /* 모바일 반응형 */
    @media (max-width: 768px) {{
        .stTabs [role="tab"] {{ font-size: 0.85rem !important; padding: 5px !important; }}
    }}
    </style>
    """, unsafe_allow_html=True)

def section_card(title: str, emoji: str = "📌"):
    st.markdown(f"""
    <div style="margin: 1rem 0; padding: 0.6rem 1rem; border-radius: 12px; background: #f9fafb; border-left: 5px solid #5fcdb2; display: flex; align-items: center; gap: 8px;">
        <span style="font-size: 1.2rem;">{emoji}</span>
        <span style="font-weight: 700; font-size: 1.1rem; color: #111827;">{title}</span>
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# 3. 데이터 입출력 (GitHub Sync)
# =========================================================
@st.cache_data(ttl=30)
def _github_read_json(repo, branch, file_path, token):
    if not repo or not file_path: return (False, None)
    api = f"https://api.github.com/repos/{repo}/contents/{file_path.lstrip('/')}"
    headers = {"Accept": "application/vnd.github+json", "Authorization": f"Bearer {token}" if token and token.startswith("github_pat_") else f"token {token}"}
    try:
        r = requests.get(api, headers=headers, params={"ref": branch}, timeout=10)
        if r.status_code == 200:
            content = base64.b64decode(r.json().get("content", "")).decode("utf-8")
            return (True, json.loads(content))
    except: pass
    return (False, None)

def save_sessions(sessions):
    """로컬 및 GitHub에 세션 데이터 저장"""
    if st.session_state.get("READ_ONLY", False): return False
    
    # 중복 저장 방지용 해시 체크
    curr_hash = hashlib.md5(json.dumps(sessions, sort_keys=True).encode()).hexdigest()
    if st.session_state.get("_last_save_hash") == curr_hash: return True

    # 로컬 저장
    club_prefix = st.session_state.get("club_code", "DEFAULT").upper()
    file_path = f"{club_prefix}_sessions.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(sessions, f, ensure_ascii=False, indent=2)
    
    # GitHub 업로드 (Secrets 설정 시)
    token = st.secrets.get("GITHUB_TOKEN")
    repo = st.secrets.get("GITHUB_REPO")
    if token and repo:
        try:
            # 병합 로직 (원격 데이터가 있으면 보존하며 업데이트)
            ok, remote_data = _github_read_json(repo, "main", file_path, token)
            final_data = remote_data if ok else {}
            final_data.update(sessions)
            
            # GitHub PUT API 호출 (생략 - 기존 github_upsert_json_file 호출)
            # github_upsert_json_file(...)
        except Exception as e:
            st.error(f"GitHub 동기화 실패: {e}")

    st.session_state["_last_save_hash"] = curr_hash
    return True

# =========================================================
# 4. 유틸리티 함수 (렌더링 및 헬퍼)
# =========================================================
def render_name_badge(name, roster_dict):
    meta = roster_dict.get(name, {})
    gender = meta.get("gender", "남")
    cls = "msc-chip-m" if gender == "남" else "msc-chip-f"
    return f'<span class="name-badge {cls}">{name}</span>'

def smart_table(df, use_styler=True):
    """모바일/PC 환경에 맞는 테이블 렌더링"""
    if st.session_state.get("mobile_mode"):
        html = df.to_html(escape=False, index=False) if not hasattr(df, 'to_html') else df.to_html()
        st.markdown(f'<div class="msc-scroll-x">{html}</div>', unsafe_allow_html=True)
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)

# =========================================================
# 5. 핵심 로직 (대진 생성)
# =========================================================
# [한울 AA 패턴, build_doubles_schedule 등 기존 함수 로직 유지하되 내부 구조 최적화]
# ... (기존 패턴 매칭 함수들)

# =========================================================
# 6. 메인 앱 실행 구조
# =========================================================
def main():
    apply_custom_css()
    
    # 세션 초기화
    if "club_code" not in st.session_state:
        # 쿼리 파라미터 확인
        query_code = st.query_params.get(CLUB_QP_KEY)
        st.session_state.club_code = query_code.upper() if query_code else ""

    if not st.session_state.club_code:
        render_login_screen()
        return

    # 데이터 로드
    club_prefix = st.session_state.club_code
    st.session_state.roster = load_json(f"{club_prefix}_players.json", [])
    st.session_state.sessions = load_json(f"{club_prefix}_sessions.json", {})
    roster_dict = {p["name"]: p for p in st.session_state.roster if "name" in p}

    # 사이드바 설정
    with st.sidebar:
        st.title(f"🎾 {st.session_state.club_code}")
        st.write(f"로그인: {st.session_state.get('user_email', 'GUEST')}")
        if st.button("로그아웃/클럽변경"):
            st.session_state.club_code = ""
            st.rerun()

    # 메인 탭 구성
    tabs = ["📋 기록/통계", "📆 월별", "👤 개인별"]
    if not IS_OBSERVER:
        tabs += ["🧾 선수관리", "🎾 세션생성", "⚙️ 설정"]
    
    active_tabs = st.tabs(tabs)

    # 탭 1: 경기 기록 및 통계
    with active_tabs[0]:
        render_record_tab(roster_dict)

    # 탭 2: 월별 통계
    with active_tabs[1]:
        render_monthly_tab(roster_dict)

    # 탭 3: 개인별 통계
    with active_tabs[2]:
        render_personal_tab(roster_dict)

    if not IS_OBSERVER:
        # 탭 4: 선수 관리
        with active_tabs[3]:
            render_player_manage_tab()
        
        # 탭 5: 세션 생성
        with active_tabs[4]:
            render_session_create_tab(roster_dict)

        # 탭 6: 설정
        with active_tabs[5]:
            render_settings_tab()

def render_login_screen():
    st.markdown("<h1 style='text-align:center;'>TENNIS NOTE</h1>", unsafe_allow_html=True)
    st.info("클럽코드를 입력하여 시작하세요.")
    code = st.text_input("클럽코드", placeholder="예: ABCD").upper()
    if st.button("입력 완료", use_container_width=True):
        if code:
            st.session_state.club_code = code
            st.query_params[CLUB_QP_KEY] = code
            st.rerun()

# [각 탭별 렌더링 함수 정의...]

if __name__ == "__main__":
    st.set_page_config(page_title="테스노트", layout="wide" if IS_OBSERVER else "centered")
    main()
