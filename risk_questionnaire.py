from __future__ import annotations

from typing import Final


def calculate_risk_score(
    age: int,
    investment_horizon_years: int,
    income_stability: int,
    investment_experience: int,
    reaction_to_20_drawdown: int,
) -> int:
    """
    Pure business logic for computing a deterministic risk score.

    Scoring logic (intentionally simple and explainable):

    1) Age (younger investorsมักรับความเสี่ยงได้มากกว่า):
        - <= 30 years      -> 10 points
        - 31-45 years      -> 7 points
        - 46-60 years      -> 4 points
        - > 60 years       -> 1 point

    2) Investment horizon in years (ยิ่งยาว ยิ่งรับความเสี่ยงได้มาก):
        - >= 15 years      -> 10 points
        - 10-14 years      -> 7 points
        - 5-9 years        -> 4 points
        - < 5 years        -> 1 point

    3) Income stability (1-5):
        - Scale 1-5, then multiply by 3
        - 1 = รายได้ไม่แน่นอนเลย
        - 5 = รายได้มั่นคงสูงมาก

    4) Investment experience (1-5):
        - Scale 1-5, then multiply by 3
        - 1 = แทบไม่มีประสบการณ์
        - 5 = มีประสบการณ์สูง เคยผ่านหลาย cycle

    5) Reaction if portfolio drops 20% (1-5):
        - 1 = ตกใจ ขายออกทันที (รับความเสี่ยงได้น้อย)
        - 3 = รอดูสถานการณ์ก่อน (กลาง)
        - 5 = มองเป็นโอกาสในการซื้อเพิ่ม (รับความเสี่ยงได้มาก)
        - ให้คะแนน = reaction_to_20_drawdown * 4

    Total score range (โดยประมาณ):
        min ~ 1 + 1 + 3 + 3 + 4  = 12
        max ~ 10 + 10 + 15 + 15 + 20 = 70
    """
    if age <= 30:
        age_score = 10
    elif age <= 45:
        age_score = 7
    elif age <= 60:
        age_score = 4
    else:
        age_score = 1

    if investment_horizon_years >= 15:
        horizon_score = 10
    elif investment_horizon_years >= 10:
        horizon_score = 7
    elif investment_horizon_years >= 5:
        horizon_score = 4
    else:
        horizon_score = 1

    income_score = income_stability * 3
    experience_score = investment_experience * 3
    drawdown_score = reaction_to_20_drawdown * 4

    total_score = age_score + horizon_score + income_score + experience_score + drawdown_score
    return total_score


def determine_risk_level(score: int) -> str:
    """
    Map a total score to a discrete risk level.

    Thresholds (ออกแบบจากช่วงคะแนนด้านบน):
        - 0 - 25    -> "low"
        - 26 - 45   -> "medium"
        - >= 46     -> "high"

    Thresholds ค่อนข้าง conservative (ต้องได้คะแนนสูงจริง ๆ ถึงจะเป็น High)
    """
    if score <= 25:
        return "low"
    if score <= 45:
        return "medium"
    return "high"


def _ask_int(prompt: str, min_value: int | None = None, max_value: int | None = None) -> int:
    """
    Helper for CLI to safely read an integer within an optional range.
    """
    while True:
        raw = input(prompt)
        try:
            value = int(raw)
        except ValueError:
            print("กรุณากรอกตัวเลขจำนวนเต็ม.")
            continue

        if min_value is not None and value < min_value:
            print(f"ค่าต้องไม่ต่ำกว่า {min_value}.")
            continue
        if max_value is not None and value > max_value:
            print(f"ค่าต้องไม่เกิน {max_value}.")
            continue
        return value


def run_questionnaire_cli() -> str:
    """
    Run the risk questionnaire via CLI and return the final, user-confirmed risk level.

    Responsibilities of this function:
        - Collect user inputs via CLI.
        - Delegate scoring to calculate_risk_score().
        - Delegate recommended level mapping to determine_risk_level().
        - Handle confirmation/override interaction flow for the final risk level.
    """

    age = _ask_int("1) อายุของคุณ (ปี): ", min_value=0)

    investment_horizon_years = _ask_int(
        "2) คุณมีแผนจะลงทุนระยะยาวกี่ปี? (จำนวนปี): ",
        min_value=1,
    )

    print("3) ความมั่นคงของรายได้ (1-5):")
    print("   1 = ไม่แน่นอนมาก, 5 = มั่นคงมาก")
    income_stability = _ask_int("   กรุณาเลือก (1-5): ", min_value=1, max_value=5)

    print("4) ประสบการณ์การลงทุน (1-5):")
    print("   1 = แทบไม่มี, 5 = มีประสบการณ์สูง")
    investment_experience = _ask_int("   กรุณาเลือก (1-5): ", min_value=1, max_value=5)

    print("5) หากพอร์ตของคุณลดลง 20% ในเวลาไม่นาน คุณจะทำอย่างไร? (1-5)")
    print("   1 = ตกใจและขายออกทันที")
    print("   2 = ขายบางส่วนเพื่อลดความเสี่ยง")
    print("   3 = ถือรอดูสถานการณ์ต่อไป")
    print("   4 = ถือต่อและอาจทยอยซื้อเพิ่ม")
    print("   5 = มองเป็นโอกาสซื้อเพิ่มอย่างชัดเจน")
    reaction_to_20_drawdown = _ask_int("   กรุณาเลือก (1-5): ", min_value=1, max_value=5)

    # Business logic (pure functions)
    score = calculate_risk_score(
        age=age,
        investment_horizon_years=investment_horizon_years,
        income_stability=income_stability,
        investment_experience=investment_experience,
        reaction_to_20_drawdown=reaction_to_20_drawdown,
    )
    recommended_level = determine_risk_level(score)

    # Show result and confirmation options
    print()
    print(f"คะแนนความเสี่ยงรวมของคุณ: {score}")
    print(f"ระดับความเสี่ยงที่ระบบแนะนำ: {recommended_level}")
    print()

    print("กรุณาเลือกวิธีการกำหนดระดับความเสี่ยง:")
    print("  1 = ใช้ระดับที่ระบบแนะนำ")
    print("  2 = เลือกระดับเอง (Override)")
    mode_choice = _ask_int("กรุณาเลือก (1-2): ", min_value=1, max_value=2)

    if mode_choice == 1:
        final_level = recommended_level
    else:
        # Override flow: เลือกและยืนยันจนกว่าจะได้ระดับสุดท้าย
        while True:
            print()
            print("เลือกระดับความเสี่ยงที่คุณต้องการ:")
            print("  1 = low")
            print("  2 = medium")
            print("  3 = high")
            override_choice = _ask_int("กรุณาเลือก (1-3): ", min_value=1, max_value=3)

            if override_choice == 1:
                selected_level = "low"
            elif override_choice == 2:
                selected_level = "medium"
            else:
                selected_level = "high"

            # Final confirmation loop
            while True:
                print()
                print(f"คุณเลือกระดับความเสี่ยง: {selected_level}")
                print("  1 = ยืนยันระดับนี้")
                print("  2 = ยกเลิกและเลือกใหม่")
                confirm_choice = _ask_int("กรุณาเลือก (1-2): ", min_value=1, max_value=2)

                if confirm_choice == 1:
                    final_level = selected_level
                    break  # ออกจาก confirmation loop
                else:
                    # ยกเลิกและกลับไปเลือกใหม่
                    break

            if confirm_choice == 1:
                # ได้ระดับสุดท้ายแล้ว ออกจาก override loop
                break

    print()
    print(f"ระดับความเสี่ยงสุดท้ายที่คุณยืนยัน: {final_level}")
    print()

    return final_level

