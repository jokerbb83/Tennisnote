# -*- coding: utf-8 -*-
"""MSC_SCB_app (스코어보드)

- 관리자 앱(공통 로직)이 있는 파일을 그대로 실행하되,
  MSC_APP_MODE=scoreboard 로 고정해서 3개 탭(경기기록/월별/개인별)만 보이게 합니다.
- 관리자 앱 파일을 수정하면, 이 스코어보드 앱에도 자동 반영됩니다.

※ 주의: 이 파일에는 Streamlit 호출을 두지 말아야 합니다.
       (set_page_config 등은 '관리자 앱 파일' 안에서 가장 먼저 실행되도록 유지)
"""

import os
import runpy
from pathlib import Path

# ✅ 스코어보드 모드로 고정 (옵저버/읽기전용 UI)
os.environ["MSC_APP_MODE"] = "scoreboard"
os.environ["MSC_READ_ONLY"] = "1"  # ✅ 어떤 경우에도 JSON 쓰기 금지

HERE = Path(__file__).resolve().parent

# ✅ 연결 대상(관리자 앱) 후보들
CANDIDATES = [

    "MSC_app.py",        # ✅ 기준(관리자) 앱 파일
]

target = None
for name in CANDIDATES:
    p = HERE / name
    if p.exists():
        target = p
        break

if target is None:
    raise FileNotFoundError("연결할 관리자 앱 파일을 찾지 못했어. (MSC_app - 복사본 (12).py / MSC_app_admin_linked.py / MSC_app.py / MSC_app - 복사본 (9).py 중 하나가 필요)")

# ✅ 관리자 앱을 그대로 실행 (수정사항 자동 반영)
runpy.run_path(str(target), run_name="__main__")