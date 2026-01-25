# -*- coding: utf-8 -*-
"""TNNT 스코어보드 엔트리 포인트

- 클럽코드 온보딩(최초 1회 입력) + ?club=CODE URL 파라미터 방식은 메인 앱(TNNT_app.py)과 동일
- 이 파일은 스코어보드 모드로만 실행되도록 환경변수를 세팅한 뒤, 메인 앱을 그대로 실행합니다.
"""

import os
import runpy
from pathlib import Path

# 스코어보드 모드 강제
os.environ["MSC_APP_MODE"] = os.getenv("MSC_APP_MODE", "scoreboard")

main_script = os.getenv("TNNT_MAIN_SCRIPT", "").strip() or "TNNT_app.py"
main_path = Path(__file__).with_name(main_script)

runpy.run_path(str(main_path), run_name="__main__")
