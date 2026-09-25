import calendar
import datetime
import os
import pandas as pd
import streamlit as st

# กำหนดรหัสผ่านสำหรับเข้าใช้งานระบบ
PASSWORD = "1234"  # สามารถเปลี่ยนรหัสผ่านได้ที่นี่
DB_FILE = "bookings.csv"  # ไฟล์สำหรับบันทึกข้อมูลถาวร


def load_bookings():
  """โหลดข้อมูลการจองจากไฟล์ CSV"""
  if os.path.exists(DB_FILE):
    try:
      df = pd.read_csv(DB_FILE)
      return df.to_dict(orient="records")
    except Exception:
      return []
  return []


def save_all_bookings(bookings_list):
  """บันทึกข้อมูลทั้งหมดลงไฟล์ CSV"""
  df = pd.DataFrame(bookings_list)
  df.to_csv(DB_FILE, index=False)


def save_booking_to_csv(new_booking):
  """บันทึกข้อมูลการจองใหม่ลงไฟล์ CSV"""
  current_data = load_bookings()
  current_data.append(new_booking)
  save_all_bookings(current_data)


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

  # โหลดข้อมูลการจองจากไฟล์
  bookings_list = load_bookings()

  # ----------------------------------------------------
  # ส่วนแสดงผลนาฬิกาดิจิตอลเรียลไทม์มุมขวาบน และเมนูหลัก
  # ----------------------------------------------------
  col_head1, col_head2 = st.columns([3, 1])

  with col_head1:
    # ส่วนเมนูด้านบน (Radio แบบแนวนอน)
    selected_menu = st.radio(
        "เลือกเมนู",
        ["📊 แดชบอร์ดภาพรวม", "📝 หน้าจองห้องประชุม", "🗑️ จัดการ/ยกเลิกการจอง"],
        horizontal=True,
        label_visibility="collapsed",
    )

  with col_head2:
    # แสดงนาฬิกาดิจิตอลเรียลไทม์ด้วย HTML/JS
    st.markdown(
        """
        <div style="text-align: right; padding-top: 5px;">
            <span style="font-size: 14px; font-weight: bold; color: #555;" id="realtime-clock">กำลังโหลดเวลา...</span>
        </div>
        <script>
        function updateClock() {
            const now = new Date();
            const hours = String(now.getHours()).padStart(2, '0');
            const minutes = String(now.getMinutes()).padStart(2, '0');
            const seconds = String(now.getSeconds()).padStart(2, '0');
            const dateStr = now.toLocaleDateString('th-TH', { year: 'numeric', month: 'short', day: 'numeric' });
            const timeString = `${dateStr} | ${hours}:${minutes}:${seconds} น.`;
            const clockElement = document.getElementById('realtime-clock');
            if (clockElement) {
                clockElement.innerText = timeString;
            }
        }
        setInterval(updateClock, 1000);
        updateClock();
        </script>
        """,
        unsafe_allow_html=True,
    )

  st.markdown("---")

  # ----------------------------------------------------
  # 1. หน้าแดชบอร์ดภาพรวม
  # ----------------------------------------------------
  if selected_menu == "📊 แดชบอร์ดภาพรวม":
    st.markdown("### 📊 แดชบอร์ดข้อมูลการจองห้องประชุม")
    st.write("แสดงรายการจองห้องประชุม สนง.ปศข.2 (ห้องเล็ก) 10 รายการล่าสุด")

    # สถานะห้องประชุมแบบเรียลไทม์ (วันนี้)
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    is_room_busy = False
    busy_detail = ""
    for b in bookings_list:
      date_str = (
          b.get("วันที่ประชุม")
          or b.get("วันที่")
          or b.get("ว.ด.ป. - ว.ด.ป.ที่")
      )
      if date_str:
        try:
          if " ถึง " in str(date_str):
            start_str, end_str = date_str.split(" ถึง ")
            d_start = datetime.datetime.strptime(
                start_str.strip(), "%Y-%m-%d"
            ).date()
            d_end = datetime.datetime.strptime(
                end_str.strip(), "%Y-%m-%d"
            ).date()
            cur = d_start
            while cur <= d_end:
              if cur.strftime("%Y-%m-%d") == today_str:
                is_room_busy = True
                busy_detail = (
                    f"มีจองช่วง: {b.get('ช่วงเวลา')} (เรื่อง:"
                    f" {b.get('เรื่องที่ประชุม')})"
                )
              cur += datetime.timedelta(days=1)
          else:
            if str(date_str).strip() == today_str:
              is_room_busy = True
              busy_detail = (
                  f"มีจองช่วง: {b.get('ช่วงเวลา')} (เรื่อง:"
                  f" {b.get('เรื่องที่ประชุม')})"
              )
        except Exception:
          pass

    if is_room_busy:
      st.error(
          f"🔴 **สถานะห้องประชุมวันนี้ ({today_str}):** ไม่ว่าง ({busy_detail})"
      )
    else:
      st.success(f"🟢 **สถานะห้องประชุมวันนี้ ({today_str}):** ห้องว่างพร้อมใช้งาน")

    total_bookings = len(bookings_list)
    st.metric(
        label="จำนวนการจองทั้งหมด (ครั้ง)", value=f"{total_bookings} รายการ"
    )

    st.markdown("---")
    search_query = st.text_input(
        "🔍 ค้นหาข้อมูล (พิมพ์ชื่อผู้จอง, เรื่อง, หรือ ฝ่าย)"
    )

    filtered_list = bookings_list
    if search_query:
      filtered_list = [
          b
          for b in bookings_list
          if any(
              search_query.lower() in str(val).lower() for val in b.values()
          )
      ]

    st.markdown("### 📋 10 รายการจองล่าสุด")
    if len(filtered_list) > 0:
      df_bookings = pd.DataFrame(filtered_list)
      df_bookings.insert(0, "ลำดับ", range(1, len(df_bookings) + 1))
      df_recent = df_bookings.tail(10).iloc[::-1]
      st.dataframe(df_recent, use_container_width=True, hide_index=True)
    else:
      st.info("ไม่พบรายการจองที่ค้นหาในระบบ")

    if total_bookings > 0:
      df_all = pd.DataFrame(bookings_list)
      from io import BytesIO

      output = BytesIO()
      with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_all.to_excel(writer, index=False, sheet_name="Booking_Report")
      excel_data = output.getvalue()

      st.download_button(
          label="📥 ดาวน์โหลดรายงานการจองทั้งหมด (.xlsx)",
          data=excel_data,
          file_name=f"Meeting_Room_Bookings_{datetime.date.today()}.xlsx",
          mime=(
              "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
          ),
      )

  # ----------------------------------------------------
  # 2. หน้าจองห้องประชุม
  # ----------------------------------------------------
  elif selected_menu == "📝 หน้าจองห้องประชุม":
    st.markdown("### 🏢 ระบบจองห้องประชุม สนง.ปศข.2 (ห้องเล็ก) V.ทดลอง")
    st.write(
        "ตรวจสอบตารางวันว่างจากปฏิทินด้านล่าง และกรอกรายละเอียดการจองห้องประชุม"
    )

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
    for b in bookings_list:
      date_str = (
          b.get("วันที่ประชุม")
          or b.get("วันที่")
          or b.get("ว.ด.ป. - ว.ด.ป.ที่")
      )
      if date_str:
        try:
          if " ถึง " in str(date_str):
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

    with st.form("booking_form", clear_on_submit=True):
      st.subheader("📝 แบบฟอร์มจองห้องประชุม")

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

      submit_button = st.form_submit_button(label="ยืนยันการจอง")

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
          save_booking_to_csv(new_booking)
          st.success("🎉 จองห้องประชุมสำเร็จเรียบร้อยแล้ว!")
          st.rerun()
        else:
          st.warning("⚠️ กรุณากรอก 'เรื่องที่ประชุม' และ 'ชื่อผู้จอง' ให้ครบถ้วน")

  # ----------------------------------------------------
  # 3. หน้าจัดการ/ยกเลิกการจอง
  # ----------------------------------------------------
  elif selected_menu == "🗑️ จัดการ/ยกเลิกการจอง":
    st.markdown("### 🗑️ จัดการหรือยกเลิกรายการจองห้องประชุม")
    st.write("เลือกรายการที่ต้องการลบเพื่อปลดล็อกวันในปฏิทิน")

    if len(bookings_list) > 0:
      booking_options = []
      for idx, b in enumerate(bookings_list):
        date_val = (
            b.get("วันที่ประชุม")
            or b.get("วันที่")
            or b.get("ว.ด.ป. - ว.ด.ป.ที่")
        )
        label = (
            f"#{idx+1} | วันที่: {date_val} | เรื่อง: {b.get('เรื่องที่ประชุม')}"
            f" | ผู้จอง: {b.get('ผู้จอง')}"
        )
        booking_options.append((idx, label))

      selected_to_delete = st.selectbox(
          "เลือกรายการที่ต้องการยกเลิก",
          options=[item[0] for item in booking_options],
          format_func=lambda x: [
              item[1] for item in booking_options if item[0] == x
          ][0],
      )

      if st.button("❌ ยืนยันการยกเลิกรายการนี้", type="primary"):
        del bookings_list[selected_to_delete]
        save_all_bookings(bookings_list)
        st.success("🗑️ ยกเลิกรายการจองเรียบร้อยแล้ว!")
        st.rerun()

      st.markdown("---")
      st.markdown("### 📋 รายการจองทั้งหมดในระบบ")
      df_all = pd.DataFrame(bookings_list)
      df_all.insert(0, "ลำดับ", range(1, len(df_all) + 1))
      st.dataframe(df_all, use_container_width=True, hide_index=True)
    else:
      st.info("ไม่มีรายการจองในระบบขณะนี้")
