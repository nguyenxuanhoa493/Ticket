import streamlit as st
from database import SupabaseHelper
from datetime import date, datetime
import pandas as pd
import os
import json
import time
import hashlib

# Cấu hình trang Streamlit với theme sáng
st.set_page_config(
    page_title="Ticket Management App",
    page_icon="🎫",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Load environment variables
from dotenv import load_dotenv

load_dotenv()

# File để lưu trạng thái login
LOGIN_FILE = ".streamlit_login_cache"


def save_login_info(user_data):
    """Lưu thông tin đăng nhập vào file local"""
    try:
        login_data = {
            "user_id": user_data.get("id"),
            "username": user_data.get("username"),
            "full_name": user_data.get("full_name"),
            "project": user_data.get("project"),
            "is_admin": user_data.get("is_admin", False),
            "timestamp": time.time(),
            "expires": time.time() + (30 * 24 * 60 * 60),  # 30 days
        }
        with open(LOGIN_FILE, "w") as f:
            json.dump(login_data, f)
    except Exception as e:
        pass


def load_login_info():
    """Đọc thông tin đăng nhập từ file local"""
    try:
        if os.path.exists(LOGIN_FILE):
            with open(LOGIN_FILE, "r") as f:
                login_data = json.load(f)

            # Kiểm tra xem có hết hạn không
            if login_data.get("expires", 0) > time.time():
                return login_data
        return None
    except Exception as e:
        return None


def remove_login_info():
    """Xóa thông tin đăng nhập"""
    try:
        if os.path.exists(LOGIN_FILE):
            os.remove(LOGIN_FILE)
    except Exception as e:
        pass


# CSS để ẩn sidebar và custom styling
st.markdown(
    """
<style>
    /* Ẩn sidebar */
    .css-1d391kg {display: none;}
    .css-1rs6os {display: none;}
    .css-17eq0hr {display: none;}
    
    /* Custom button styling */
    .stButton > button {
        border-radius: 8px;
        border: 1px solid #ddd;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }
    
    /* Action buttons */
    .action-btn {
        margin: 2px;
        padding: 0.3rem 0.8rem;
        border-radius: 6px;
        border: none;
        cursor: pointer;
        font-size: 0.8rem;
    }
    
    .edit-btn {
        background-color: #0066cc;
        color: white;
    }
    
    .delete-btn {
        background-color: #dc3545;
        color: white;
    }
    
    /* Table styling */
    .dataframe {
        border-radius: 8px;
        border: 1px solid #e0e0e0;
    }
    
    /* Modal width - tăng độ rộng */
    .stDialog > div > div > div > div > section {
        max-width: 1200px !important;
        width: 95vw !important;
    }
    
    /* Login form styling - width nhỏ hơn và căn giữa */
    .login-container {
        max-width: 350px;
        width: 100%;
        margin: 3rem auto;
        padding: 2rem 1.5rem;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        background: white;
    }
    
    /* Center login form vertically */
    .main .block-container {
        display: flex;
        align-items: center;
        min-height: 100vh;
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    
    /* Login form specific */
    .login-container h3 {
        text-align: center;
        margin-bottom: 1.5rem;
        color: #333;
    }
    
    .login-container .stButton > button {
        width: 100%;
        margin-top: 1rem;
    }
    
    .login-container .stCheckbox {
        margin: 1rem 0;
    }
</style>
""",
    unsafe_allow_html=True,
)


# Các options cho dropdown
PHAN_LOAI_OPTIONS = [
    "Lỗi",
    "Task",
]

NEN_TANG_OPTIONS = [
    "Web",
    "APP",
    "Tất cả",
]

UU_TIEN_OPTIONS = ["Thấp", "Trung bình", "Cao", "Khẩn cấp"]

TRANG_THAI_OPTIONS = ["Chờ xử lý", "Đang xử lý", "Hoàn thành", "Hủy bỏ"]


def check_credentials(username, password, db):
    """Kiểm tra thông tin đăng nhập từ database"""
    try:
        user_data = db.authenticate_user(username, password)
        return user_data
    except Exception as e:
        st.error(f"Lỗi xác thực: {e}")
        return None


def show_login_form():
    """Hiển thị form đăng nhập"""
    st.markdown("<div class='login-container'>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        pass
    with col2:
        with st.form("login_form"):
            st.markdown("**Vui lòng nhập thông tin đăng nhập:**")

            username = st.text_input("Tên đăng nhập:", placeholder="Nhập username")
            password = st.text_input(
                "Mật khẩu:", type="password", placeholder="Nhập password"
            )

            remember_me = st.checkbox("Ghi nhớ đăng nhập")

            submitted = st.form_submit_button(
                "🚀 Đăng nhập", type="primary", use_container_width=True
            )
    with col3:
        pass

    if submitted:
        if username and password:
            # Khởi tạo database helper cho authentication
            try:
                db = SupabaseHelper()
                user_data = check_credentials(username, password, db)

                if user_data:
                    # Lưu thông tin user vào session
                    st.session_state.authenticated = True
                    st.session_state.user_id = user_data.get("id")
                    st.session_state.username = user_data.get("username")
                    st.session_state.full_name = user_data.get("full_name")
                    st.session_state.project = user_data.get("project")
                    st.session_state.is_admin = user_data.get("is_admin", False)

                    # Chỉ lưu thông tin nếu chọn ghi nhớ
                    if remember_me:
                        save_login_info(user_data)

                    st.success("✅ Đăng nhập thành công!")
                    st.rerun()
                else:
                    st.error("❌ Tên đăng nhập hoặc mật khẩu không đúng!")
            except Exception as e:
                st.error(f"❌ Lỗi kết nối database: {e}")
        else:
            st.warning("⚠️ Vui lòng nhập đầy đủ thông tin!")

    st.markdown("</div>", unsafe_allow_html=True)


def check_authentication():
    """Kiểm tra trạng thái đăng nhập"""
    # Kiểm tra session state trước
    if st.session_state.get("authenticated", False):
        return True

    # Nếu chưa có trong session, kiểm tra file local
    user_data = load_login_info()
    if user_data:
        st.session_state.authenticated = True
        st.session_state.user_id = user_data.get("user_id")
        st.session_state.username = user_data.get("username")
        st.session_state.full_name = user_data.get("full_name")
        st.session_state.project = user_data.get("project")
        st.session_state.is_admin = user_data.get("is_admin", False)
        return True

    return False


def calculate_completion_days(created_date, completed_date):
    """Tính số ngày hoàn thành"""
    if not created_date or not completed_date:
        return None

    try:
        # Parse dates
        if isinstance(created_date, str):
            # Xử lý các format ngày khác nhau
            created_str = created_date.strip()
            if "T" in created_str:
                created = datetime.strptime(created_str[:10], "%Y-%m-%d")
            else:
                created = datetime.strptime(created_str[:10], "%Y-%m-%d")
        elif isinstance(created_date, datetime):
            created = created_date
        elif isinstance(created_date, date):
            created = datetime.combine(created_date, datetime.min.time())
        else:
            return None

        if isinstance(completed_date, str):
            # Xử lý các format ngày khác nhau
            completed_str = completed_date.strip()
            if "T" in completed_str:
                completed = datetime.strptime(completed_str[:10], "%Y-%m-%d")
            else:
                completed = datetime.strptime(completed_str[:10], "%Y-%m-%d")
        elif isinstance(completed_date, datetime):
            completed = completed_date
        elif isinstance(completed_date, date):
            completed = datetime.combine(completed_date, datetime.min.time())
        else:
            return None

        # Calculate difference
        diff = completed - created
        return max(0, diff.days)  # Không trả về số âm
    except (ValueError, TypeError, AttributeError) as e:
        return None
    except Exception as e:
        return None


def main():
    # Kiểm tra xác thực trước
    if not check_authentication():
        show_login_form()
        return

    try:
        db = SupabaseHelper()
    except Exception as e:
        st.error(f"❌ Lỗi kết nối Supabase: {e}")
        return

    # Khởi tạo session states
    if "show_add_modal" not in st.session_state:
        st.session_state.show_add_modal = False
    if "show_edit_modal" not in st.session_state:
        st.session_state.show_edit_modal = False
    if "edit_ticket_id" not in st.session_state:
        st.session_state.edit_ticket_id = None
    if "show_delete_confirm" not in st.session_state:
        st.session_state.show_delete_confirm = False
    if "delete_ticket_id" not in st.session_state:
        st.session_state.delete_ticket_id = None

    # Session states cho user management
    if "show_add_user_modal" not in st.session_state:
        st.session_state.show_add_user_modal = False
    if "show_edit_user_modal" not in st.session_state:
        st.session_state.show_edit_user_modal = False
    if "edit_user_id" not in st.session_state:
        st.session_state.edit_user_id = None
    if "show_delete_user_confirm" not in st.session_state:
        st.session_state.show_delete_user_confirm = False
    if "delete_user_id" not in st.session_state:
        st.session_state.delete_user_id = None

    # Kiểm tra quyền admin
    is_admin = st.session_state.get("is_admin", False)

    # Header chung với thông tin user
    col1, col2 = st.columns([4, 1])
    with col1:
        user_info = f"👤 {st.session_state.get('full_name', st.session_state.get('username', 'User'))} | 📁 Project: {st.session_state.get('project', 'N/A')}"
        if is_admin:
            user_info += " | 👑 Administrator"
        st.caption(user_info)
    with col2:
        if st.button(
            "🚪 Đăng xuất", help="Đăng xuất khỏi hệ thống", use_container_width=True
        ):
            # Xóa session state
            st.session_state.authenticated = False
            # Xóa tất cả thông tin user
            for key in ["username", "user_id", "full_name", "project", "is_admin"]:
                if key in st.session_state:
                    del st.session_state[key]
            remove_login_info()  # Xóa thông tin đăng nhập
            st.rerun()

    # Navigation menu cho admin
    if is_admin:
        tab1, tab2 = st.tabs(["📋 Quản lý Tickets", "👥 Quản lý Users"])

        with tab1:
            show_tickets_table(db)

        with tab2:
            show_users_management(db)
    else:
        # User thường chỉ xem tickets
        show_tickets_table(db)

    # Modals cho tickets
    if st.session_state.show_add_modal:
        show_add_ticket_modal(db)

    if st.session_state.show_edit_modal:
        show_edit_ticket_modal(db)

    if st.session_state.show_delete_confirm:
        show_delete_confirmation(db)

    # Modals cho users (chỉ cho admin)
    if is_admin:
        if st.session_state.show_add_user_modal:
            show_add_user_modal(db)

        if st.session_state.show_edit_user_modal:
            show_edit_user_modal(db)

        if st.session_state.show_delete_user_confirm:
            show_delete_user_confirmation(db)


def show_tickets_table(db):
    # Header với filters và nút thêm
    col1, col2 = st.columns([4, 1])

    with col1:
        st.header("📋 Danh sách Tickets")

    with col2:
        if st.button("➕ Thêm Ticket", type="primary", use_container_width=True):
            st.session_state.show_add_modal = True
            st.rerun()

    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_trang_thai = st.selectbox(
            "Lọc theo trạng thái:", ["Tất cả"] + TRANG_THAI_OPTIONS
        )
    with col2:
        filter_uu_tien = st.selectbox("Lọc theo ưu tiên:", ["Tất cả"] + UU_TIEN_OPTIONS)
    with col3:
        filter_phan_loai = st.selectbox(
            "Lọc theo phân loại:", ["Tất cả"] + PHAN_LOAI_OPTIONS
        )

    # Lấy dữ liệu từ bảng theo project của user
    try:
        # Áp dụng filters
        filters = {}
        if filter_trang_thai != "Tất cả":
            filters["trang_thai"] = filter_trang_thai
        if filter_uu_tien != "Tất cả":
            filters["uu_tien"] = filter_uu_tien
        if filter_phan_loai != "Tất cả":
            filters["phan_loai"] = filter_phan_loai

        # Lấy tickets theo project của user
        user_project = st.session_state.get("project")
        is_admin = st.session_state.get("is_admin", False)

        if is_admin:
            # Admin có thể xem tất cả tickets
            tickets = db.select_data("tickets", "*", filters if filters else None)
        else:
            # User thường chỉ xem tickets của project mình
            tickets = db.select_tickets_by_project(
                user_project, filters if filters else None
            )

        # Kiểm tra dữ liệu hợp lệ
        if tickets is None:
            tickets = []
        elif not isinstance(tickets, list):
            tickets = []

        try:
            total_tickets = len(tickets) if tickets else 0
            cho_xu_ly = (
                len([t for t in tickets if t.get("trang_thai") == "Chờ xử lý"])
                if tickets
                else 0
            )
            dang_xu_ly = (
                len([t for t in tickets if t.get("trang_thai") == "Đang xử lý"])
                if tickets
                else 0
            )
            hoan_thanh = (
                len([t for t in tickets if t.get("trang_thai") == "Hoàn thành"])
                if tickets
                else 0
            )

            # Tính thời gian hoàn thành trung bình
            completion_times = []
            if tickets:
                completed_tickets = [
                    t for t in tickets if t.get("trang_thai") == "Hoàn thành"
                ]
                for ticket in completed_tickets:
                    try:
                        days = calculate_completion_days(
                            ticket.get("ngay_yeu_cau"), ticket.get("ngay_hoan_thanh")
                        )
                        if days is not None and isinstance(days, (int, float)):
                            completion_times.append(days)
                    except Exception:
                        continue

            # Tính thời gian trung bình
            if completion_times and len(completion_times) > 0:
                avg_completion_time = round(
                    sum(completion_times) / len(completion_times), 1
                )
                avg_display = f"{avg_completion_time} ngày"
            else:
                avg_display = "Chưa có dữ liệu"

            # Hiển thị thống kê
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.metric("Tổng tickets", total_tickets)
            with col2:
                st.metric("Chờ xử lý", cho_xu_ly)
            with col3:
                st.metric("Đang xử lý", dang_xu_ly)
            with col4:
                st.metric("Hoàn thành", hoan_thanh)
            with col5:
                st.metric("TG HT trung bình", avg_display)

        except Exception as e:
            st.error(f"Lỗi khi tính toán thống kê: {e}")
            # Hiển thị thống kê cơ bản
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.metric("Tổng tickets", 0)
            with col2:
                st.metric("Chờ xử lý", 0)
            with col3:
                st.metric("Đang xử lý", 0)
            with col4:
                st.metric("Hoàn thành", 0)
            with col5:
                st.metric("TG HT trung bình", "Lỗi tính toán")

        if tickets and len(tickets) > 0:
            # Header cho bảng
            header_cols = st.columns(
                [0.4, 2, 0.7, 0.5, 0.9, 0.9, 0.9, 0.9, 0.9, 1.5, 0.7, 1.2]
            )
            headers = [
                "ID",
                "Nội dung",
                "Phân loại",
                "Nền tảng",
                "Ưu tiên",
                "Trạng thái",
                "Thời hạn",
                "Ngày tạo",
                "Ngày HT",
                "Ghi chú",
                "Số ngày HT",
                "Thao tác",
            ]
            for i, header in enumerate(headers):
                with header_cols[i]:
                    st.markdown(f"**{header}**")

            st.markdown("---")

            # Hiển thị bảng với cột thao tác và số ngày hoàn thành
            for i, ticket in enumerate(tickets):
                # Đảm bảo ticket là dict và có dữ liệu hợp lệ
                if not isinstance(ticket, dict) or not ticket:
                    continue

                cols = st.columns(
                    [0.4, 2, 0.7, 0.5, 0.9, 0.9, 0.9, 0.9, 0.9, 1.5, 0.7, 1.2]
                )

                with cols[0]:
                    st.write(str(ticket.get("id", "")))
                with cols[1]:
                    content = str(ticket.get("noi_dung", ""))
                    display_content = (
                        content[:30] + "..." if len(content) > 30 else content
                    )
                    st.write(display_content)
                with cols[2]:
                    st.write(str(ticket.get("phan_loai", "")))
                with cols[3]:
                    st.write(str(ticket.get("nen_tang", "")))
                with cols[4]:
                    # Ưu tiên với màu sắc
                    priority = str(ticket.get("uu_tien", ""))
                    if priority == "Khẩn cấp":
                        st.markdown(f"🔴 {priority}")
                    elif priority == "Cao":
                        st.markdown(f"🟠 {priority}")
                    elif priority == "Trung bình":
                        st.markdown(f"🟡 {priority}")
                    else:
                        st.markdown(f"🟢 {priority}")
                with cols[5]:
                    # Trạng thái với màu sắc
                    status = str(ticket.get("trang_thai", ""))
                    if status == "Hoàn thành":
                        st.markdown(f"✅ {status}")
                    elif status == "Đang xử lý":
                        st.markdown(f"🔄 {status}")
                    elif status == "Chờ phản hồi":
                        st.markdown(f"⏳ {status}")
                    else:
                        st.markdown(f"⏸️ {status}")
                with cols[6]:
                    thoi_han = ticket.get("thoi_han_mong_muon", "")
                    st.write(str(thoi_han)[:10] if thoi_han else "")
                with cols[7]:
                    date_str = ticket.get("ngay_yeu_cau", "")
                    st.write(str(date_str)[:10] if date_str else "")
                with cols[8]:
                    # Ngày hoàn thành
                    completed_date = ticket.get("ngay_hoan_thanh", "")
                    st.write(str(completed_date)[:10] if completed_date else "-")
                with cols[9]:
                    # Ghi chú
                    note = str(ticket.get("ghi_chu", ""))
                    display_note = (
                        note[:25] + "..." if len(note) > 25 else note if note else "-"
                    )
                    st.write(display_note)
                with cols[10]:
                    # Số ngày hoàn thành
                    try:
                        completion_days = calculate_completion_days(
                            ticket.get("ngay_yeu_cau"), ticket.get("ngay_hoan_thanh")
                        )
                        if completion_days is not None and isinstance(
                            completion_days, (int, float)
                        ):
                            st.write(f"{completion_days} ngày")
                        else:
                            st.write("-")
                    except Exception:
                        st.write("-")
                with cols[11]:
                    # Cột thao tác
                    try:
                        action_cols = st.columns(2)
                        ticket_id = ticket.get("id")
                        if ticket_id:
                            with action_cols[0]:
                                if st.button(
                                    "✏️", key=f"edit_{ticket_id}", help="Sửa ticket"
                                ):
                                    st.session_state.show_edit_modal = True
                                    st.session_state.edit_ticket_id = ticket_id
                                    st.rerun()
                            with action_cols[1]:
                                if st.button(
                                    "🗑️", key=f"delete_{ticket_id}", help="Xóa ticket"
                                ):
                                    st.session_state.show_delete_confirm = True
                                    st.session_state.delete_ticket_id = ticket_id
                                    st.rerun()
                    except Exception:
                        st.write("Lỗi hiển thị")

        else:
            st.info("Không có ticket nào.")
    except Exception as e:
        st.error(f"Lỗi khi lấy dữ liệu: {e}")


@st.dialog("Thêm Ticket Mới")
def show_add_ticket_modal(db):
    with st.form(
        "add_ticket_form",
        width="stretch",
    ):
        col1, col2 = st.columns(2)

        with col1:
            phan_loai = st.selectbox("Phân loại:", PHAN_LOAI_OPTIONS)
            nen_tang = st.selectbox("Nền tảng:", NEN_TANG_OPTIONS)
            thoi_han_mong_muon = st.date_input("Thời hạn mong muốn:", value=None)

        with col2:
            trang_thai = st.selectbox("Trạng thái:", TRANG_THAI_OPTIONS, index=0)
            uu_tien = st.selectbox("Ưu tiên:", UU_TIEN_OPTIONS, index=1)
            ngay_hoan_thanh = st.date_input("Ngày hoàn thành:", value=None)

        noi_dung = st.text_area("Nội dung ticket:", height=100)
        link = st.text_input("Link liên quan (tùy chọn):")
        ghi_chu = st.text_area("Ghi chú (tùy chọn):", height=80)

        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button(
                "Thêm Ticket", type="primary", use_container_width=True
            )
        with col2:
            cancelled = st.form_submit_button("Hủy", use_container_width=True)

        if cancelled:
            st.session_state.show_add_modal = False
            st.rerun()

        if submitted and noi_dung:
            ticket_data = {
                "phan_loai": phan_loai,
                "nen_tang": nen_tang,
                "noi_dung": noi_dung,
                "uu_tien": uu_tien,
                "trang_thai": trang_thai,
            }

            if link:
                ticket_data["link"] = link
            if ghi_chu:
                ticket_data["ghi_chu"] = ghi_chu
            if thoi_han_mong_muon:
                ticket_data["thoi_han_mong_muon"] = thoi_han_mong_muon.isoformat()
            if ngay_hoan_thanh:
                ticket_data["ngay_hoan_thanh"] = ngay_hoan_thanh.isoformat()

            # Sử dụng insert_ticket với thông tin user
            user_id = st.session_state.get("user_id")
            project = st.session_state.get("project")

            result = db.insert_ticket(ticket_data, user_id, project)
            if result:
                st.success("✅ Thêm ticket thành công!")
                st.session_state.show_add_modal = False
                st.rerun()
            else:
                st.error("❌ Lỗi khi thêm ticket")


@st.dialog("Sửa Ticket")
def show_edit_ticket_modal(db):
    if not st.session_state.edit_ticket_id:
        return

    # Lấy thông tin ticket hiện tại
    tickets = db.select_data("tickets", "*", {"id": st.session_state.edit_ticket_id})
    if not tickets:
        st.error("Không tìm thấy ticket!")
        return

    ticket = tickets[0]

    with st.form("edit_ticket_form"):
        col1, col2 = st.columns(2)

        with col1:
            phan_loai = st.selectbox(
                "Phân loại:",
                PHAN_LOAI_OPTIONS,
                index=(
                    PHAN_LOAI_OPTIONS.index(
                        ticket.get("phan_loai", PHAN_LOAI_OPTIONS[0])
                    )
                    if ticket.get("phan_loai") in PHAN_LOAI_OPTIONS
                    else 0
                ),
            )
            nen_tang = st.selectbox(
                "Nền tảng:",
                NEN_TANG_OPTIONS,
                index=(
                    NEN_TANG_OPTIONS.index(ticket.get("nen_tang", NEN_TANG_OPTIONS[0]))
                    if ticket.get("nen_tang") in NEN_TANG_OPTIONS
                    else 0
                ),
            )
            uu_tien = st.selectbox(
                "Ưu tiên:",
                UU_TIEN_OPTIONS,
                index=(
                    UU_TIEN_OPTIONS.index(ticket.get("uu_tien", UU_TIEN_OPTIONS[1]))
                    if ticket.get("uu_tien") in UU_TIEN_OPTIONS
                    else 1
                ),
            )

        with col2:
            trang_thai = st.selectbox(
                "Trạng thái:",
                TRANG_THAI_OPTIONS,
                index=(
                    TRANG_THAI_OPTIONS.index(
                        ticket.get("trang_thai", TRANG_THAI_OPTIONS[0])
                    )
                    if ticket.get("trang_thai") in TRANG_THAI_OPTIONS
                    else 0
                ),
            )

            # Handle date fields
            current_thoi_han = None
            if ticket.get("thoi_han_mong_muon"):
                try:
                    current_thoi_han = datetime.strptime(
                        ticket.get("thoi_han_mong_muon"), "%Y-%m-%d"
                    ).date()
                except:
                    current_thoi_han = None

            current_ngay_hoan_thanh = None
            if ticket.get("ngay_hoan_thanh"):
                try:
                    current_ngay_hoan_thanh = datetime.strptime(
                        ticket.get("ngay_hoan_thanh"), "%Y-%m-%d"
                    ).date()
                except:
                    current_ngay_hoan_thanh = None

            thoi_han_mong_muon = st.date_input(
                "Thời hạn mong muốn:", value=current_thoi_han
            )
            ngay_hoan_thanh = st.date_input(
                "Ngày hoàn thành:", value=current_ngay_hoan_thanh
            )

        noi_dung = st.text_area(
            "Nội dung ticket:", value=ticket.get("noi_dung", ""), height=100
        )
        link = st.text_input("Link liên quan:", value=ticket.get("link", ""))
        ghi_chu = st.text_area("Ghi chú:", value=ticket.get("ghi_chu", ""), height=80)

        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button(
                "Cập nhật", type="primary", use_container_width=True
            )
        with col2:
            cancelled = st.form_submit_button("Hủy", use_container_width=True)

        if cancelled:
            st.session_state.show_edit_modal = False
            st.session_state.edit_ticket_id = None
            st.rerun()

        if submitted:
            update_data = {
                "phan_loai": phan_loai,
                "nen_tang": nen_tang,
                "noi_dung": noi_dung,
                "uu_tien": uu_tien,
                "trang_thai": trang_thai,
                "link": link,
                "ghi_chu": ghi_chu,
                "updated_at": datetime.now().isoformat(),
            }

            if thoi_han_mong_muon:
                update_data["thoi_han_mong_muon"] = thoi_han_mong_muon.isoformat()
            if ngay_hoan_thanh:
                update_data["ngay_hoan_thanh"] = ngay_hoan_thanh.isoformat()

            result = db.update_data("tickets", update_data, {"id": ticket["id"]})
            if result:
                st.success("✅ Cập nhật ticket thành công!")
                st.session_state.show_edit_modal = False
                st.session_state.edit_ticket_id = None
                st.rerun()
            else:
                st.error("❌ Lỗi khi cập nhật ticket")


@st.dialog("Xác nhận xóa")
def show_delete_confirmation(db):
    if not st.session_state.delete_ticket_id:
        return

    # Lấy thông tin ticket
    tickets = db.select_data("tickets", "*", {"id": st.session_state.delete_ticket_id})
    if not tickets:
        st.error("Không tìm thấy ticket!")
        return

    ticket = tickets[0]

    st.warning("⚠️ **Cảnh báo:** Bạn có chắc chắn muốn xóa ticket này?")

    # Hiển thị thông tin ticket
    st.markdown("### 📋 Thông tin ticket:")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**ID:** {ticket.get('id', 'N/A')}")
        st.write(f"**Phân loại:** {ticket.get('phan_loai', 'N/A')}")
        st.write(f"**Nền tảng:** {ticket.get('nen_tang', 'N/A')}")
    with col2:
        st.write(f"**Ưu tiên:** {ticket.get('uu_tien', 'N/A')}")
        st.write(f"**Trạng thái:** {ticket.get('trang_thai', 'N/A')}")

    st.write(f"**Nội dung:** {ticket.get('noi_dung', 'N/A')}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Xác nhận xóa", type="secondary", use_container_width=True):
            result = db.delete_data("tickets", {"id": ticket["id"]})
            if result:
                st.success("✅ Xóa ticket thành công!")
                st.session_state.show_delete_confirm = False
                st.session_state.delete_ticket_id = None
                st.rerun()
            else:
                st.error("❌ Lỗi khi xóa ticket")

    with col2:
        if st.button("❌ Hủy bỏ", use_container_width=True):
            st.session_state.show_delete_confirm = False
            st.session_state.delete_ticket_id = None
            st.rerun()


def show_users_management(db):
    """Hiển thị giao diện quản lý users cho admin"""

    # Header với nút thêm user
    col1, col2 = st.columns([4, 1])

    with col1:
        st.header("👥 Quản lý Users")

    with col2:
        if st.button("➕ Thêm User", type="primary", use_container_width=True):
            st.session_state.show_add_user_modal = True
            st.rerun()

    # Lấy danh sách users
    users = db.get_all_users()

    if not users:
        st.info("📝 Chưa có user nào trong hệ thống.")
        return

    # Hiển thị bảng users
    st.write("")  # Spacer

    # Header cho bảng
    header_cols = st.columns([0.5, 1.5, 2, 1.5, 0.8, 1.2, 1, 1])
    with header_cols[0]:
        st.markdown("**ID**")
    with header_cols[1]:
        st.markdown("**Username**")
    with header_cols[2]:
        st.markdown("**Họ tên**")
    with header_cols[3]:
        st.markdown("**Project**")
    with header_cols[4]:
        st.markdown("**Admin**")
    with header_cols[5]:
        st.markdown("**Ngày tạo**")
    with header_cols[6]:
        st.markdown("**Sửa**")
    with header_cols[7]:
        st.markdown("**Xóa**")

    st.markdown("---")

    # Hiển thị dữ liệu users
    for i, user in enumerate(users):
        cols = st.columns([0.5, 1.5, 2, 1.5, 0.8, 1.2, 1, 1])

        with cols[0]:
            st.write(user.get("id", "N/A"))
        with cols[1]:
            st.write(user.get("username", "N/A"))
        with cols[2]:
            st.write(user.get("full_name", "N/A"))
        with cols[3]:
            st.write(user.get("project", "N/A"))
        with cols[4]:
            st.write("✅" if user.get("is_admin", False) else "❌")
        with cols[5]:
            created_at = user.get("created_at", "N/A")
            st.write(created_at[:10] if created_at != "N/A" else "N/A")
        with cols[6]:
            if st.button("✏️", key=f"edit_user_{user.get('id')}", help="Sửa user"):
                st.session_state.edit_user_id = user.get("id")
                st.session_state.show_edit_user_modal = True
                st.rerun()
        with cols[7]:
            # Không cho phép xóa chính mình
            current_user_id = st.session_state.get("user_id")
            if user.get("id") != current_user_id:
                if st.button("🗑️", key=f"delete_user_{user.get('id')}", help="Xóa user"):
                    st.session_state.delete_user_id = user.get("id")
                    st.session_state.show_delete_user_confirm = True
                    st.rerun()
            else:
                st.write("🚫")  # Không thể xóa chính mình


@st.dialog("➕ Thêm User Mới")
def show_add_user_modal(db):
    """Modal để thêm user mới"""

    with st.form("add_user_form"):
        st.markdown("### 📝 Thông tin user mới:")

        col1, col2 = st.columns(2)

        with col1:
            username = st.text_input("Username *", placeholder="Nhập username")
            full_name = st.text_input("Họ và tên *", placeholder="Nhập họ và tên")

        with col2:
            password = st.text_input(
                "Mật khẩu *", type="password", placeholder="Nhập mật khẩu"
            )
            project = st.text_input("Project *", placeholder="Nhập tên project")

        is_admin = st.checkbox("Quyền Administrator")

        col1, col2 = st.columns(2)

        with col1:
            if st.form_submit_button(
                "💾 Tạo User", type="primary", use_container_width=True
            ):
                # Validate input
                if not username or not password or not full_name or not project:
                    st.error("❌ Vui lòng điền đầy đủ thông tin bắt buộc!")
                    return

                # Kiểm tra username đã tồn tại
                if db.check_username_exists(username):
                    st.error(f"❌ Username '{username}' đã tồn tại!")
                    return

                # Tạo user mới
                result = db.create_user(
                    username, password, full_name, project, is_admin
                )
                if result:
                    st.success("✅ Tạo user thành công!")
                    st.session_state.show_add_user_modal = False
                    st.rerun()
                else:
                    st.error("❌ Lỗi khi tạo user")

        with col2:
            if st.form_submit_button("❌ Hủy bỏ", use_container_width=True):
                st.session_state.show_add_user_modal = False
                st.rerun()


@st.dialog("✏️ Sửa User")
def show_edit_user_modal(db):
    """Modal để sửa user"""

    if not st.session_state.edit_user_id:
        return

    # Lấy thông tin user hiện tại
    user = db.get_user_by_id(st.session_state.edit_user_id)
    if not user:
        st.error("Không tìm thấy user!")
        return

    with st.form("edit_user_form"):
        st.markdown(f"### ✏️ Sửa user: {user.get('username', 'N/A')}")

        col1, col2 = st.columns(2)

        with col1:
            username = st.text_input("Username *", value=user.get("username", ""))
            full_name = st.text_input("Họ và tên *", value=user.get("full_name", ""))

        with col2:
            password = st.text_input(
                "Mật khẩu mới", type="password", placeholder="Để trống nếu không đổi"
            )
            project = st.text_input("Project *", value=user.get("project", ""))

        is_admin = st.checkbox("Quyền Administrator", value=user.get("is_admin", False))

        col1, col2 = st.columns(2)

        with col1:
            if st.form_submit_button(
                "💾 Cập nhật", type="primary", use_container_width=True
            ):
                # Validate input
                if not username or not full_name or not project:
                    st.error("❌ Vui lòng điền đầy đủ thông tin bắt buộc!")
                    return

                # Kiểm tra username đã tồn tại (exclude user hiện tại)
                if db.check_username_exists(username, exclude_user_id=user.get("id")):
                    st.error(f"❌ Username '{username}' đã tồn tại!")
                    return

                # Tạo dữ liệu cập nhật
                update_data = {
                    "username": username,
                    "full_name": full_name,
                    "project": project,
                    "is_admin": is_admin,
                }

                # Cập nhật password nếu có
                if password:
                    password_hash = hashlib.sha256(password.encode()).hexdigest()
                    update_data["password_hash"] = password_hash

                # Cập nhật user
                result = db.update_user(user.get("id"), update_data)
                if result:
                    st.success("✅ Cập nhật user thành công!")
                    st.session_state.show_edit_user_modal = False
                    st.session_state.edit_user_id = None
                    st.rerun()
                else:
                    st.error("❌ Lỗi khi cập nhật user")

        with col2:
            if st.form_submit_button("❌ Hủy bỏ", use_container_width=True):
                st.session_state.show_edit_user_modal = False
                st.session_state.edit_user_id = None
                st.rerun()


@st.dialog("Xác nhận xóa User")
def show_delete_user_confirmation(db):
    """Modal xác nhận xóa user"""

    if not st.session_state.delete_user_id:
        return

    # Lấy thông tin user
    user = db.get_user_by_id(st.session_state.delete_user_id)
    if not user:
        st.error("Không tìm thấy user!")
        return

    st.warning("⚠️ **Cảnh báo:** Bạn có chắc chắn muốn xóa user này?")

    # Hiển thị thông tin user
    st.markdown("### 👤 Thông tin user:")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**ID:** {user.get('id', 'N/A')}")
        st.write(f"**Username:** {user.get('username', 'N/A')}")
        st.write(f"**Họ tên:** {user.get('full_name', 'N/A')}")
    with col2:
        st.write(f"**Project:** {user.get('project', 'N/A')}")
        st.write(f"**Admin:** {'Có' if user.get('is_admin', False) else 'Không'}")
        st.write(
            f"**Ngày tạo:** {user.get('created_at', 'N/A')[:10] if user.get('created_at') else 'N/A'}"
        )

    st.markdown("---")
    st.info(
        "💡 **Lưu ý:** Các tickets được tạo bởi user này sẽ vẫn được giữ lại nhưng không còn liên kết với user."
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Xác nhận xóa", type="secondary", use_container_width=True):
            result = db.delete_user(user.get("id"))
            if result:
                st.success("✅ Xóa user thành công!")
                st.session_state.show_delete_user_confirm = False
                st.session_state.delete_user_id = None
                st.rerun()
            else:
                st.error("❌ Lỗi khi xóa user")

    with col2:
        if st.button("❌ Hủy bỏ", use_container_width=True):
            st.session_state.show_delete_user_confirm = False
            st.session_state.delete_user_id = None
            st.rerun()


if __name__ == "__main__":
    main()
