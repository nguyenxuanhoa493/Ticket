#!/usr/bin/env python3
"""
Script để tạo user mới trong bảng users của Supabase
Sử dụng: python create_user.py
"""

import hashlib
from database import SupabaseHelper
import sys


def hash_password(password):
    """Mã hóa password bằng SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()


def create_user():
    """Tạo user mới"""
    print("🔐 Tạo User Mới cho Hệ thống Ticket Management")
    print("=" * 50)

    try:
        # Khởi tạo database helper
        db = SupabaseHelper()

        # Nhập thông tin user
        username = input("Nhập username: ").strip()
        if not username:
            print("❌ Username không được để trống!")
            return

        password = input("Nhập password: ").strip()
        if not password:
            print("❌ Password không được để trống!")
            return

        full_name = input("Nhập họ tên đầy đủ: ").strip()
        if not full_name:
            print("❌ Họ tên không được để trống!")
            return

        project = input("Nhập tên project: ").strip()
        if not project:
            print("❌ Project không được để trống!")
            return

        is_admin_input = input("Có phải admin không? (y/N): ").strip().lower()
        is_admin = is_admin_input in ["y", "yes", "1", "true"]

        # Kiểm tra username đã tồn tại chưa
        existing_user = db.get_user_by_username(username)
        if existing_user:
            print(f"❌ Username '{username}' đã tồn tại!")
            return

        # Tạo user mới
        print("\n🔄 Đang tạo user...")
        result = db.create_user(username, password, full_name, project, is_admin)

        if result:
            print("✅ Tạo user thành công!")
            print(f"📋 Thông tin user:")
            print(f"   - ID: {result.get('id')}")
            print(f"   - Username: {result.get('username')}")
            print(f"   - Họ tên: {result.get('full_name')}")
            print(f"   - Project: {result.get('project')}")
            print(f"   - Admin: {'Có' if result.get('is_admin') else 'Không'}")
            print(f"   - Password hash: {result.get('password_hash')}")
        else:
            print("❌ Lỗi khi tạo user!")

    except Exception as e:
        print(f"❌ Lỗi: {e}")


if __name__ == "__main__":
    create_user()
