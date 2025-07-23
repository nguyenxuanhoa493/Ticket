#!/usr/bin/env python3
"""
Script để migrate database - thêm các cột cần thiết vào bảng tickets
Sử dụng: python migrate_database.py
"""

from database import SupabaseHelper
import sys


def migrate_database():
    """Migrate database - thêm cột created_by và project vào bảng tickets"""
    print("🔄 Database Migration - Cập nhật bảng tickets")
    print("=" * 50)

    try:
        # Khởi tạo database helper
        db = SupabaseHelper()

        print("📋 Đang kiểm tra cấu trúc bảng hiện tại...")

        # Kiểm tra xem các cột đã tồn tại chưa
        try:
            # Thử select với cột created_by và project
            test_result = (
                db.supabase.table("tickets")
                .select("id, created_by, project")
                .limit(1)
                .execute()
            )
            print("✅ Bảng tickets đã có đầy đủ cột created_by và project!")
            return True
        except Exception as e:
            print("🔄 Cần cập nhật cấu trúc bảng...")

        # Thực hiện migration
        migration_sql = """
        -- Thêm cột created_by (references users.id)
        ALTER TABLE tickets 
        ADD COLUMN IF NOT EXISTS created_by INTEGER REFERENCES users(id) ON DELETE SET NULL;

        -- Thêm cột project 
        ALTER TABLE tickets 
        ADD COLUMN IF NOT EXISTS project TEXT;
        """

        print("🔨 Đang thực hiện migration...")

        # Thực hiện từng câu lệnh
        try:
            # Thêm cột created_by
            db.supabase.rpc(
                "exec_sql",
                {
                    "sql": "ALTER TABLE tickets ADD COLUMN IF NOT EXISTS created_by INTEGER REFERENCES users(id) ON DELETE SET NULL;"
                },
            ).execute()
            print("✅ Đã thêm cột created_by")
        except Exception as e:
            if "already exists" not in str(e).lower():
                print(f"⚠️ Lỗi khi thêm cột created_by: {e}")

        try:
            # Thêm cột project
            db.supabase.rpc(
                "exec_sql",
                {"sql": "ALTER TABLE tickets ADD COLUMN IF NOT EXISTS project TEXT;"},
            ).execute()
            print("✅ Đã thêm cột project")
        except Exception as e:
            if "already exists" not in str(e).lower():
                print(f"⚠️ Lỗi khi thêm cột project: {e}")

        # Cập nhật project cho tickets hiện tại
        try:
            result = (
                db.supabase.table("tickets")
                .update({"project": "DEFAULT_PROJECT"})
                .is_("project", "null")
                .execute()
            )
            if result.data:
                print(f"✅ Đã cập nhật project cho {len(result.data)} tickets hiện tại")
        except Exception as e:
            print(f"⚠️ Lỗi khi cập nhật project: {e}")

        print("\n✅ Migration hoàn thành!")
        print("🎉 Bạn có thể sử dụng đầy đủ tính năng quản lý project và user!")

        return True

    except Exception as e:
        print(f"❌ Lỗi migration: {e}")
        print("\n💡 Hướng dẫn thay thế:")
        print("1. Vào Supabase Dashboard")
        print("2. Mở SQL Editor")
        print("3. Chạy nội dung file update_tickets_table.sql")
        return False


def check_database_structure():
    """Kiểm tra cấu trúc database"""
    try:
        db = SupabaseHelper()

        print("🔍 Kiểm tra cấu trúc database...")

        # Kiểm tra bảng users
        try:
            users = (
                db.supabase.table("users")
                .select("id, username, full_name, project, is_admin")
                .limit(1)
                .execute()
            )
            print("✅ Bảng users: OK")
        except Exception as e:
            print(f"❌ Bảng users: {e}")
            return False

        # Kiểm tra bảng tickets
        try:
            tickets = (
                db.supabase.table("tickets")
                .select("id, created_by, project")
                .limit(1)
                .execute()
            )
            print("✅ Bảng tickets: OK (có đầy đủ cột)")
        except Exception as e:
            print(f"⚠️ Bảng tickets: Thiếu cột (cần migration)")
            return False

        return True

    except Exception as e:
        print(f"❌ Lỗi kiểm tra: {e}")
        return False


if __name__ == "__main__":
    print("🗃️ Database Management Tool")
    print("=" * 40)

    if len(sys.argv) > 1 and sys.argv[1] == "check":
        check_database_structure()
    else:
        migrate_database()
