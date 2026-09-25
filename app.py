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
      del st.session_state["password"]  # ล้างค่ารหัสผ่านออกจากหน่วยความจำ
    else:
      st.session_state["password_correct"] = False

  if "password_correct" not in st.session_state:
    # แสดงหน้าจอให้กรอกรหัสผ่านครั้งแรก
    st.markdown("## กรุณาใส่รหัสผ่านเพื่อเข้าสู่ระบบจองห้องประชุม")
    st.text_input(
        "รหัสผ่าน", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state and not st.session_state[
        "password_correct"
    ]:
      st.error("รหัสผ่านไม่ถูกต้อง กรุณาลองใหม่อีกครั้ง")
    return False
  elif not st.session_state["password_correct"]:
    # กรณีใส่รหัสผ่านผิด
    st.markdown("## กรุณาใส่รหัสผ่านเพื่อเข้าสู่ระบบจองห้องประชุม")
    st.text_input(
        "รหัสผ่าน", type="password", on_change=password_entered, key="password"
    )
    st.error("รหัสผ่านไม่ถูกต้อง กรุณาลองใหม่อีกครั้ง")
    return False
  else:
    # ผ่านการตรวจสอบแล้ว
    return True


# ตรวจสอบสิทธิ์การเข้าใช้งาน
if check_password():

  # จำลองฐานข้อมูลเก็บข้อมูลการจองไว้ใน st.session_state
  if "bookings" not in st.session_state:
    st.session_state.bookings = []

  st.title("🏢 ระบบจองห้องประชุม")
  st.write("กรอกข้อมูลรายละเอียดการจองห้องประชุมด้านล่างนี้")

  # ฟอร์มกรอกข้อมูลการจอง
  with st.form("booking_form"):
    st.subheader("📝 แบบฟอร์มจองห้องประชุม")

    # เลือก วัน เดือน ปี
    booking_date = st.date_input(
        "เลือกวันที่ประชุม",
        value=datetime.date.today(),
        min_value=datetime.date.today(),
    )

    # เลือกช่วงเวลา
    time_slot = st.selectbox(
        "ช่วงเวลาที่ใช้ห้อง",
        ["ครึ่งวันเช้า (09:00 - 12:00)", "ครึ่งวันบ่าย (13:00 - 16:00)", "เต็มวัน"],
    )

    # เรื่องที่ประชุม
    meeting_topic = st.text_input("เรื่องที่ประชุม / วาระการประชุม")

    # ผู้จอง
    booker_name = st.text_input("ชื่อผู้จอง")

    # ส่วน-ฝ่าย
    department = st.selectbox(
        "ส่วน / ฝ่าย",
        [
            "ฝ่ายบริหาร",
            "ฝ่ายบุคคล (HR)",
            "ฝ่ายบัญชีและการเงิน",
            "ฝ่ายไอที (IT)",
            "ฝ่ายการตลาด",
            "ฝ่ายปฏิบัติการ",
        ],
    )

    # ปุ่มกดบันทึก
    submit_button = st.form_submit_button(label="ยืนยันการจอง")

    if submit_button:
      if meeting_topic and booker_name:
        # บันทึกข้อมูลลงในรายการ
        new_booking = {
            "วันที่": booking_date.strftime("%Y-%m-%d"),
            "ช่วงเวลา": time_slot,
            "เรื่องที่ประชุม": meeting_topic,
            "ผู้จอง": booker_name,
            "ส่วน/ฝ่าย": department,
        }
        st.session_state.bookings.append(new_booking)
        st.success("🎉จองห้องประชุมสำเร็จเรียบร้อยแล้ว!")
      else:
        st.warning("⚠️ กรุณากรอก 'เรื่องที่ประชุม' และ 'ชื่อผู้จอง' ให้ครบถ้วน")

  # แสดงประวัติหรือรายการห้องประชุมที่ถูกจองแล้ว
  st.markdown("---")
  st.subheader("📅 รายการจองห้องประชุมทั้งหมด")

  if len(st.session_state.bookings) > 0:
    df_bookings = pd.DataFrame(st.session_state.bookings)
    st.dataframe(df_bookings, use_container_width=True)
  else:
    st.info("ยังไม่มีรายการจองห้องประชุมในขณะนี้")
