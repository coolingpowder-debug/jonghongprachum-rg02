import calendar
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

  # ส่วนเมนูด้านบน (Radio แบบแนวนอน)
  st.markdown("### เมนู")
  selected_menu = st.radio(
      "เลือกเมนู",
      ["📊 แดชบอร์ดภาพรวม", "📝 หน้าจองห้องประชุม"],
      horizontal=True,
      label_visibility="collapsed",
  )

  st.markdown("---")

  # ----------------------------------------------------
  # 1. หน้าแดชบอร์ดภาพรวม
  # ----------------------------------------------------
  if selected_menu == "📊 แดชบอร์ดภาพรวม":
    st.title("📊 แดชบอร์ดข้อมูลการจองห้องประชุมล่าสุด")
    st.write("แสดงรายการจองห้องประชุม สนง.ปศข.2 (ห้องเล็ก) 10 รายการล่าสุด")

    total_bookings = len(st.session_state.bookings)
    st.metric(
        label="จำนวนการจองทั้งหมด (ครั้ง)", value=f"{total_bookings} รายการ"
    )

    st.markdown("### 📋 10 รายการจองล่าสุด")
    if total_bookings > 0:
      df_bookings = pd.DataFrame(st.session_state.bookings)
      df_bookings.insert(0, "ลำดับ", range(1, len(df_bookings) + 1))
      df_recent = df_bookings.tail(10).iloc[::-1]
      st.dataframe(df_recent, use_container_width=True, hide_index=True)
    else:
      st.info("ยังไม่มีรายการจองห้องประชุมในขณะนี้")

  # ----------------------------------------------------
  # 2. หน้าจองห้องประชุม (รวมปฏิทินและฟอร์ม)
  # ----------------------------------------------------
  elif selected_menu == "📝 หน้าจองห้องประชุม":
    st.title("🏢 ระบบจองห้องประชุม สนง.ปศข.2 (ห้องเล็ก) V.ทดลอง")
    st.write(
        "ตรวจสอบตารางวันว่างจากปฏิทินด้านล่าง และกรอกรายละเอียดการจองห้องประชุม"
    )

    # ส่วนแสดงปฏิทินรายเดือน
    st.subheader("📅 ปฏิทินสถานะการจองห้องประชุม")

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

    booked_dates_in_month = set()
    for b in st.session_state.bookings:
      # ตรวจสอบว่าเป็นช่วงวันหรือวันเดียว
      date_str = (
          b.get("วันที่ประชุม")
          or b.get("วันที่")
          or b.get("ว.ด.ป. - ว.ด.ป.ที่")
      )
      if date_str:
        try:
          if " ถึง " in str(date_str):
            # กรณีเป็นช่วงวัน (เช่น 2026-09-23 ถึง 2026-09-25)
            start_str, end_str = date_str.split(" ถึง ")
            d_start = datetime.datetime.strptime(
                start_str.strip(), "%Y-%m-%d"
            ).date()
            d_end = datetime.datetime.strptime(
                end_str.strip(), "%Y-%m-%d"
            ).date()
            cur = d_start
            while cur <= d_end:
              if cur.year == selected_year and cur.month == selected_month:
                booked_dates_in_month.add(cur.day)
              cur += datetime.timedelta(days=1)
          else:
            # กรณีวันเดียว
            b_date = datetime.datetime.strptime(
                str(date_str).strip(), "%Y-%m-%d"
            ).date()
            if b_date.year == selected_year and b_date.month == selected_month:
              booked_dates_in_month.add(b_date.day)
        except Exception:
          pass

    cal = calendar.monthcalendar(selected_year, selected_month)
    cal_data = []
    week_days = [
        "จันทร์",
        "อังคาร",
        "พุธ",
        "พฤหัสบดี",
        "ศุกร์",
        "เสาร์",
        "อาทิตย์",
    ]

    for week in cal:
      week_row = {}
      for i, day in enumerate(week):
        day_str = str(day) if day != 0 else ""
        if day != 0:
          if day in booked_dates_in_month:
            day_str = f"🔴 {day} (ถูกจองแล้ว)"
          else:
            day_str = f"🟢 {day} (ว่าง)"
        week_row[week_days[i]] = day_str
      cal_data.append(week_row)

    st.dataframe(pd.DataFrame(cal_data), use_container_width=True)
    st.caption("คำอธิบาย: 🔴 = มีการจองแล้วในวันนี้ | 🟢 = วันที่ยังว่างอยู่")

    st.markdown("---")

    # ฟอร์มกรอกข้อมูลการจอง
    with st.form("booking_form"):
      st.subheader("📝 แบบฟอร์มจองห้องประชุม")

      # เลือกรูปแบบการจอง
      booking_type = st.radio(
          "รูปแบบการจองวันที่", ["จองวันเดียว", "จองเป็นช่วงวัน (หลายวัน)"]
      )

      if booking_type == "จองวันเดียว":
        booking_date = st.date_input(
            "เลือกวันที่ต้องการจอง",
            value=datetime.date.today(),
            min_value=datetime.date.today(),
        )
        date_display = booking_date.strftime("%Y-%m-%d")
      else:
        date_range = st.date_input(
            "เลือกช่วงวันที่ต้องการจอง (วันเริ่มต้น - วันสิ้นสุด)",
            value=(datetime.date.today(), datetime.date.today()),
            min_value=datetime.date.today(),
        )
        if isinstance(date_range, tuple) and len(date_range) == 2:
          date_display = (
              f"{date_range[0].strftime('%Y-%m-%d')} ถึง"
              f" {date_range[1].strftime('%Y-%m-%d')}"
          )
        else:
          date_display = datetime.date.today().strftime("%Y-%m-%d")

      time_slot = st.selectbox(
          "ช่วงเวลาที่ใช้ห้อง",
          ["ครึ่งวันเช้า", "ครึ่งวันบ่าย", "เต็มวัน"],
      )

      meeting_topic = st.text_input("เรื่องที่ประชุม / วาระการประชุม")
      booker_name = st.text_input("ชื่อผู้จอง")

      department = st.selectbox(
          "ส่วน / ฝ่าย",
          [
              "บริหาร",
              "ยุทธศาสตร์",
              "สุขภาพ",
              "มาตรฐาน",
              "สินค้า",
              "ส่งเสริม",
              "อื่นๆ",
          ],
      )

      submit_button = st.form_submit_button(label="เยืนยันการจอง")

      if submit_button:
        if meeting_topic and booker_name:
          new_booking = {
              "วันที่บันทึก": datetime.datetime.now().strftime(
                  "%Y-%m-%d %H:%M:%S"
              ),
              "วันที่ประชุม": date_display,
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
