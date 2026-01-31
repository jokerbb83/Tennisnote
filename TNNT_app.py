 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a/TNNT_app.py b/TNNT_app.py
index 28fbdf3ad67f20fbb23bd4b7db388b34db91a6b4..6a4f66dc004dc0f25b5b96f3257f981130578b5a 100644
--- a/TNNT_app.py
+++ b/TNNT_app.py
@@ -4335,51 +4335,54 @@ def render_tab_player_manage(tab, read_only: bool = False):
                     f"- 성별: 남자 {gender_counter.get('남', 0)}명, "
                     f"여자 {gender_counter.get('여', 0)}명"
                 )
 
                 # 주손
                 st.markdown(
                     f"- 주손: 오른손 {hand_counter.get('오른손', 0)}명, "
                     f"왼손 {hand_counter.get('왼손', 0)}명"
                 )
 
                 # 라켓 브랜드
                 racket_text = " / ".join(f"{k} {v}명" for k, v in racket_counter.items())
                 st.markdown(f"- 라켓 브랜드: {racket_text}")
 
                 # NTRP
                 ntrp_text = " / ".join(f"NTRP {k}: {v}명" for k, v in ntrp_counter.items())
                 st.markdown(f"- NTRP 분포: {ntrp_text}")
 
                 if mbti_counter:
                     mbti_text = " / ".join(f"{k} {v}명" for k, v in mbti_counter.items())
                 else:
                     mbti_text = "집계할 MBTI가 없습니다."
                 st.markdown(f"- MBTI 분포: {mbti_text}")
 
 
-                with st.expander("📈 항목별 분포 다이어그램 (각 항목 100% 기준) 🔽 아래로 내려보세요.", expanded=False):
+                with st.expander(
+                    "📈 항목별 분포 다이어그램 (각 항목 100% 기준) 🔽 아래로 내려보세요.",
+                    expanded=True,
+                ):
 
                     # 🔧 필터 / 옵션 (슬라이더 + 어떤 항목 볼지 선택)
                     with st.expander("필터 / 옵션 열기", expanded=False):
                         min_count = st.slider(
                             "표시할 최소 인원 수",
                             min_value=0,
                             max_value=total_players,
                             value=1,
                             help="이 값보다 적은 인원인 항목은 숨겨집니다.",
                         )
 
                         section_options = ["나이대", "성별", "주손", "라켓", "NTRP", "MBTI"]
                         selected_sections = st.multiselect(
                             "보고 싶은 항목 선택",
                             section_options,
                             default=section_options,
                         )
 
                     # 어떤 분포를 쓸지 묶어두기
                     dist_items = []
                     if "나이대" in selected_sections:
                         dist_items.append(("나이대별 인원 분포", age_counter))
                     if "성별" in selected_sections:
                         dist_items.append(("성별 인원 분포", gender_counter))
                     if "주손" in selected_sections:
 
EOF
)
