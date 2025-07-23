import os
from supabase import create_client, Client
from dotenv import load_dotenv
import streamlit as st
import hashlib

# Load environment variables
load_dotenv()


@st.cache_resource
def init_connection():
    """
    Khởi tạo kết nối với Supabase
    Sử dụng st.cache_resource để cache kết nối
    """
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")

    if not url or not key:
        st.error("Vui lòng cấu hình SUPABASE_URL và SUPABASE_ANON_KEY trong file .env")
        st.stop()

    try:
        supabase: Client = create_client(url, key)
        return supabase
    except Exception as e:
        st.error(f"Lỗi kết nối Supabase: {e}")
        st.stop()


def get_supabase_client():
    """
    Lấy client Supabase đã được cache
    """
    return init_connection()


def hash_password(password):
    """Mã hóa password bằng SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()


# Các hàm tiện ích để làm việc với Supabase
class SupabaseHelper:
    def __init__(self):
        self.supabase = get_supabase_client()

    def authenticate_user(self, username, password):
        """
        Xác thực người dùng từ database

        Args:
            username (str): Tên đăng nhập
            password (str): Mật khẩu

        Returns:
            dict: Thông tin user nếu thành công, None nếu thất bại
        """
        try:
            password_hash = hash_password(password)

            response = (
                self.supabase.table("users")
                .select("*")
                .eq("username", username)
                .eq("password_hash", password_hash)
                .execute()
            )

            if response.data and len(response.data) > 0:
                return response.data[0]
            return None

        except Exception as e:
            st.error(f"Lỗi xác thực: {e}")
            return None

    def get_user_by_username(self, username):
        """
        Lấy thông tin user theo username

        Args:
            username (str): Username

        Returns:
            dict: Thông tin user hoặc None
        """
        try:
            response = (
                self.supabase.table("users")
                .select("*")
                .eq("username", username)
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:
            st.error(f"Lỗi khi lấy thông tin user: {e}")
            return None

    def get_all_users(self):
        """
        Lấy danh sách tất cả users

        Returns:
            list: Danh sách users
        """
        try:
            response = self.supabase.table("users").select("*").order("id").execute()
            return response.data if response.data else []
        except Exception as e:
            st.error(f"Lỗi khi lấy danh sách users: {e}")
            return []

    def get_user_by_id(self, user_id):
        """
        Lấy thông tin user theo ID

        Args:
            user_id (int): ID của user

        Returns:
            dict: Thông tin user hoặc None
        """
        try:
            response = (
                self.supabase.table("users").select("*").eq("id", user_id).execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:
            st.error(f"Lỗi khi lấy thông tin user: {e}")
            return None

    def update_user(self, user_id, user_data):
        """
        Cập nhật thông tin user

        Args:
            user_id (int): ID của user
            user_data (dict): Dữ liệu user mới

        Returns:
            dict: User đã cập nhật hoặc None
        """
        try:
            response = (
                self.supabase.table("users")
                .update(user_data)
                .eq("id", user_id)
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:
            st.error(f"Lỗi khi cập nhật user: {e}")
            return None

    def delete_user(self, user_id):
        """
        Xóa user

        Args:
            user_id (int): ID của user

        Returns:
            bool: True nếu xóa thành công
        """
        try:
            response = self.supabase.table("users").delete().eq("id", user_id).execute()
            return True
        except Exception as e:
            st.error(f"Lỗi khi xóa user: {e}")
            return False

    def check_username_exists(self, username, exclude_user_id=None):
        """
        Kiểm tra username đã tồn tại chưa

        Args:
            username (str): Username cần kiểm tra
            exclude_user_id (int): ID user cần loại trừ (dùng khi edit)

        Returns:
            bool: True nếu username đã tồn tại
        """
        try:
            query = self.supabase.table("users").select("id").eq("username", username)

            if exclude_user_id:
                query = query.neq("id", exclude_user_id)

            response = query.execute()
            return len(response.data) > 0
        except Exception as e:
            st.error(f"Lỗi khi kiểm tra username: {e}")
            return False

    def create_user(self, username, password, full_name, project, is_admin=False):
        """
        Tạo user mới

        Args:
            username (str): Tên đăng nhập
            password (str): Mật khẩu
            full_name (str): Họ tên đầy đủ
            project (str): Project
            is_admin (bool): Có phải admin không

        Returns:
            dict: Thông tin user đã tạo hoặc None
        """
        try:
            password_hash = hash_password(password)

            user_data = {
                "username": username,
                "password_hash": password_hash,
                "full_name": full_name,
                "project": project,
                "is_admin": is_admin,
            }

            response = self.supabase.table("users").insert(user_data).execute()
            return response.data[0] if response.data else None

        except Exception as e:
            st.error(f"Lỗi tạo user: {e}")
            return None

    def select_data(self, table_name, columns="*", filters=None):
        """
        Lấy dữ liệu từ bảng

        Args:
            table_name (str): Tên bảng
            columns (str): Cột cần lấy (mặc định: "*")
            filters (dict): Điều kiện lọc
        """
        try:
            query = self.supabase.table(table_name).select(columns)

            if filters:
                for column, value in filters.items():
                    if value is not None and value != "":
                        query = query.eq(column, value)

            response = query.execute()

            # Đảm bảo luôn trả về list
            if response and hasattr(response, "data") and response.data is not None:
                return response.data if isinstance(response.data, list) else []
            else:
                return []

        except Exception as e:
            st.error(f"Lỗi khi lấy dữ liệu từ {table_name}: {e}")
            return []

    def select_tickets_by_project(self, project, additional_filters=None):
        """
        Lấy tickets theo project

        Args:
            project (str): Tên project
            additional_filters (dict): Các filter bổ sung

        Returns:
            list: Danh sách tickets
        """
        try:
            query = self.supabase.table("tickets").select("*").eq("project", project)

            if additional_filters:
                for column, value in additional_filters.items():
                    if value is not None and value != "":
                        query = query.eq(column, value)

            response = query.execute()
            return response.data if response.data else []

        except Exception as e:
            # Nếu lỗi do thiếu cột project, fallback về select_data thông thường
            error_msg = str(e).lower()
            if "project" in error_msg:
                st.warning(
                    "⚠️ Bảng tickets chưa có cột project. Hiển thị tất cả tickets."
                )
                return self.select_data("tickets", "*", additional_filters)
            else:
                st.error(f"Lỗi khi lấy tickets theo project: {e}")
                return []

    def insert_data(self, table_name, data):
        """
        Thêm dữ liệu vào bảng

        Args:
            table_name (str): Tên bảng
            data (dict or list): Dữ liệu cần thêm
        """
        try:
            response = self.supabase.table(table_name).insert(data).execute()
            return response.data
        except Exception as e:
            st.error(f"Lỗi khi thêm dữ liệu vào {table_name}: {e}")
            return None

    def insert_ticket(self, ticket_data, created_by_user_id, project):
        """
        Thêm ticket với thông tin người tạo và project

        Args:
            ticket_data (dict): Dữ liệu ticket
            created_by_user_id (int): ID người tạo
            project (str): Project

        Returns:
            dict: Ticket đã tạo hoặc None
        """
        try:
            # Thêm thông tin người tạo và project
            ticket_data["created_by"] = created_by_user_id
            ticket_data["project"] = project

            response = self.supabase.table("tickets").insert(ticket_data).execute()
            return response.data[0] if response.data else None

        except Exception as e:
            # Nếu lỗi do thiếu cột, thử insert không có created_by và project
            error_msg = str(e).lower()
            if "created_by" in error_msg or "project" in error_msg:
                st.warning(
                    "⚠️ Bảng tickets chưa được cập nhật với cột created_by và project. Vui lòng chạy script update_tickets_table.sql"
                )

                # Fallback: insert ticket mà không có created_by và project
                fallback_data = ticket_data.copy()
                fallback_data.pop("created_by", None)
                fallback_data.pop("project", None)

                try:
                    response = (
                        self.supabase.table("tickets").insert(fallback_data).execute()
                    )
                    return response.data[0] if response.data else None
                except Exception as fallback_error:
                    st.error(f"Lỗi khi tạo ticket (fallback): {fallback_error}")
                    return None
            else:
                st.error(f"Lỗi khi tạo ticket: {e}")
                return None

    def update_data(self, table_name, data, filters):
        """
        Cập nhật dữ liệu

        Args:
            table_name (str): Tên bảng
            data (dict): Dữ liệu cần cập nhật
            filters (dict): Điều kiện để cập nhật
        """
        try:
            query = self.supabase.table(table_name).update(data)

            for column, value in filters.items():
                query = query.eq(column, value)

            response = query.execute()
            return response.data
        except Exception as e:
            st.error(f"Lỗi khi cập nhật dữ liệu trong {table_name}: {e}")
            return None

    def delete_data(self, table_name, filters):
        """
        Xóa dữ liệu

        Args:
            table_name (str): Tên bảng
            filters (dict): Điều kiện để xóa
        """
        try:
            query = self.supabase.table(table_name).delete()

            for column, value in filters.items():
                query = query.eq(column, value)

            response = query.execute()
            return response.data
        except Exception as e:
            st.error(f"Lỗi khi xóa dữ liệu từ {table_name}: {e}")
            return None
