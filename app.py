import datetime
import pandas as pd
import streamlit as st

# กำหนดรหัสผ่านสำหรับเข้าใช้งานระบบ
PASSWORD = "1234"  # สามารถเปลี่ยนรหัสผ่านได้ที่นี่


def check_password():
  """ฟังก์ชันตรวจสอบรหัสผ่าน"""

  def password_entered():
    if st.session_state["password"] == PASSWORD:
      st.session_state["password_correct"] = True
      del st.session_state["password"]
    else:
      st.session_state["password_correct"] = False

  if "password_correct" not in st.session_state:
    st.markdown(
        "## 🔒 กรุณาใส่รหัสผ่านเพื่อเข้าสู่ระบบ สนง.ปศข.2 (ห้องเล็ก) V.ทดลอง"
    )
    st.text_input(
        "รหัสผ่าน", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state and not st.session_state[
        "password_correct"
    ]:
      st.error("รหัสผ่านไม่ถูกต้อง กรุณาลองใหม่อีกครั้ง")
    return False
  elif not st.session_state["password_correct"]:
    st.markdown(
        "## 🔒 กรุณาใส่รหัสผ่านเพื่อเข้าสู่ระบบ สนง.ปศข.2 (ห้องเล็ก) V.ทดลอง"
    )
    st.text_input(
        "รหัสผ่าน", type="password", on_change=password_entered, key="password"
    )
    st.error("รหัสผ่านไม่ถูกต้อง กรุณาลองใหม่อีกครั้ง")
    return False
  else:
    return True


# ตรวจสอบสิทธิ์การเข้าใช้งาน
if check_password():

  # จำลองฐานข้อมูลเก็บข้อมูลการจองไว้ใน st.session_state
  if "bookings" not in st.session_state:
    st.session_state.bookings = []

  st.title("🏢 ระบบจองห้องประชุม สนง.ปศข.2 (ห้องเล็ก) V.ทดลอง")
  st.write("ตรวจสอบตารางวันว่าง และกรอกรายละเอียดการจองห้องประชุมด้านล่าง")

  # ----------------------------------------------------
  # ส่วนแสดงปฏิทินและสถานะการจองรายเดือน
  # ----------------------------------------------------
  st.markdown("---")
  st.subheader("📅 ปฏิทินสถานะการจองห้องประชุม")

  # เลือกเดือนและปีสำหรับดูปฏิทิน
  col_m1, col_m2 = st.columns(2)
  with col_m1:
    selected_year = st.selectbox(
        "เลือกปี",
        range(datetime.date.today().year, datetime.date.today().year + 3),
    )
  with col_m2:
    month_names = {
        1: "มกราคม",
        2: "กุมภาพันธ์",
        3: "มีนาคม",
        4: "เมษายน",
        5: "พฤษภาคม",
        6: "มิถุนายน",
        7: "กรกฎาคม",
        8: "สิงหาคม",
        9: "กันยายน",
        10: "ตุลาคม",
        11: "พฤศจิกายน",
        12: "ธันวาคม",
    }
    selected_month = st.selectbox(
        "เลือกเดือน",
        options=list(month_names.keys()),
        format_func=lambda x: month_names[x],
        index=datetime.date.today().month - 1,
    )

  # ดึงรายการวันที่ถูกจองแล้วในเดือน/ปีที่เลือก
  booked_dates_in_month = set()
  for b in st.session_state.bookings:
    b_date = datetime.datetime.strptime(b["วันที่"], "%Y-%m-%d").date()
    if b_date.year == selected_year and b_date.month == selected_month:
      booked_dates_in_month.add(b_date.day)

  # สร้างตารางปฏิทินอย่างง่ายแสดงในเดือนนั้นๆ
  import calendar

  cal = calendar.monthcalendar(selected_year, selected_month)
  cal_data = []
  week_days = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"]

  for week in cal:
    week_row = {}
    for i, day in enumerate(week):
      day_str = (
          str(day) if day != 0 else ""
      )  # ถ้าเป็น 0 คือวันนอกเหนือจากเดือนนั้น
      if day != 0:
        if day in booked_dates_in_month:
          day_str = f"🔴 {day} (ถูกจองแล้ว)"
        else:
          day_str = f"🟢 {day} (ว่าง)"
      week_row[week_days[i]] = day_str
    cal_data.append(week_row)

  st.dataframe(pd.DataFrame(cal_data), use_container_width=True)
  st.caption("คำอธิบาย: 🔴 = มีการจองแล้วในวันนี้ | 🟢 = วันที่ยังว่างอยู่")

  # ----------------------------------------------------
  # ฟอร์มกรอกข้อมูลการจอง
  # ----------------------------------------------------
  st.markdown("---")
  with st.form("booking_form"):
    st.subheader("📝 แบบฟอร์มจองห้องประชุม")

    # เลือก วัน เดือน ปี
    booking_date = st.date_input(
        "เลือกวันที่ต้องการจอง",
        value=datetime.date.today(),
        min_value=datetime.date.today(),
    )

    # เลือกช่วงเวลา
    time_slot = st.selectbox(
        "ช่วงเวลาที่ใช้ห้อง",
        ["ครึ่งวันเช้า", "ครึ่งวันบ่าย", "เต็มวัน"],
    )

    # เรื่องที่ประชุม
    meeting_topic = st.text_input("เรื่องที่ประชุม / วาระการประชุม")

    # ผู้จอง
    booker_name = st.text_input("ชื่อผู้จอง")

    # ส่วน-ฝ่าย (ตามที่ระบุ)
    department = st.selectbox(
        "ส่วน / ฝ่าย",
        ["บริหาร", "ยุทธศาสตร์", "สุขภาพ", "มาตรฐาน", "สินค้า", "อื่นๆ"],
    )

    # ปุ่มกดบันทึก
    submit_button = st.form_submit_button(label="ยืนยันการจอง")

    if submit_button:
      if meeting_topic and booker_name:
        new_booking = {
            "วันที่": booking_date.strftime("%Y-%m-%d"),
            "ช่วงเวลา": time_slot,
            "เรื่องที่ประชุม": meeting_topic,
            "ผู้จอง": booker_name,
            "ส่วน/ฝ่าย": department,
        }
        st.session_state.bookings.append(new_booking)
        st.success("🎉 จองห้องประชุมสำเร็จเรียบร้อยแล้ว!")
        st.rerun()
      else:
        st.warning("⚠️ กรุณากรอก 'เรื่องที่ประชุม' และ 'ชื่อผู้จอง' ให้ครบถ้วน")

  # ----------------------------------------------------
  # แสดงรายการจองทั้งหมด
  # ----------------------------------------------------
  st.markdown("---")
  st.subheader("📋 รายการจองห้องประชุมทั้งหมด")

  if len(st.session_state.bookings) > 0:
    df_bookings = pd.DataFrame(st.session_state.bookings)
    st.dataframe(df_bookings, use_container_width=True)
  else:
    st.info("ยังไม่มีรายการจองห้องประชุมในขณะนี้")
