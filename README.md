# 🎫 Ứng dụng Quản lý Ticket với Streamlit & Supabase

## Cài đặt

1. Cài đặt các dependency:

```bash
pip install -r requirements.txt
```

2. Tạo file `.env` trong thư mục gốc với nội dung:

```env
SUPABASE_URL=your_supabase_url_here
SUPABASE_ANON_KEY=your_supabase_anon_key_here
```

**Cách tạo file .env:**

```bash
# Tạo file .env bằng command line:
touch .env

# Hoặc tạo thủ công và thêm nội dung:
echo "SUPABASE_URL=your_supabase_url_here" > .env
echo "SUPABASE_ANON_KEY=your_supabase_anon_key_here" >> .env
```

3. Thay thế các giá trị trong file `.env`:

    - Lấy `SUPABASE_URL` và `SUPABASE_ANON_KEY` từ project Supabase của bạn
    - Vào project Supabase → Settings → API → Copy URL và anon key

4. **Tạo bảng và dữ liệu trong Supabase**:

    - Tạo 2 bảng `users` và `tickets` theo cấu trúc ở phần "Cấu trúc Database"
    - Tạo user đầu tiên trong bảng `users`:

    ```sql
    INSERT INTO users (username, password_hash, full_name, project, is_admin)
    VALUES (
      'admin',
      'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', -- password: admin123
      'Administrator',
      'ALL_PROJECTS',
      true
    );
    ```

    **Hoặc sử dụng script helper:**

    ```bash
    python create_user.py
    ```

5. **Migrate Database** (nếu đã có bảng tickets cũ):

    ```bash
    # Kiểm tra cấu trúc database
    python migrate_database.py check

    # Thực hiện migration tự động
    python migrate_database.py
    ```

    **Hoặc chạy SQL thủ công trong Supabase:**

    - Mở SQL Editor trong Supabase Dashboard
    - Copy và chạy nội dung file `update_tickets_table.sql`

6. **Đăng nhập**:
    - Chạy ứng dụng: `streamlit run app.py`
    - Nhập username: `admin` và password: `admin123`
    - ✅ Chọn "Ghi nhớ đăng nhập" để không phải đăng nhập lại (30 ngày)
    - Nếu không chọn ghi nhớ: chỉ lưu trong session hiện tại

## Cấu trúc Database

### Bảng `users` trong Supabase:

```sql
CREATE TABLE public.users (
  id serial not null,
  username character varying(50) not null,
  password_hash character varying(255) not null,
  full_name character varying(100) not null,
  is_admin boolean null default false,
  created_at timestamp with time zone null default now(),
  project text null,
  constraint users_pkey primary key (id),
  constraint users_username_key unique (username)
) TABLESPACE pg_default;
```

### Bảng `tickets` trong Supabase (cập nhật):

```sql
CREATE TABLE IF NOT EXISTS tickets (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    project TEXT NOT NULL,
    ngay_yeu_cau TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    phan_loai VARCHAR(50) NOT NULL,
    nen_tang VARCHAR(50) NOT NULL,
    noi_dung TEXT NOT NULL,
    link TEXT,
    uu_tien VARCHAR(20) NOT NULL,
    thoi_han_mong_muon DATE,
    ngay_hoan_thanh DATE,
    trang_thai VARCHAR(20) DEFAULT 'Chờ xử lý',
    ghi_chu TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**Giải thích các cột mới:**

-   `created_by`: ID người tạo ticket (liên kết với bảng users)
-   `project`: Project mà ticket thuộc về (lấy từ user tạo ticket)

**Giải thích bảng users:**

-   `id`: ID duy nhất của user
-   `username`: Tên đăng nhập (unique)
-   `password_hash`: Mật khẩu đã mã hóa SHA256
-   `full_name`: Họ tên đầy đủ
-   `is_admin`: Quyền admin (có thể xem tất cả tickets)
-   `project`: Project mà user thuộc về

## Chạy ứng dụng

```bash
streamlit run app.py
```

## Tính năng

-   🔐 **Đăng nhập bảo mật**: Authentication từ bảng users trong Supabase
-   💾 **Ghi nhớ đăng nhập**: Lưu trạng thái login vào file local (30 ngày)
-   👥 **Quản lý người dùng**: Hệ thống users với roles và projects
-   🏢 **Quản lý project**: Mỗi user thuộc một project, tickets được filter theo project
-   👑 **Quyền admin**: Admin có thể xem tất cả tickets của mọi project
-   ✅ Xem danh sách tickets (theo project)
-   ➕ Thêm ticket mới (tự động gán user và project)
-   ✏️ Cập nhật ticket
-   🗑️ Xóa ticket
-   📊 Thống kê tổng quan (hiển thị ở đầu trang)
-   🔍 Lọc theo trạng thái, ưu tiên, phân loại
-   📅 Quản lý thời hạn và ngày hoàn thành
-   📝 Ghi chú chi tiết cho từng ticket
-   🔒 Kết nối bảo mật với Supabase
-   🎨 **Light theme**: Giao diện sáng mặc định

## Cấu trúc file

-   `app.py` - Ứng dụng Streamlit chính
-   `database.py` - Module kết nối và thao tác với Supabase
-   `create_user.py` - Script helper để tạo user mới
-   `migrate_database.py` - Script migration database tự động
-   `update_tickets_table.sql` - SQL script để cập nhật bảng tickets
-   `requirements.txt` - Danh sách dependencies
-   `.env` - File cấu hình Supabase (cần tạo thủ công)
-   `.streamlit/config.toml` - Cấu hình Streamlit (theme light mặc định)
-   `.streamlit_login_cache` - File lưu trạng thái login (tự động tạo)
-   `USER_MANAGEMENT_GUIDE.md` - Hướng dẫn quản lý user cho admin

## Lưu ý

-   File `
