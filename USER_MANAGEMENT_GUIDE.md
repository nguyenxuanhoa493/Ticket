# 👥 Hướng dẫn Quản lý User (Administrator)

## 🔐 Quyền truy cập

Tính năng quản lý user chỉ hiển thị cho các tài khoản có quyền **Administrator** (`is_admin = true`).

## 🎯 Tính năng chính

### 1. **Xem danh sách Users**

-   Hiển thị tất cả users trong hệ thống
-   Thông tin bao gồm: ID, Username, Họ tên, Project, Quyền Admin, Ngày tạo
-   Layout dạng bảng với các nút hành động

### 2. **➕ Thêm User mới**

-   **Trường bắt buộc:**
    -   Username (duy nhất)
    -   Mật khẩu
    -   Họ và tên
    -   Project
-   **Tùy chọn:**
    -   Quyền Administrator (checkbox)
-   **Validation:**
    -   Kiểm tra username đã tồn tại
    -   Tất cả trường bắt buộc phải được điền

### 3. **✏️ Sửa User**

-   Cập nhật thông tin user hiện có
-   Có thể đổi mật khẩu (để trống nếu không đổi)
-   Không được trùng username với user khác
-   Tự động hash mật khẩu bằng SHA256

### 4. **🗑️ Xóa User**

-   Hiển thị modal xác nhận trước khi xóa
-   **Bảo vệ:** Không thể xóa chính mình
-   **Lưu ý:** Tickets của user đã xóa vẫn được giữ lại

## 📋 Quy trình sử dụng

### Để truy cập tính năng:

1. Đăng nhập với tài khoản Administrator
2. Chọn tab **"👥 Quản lý Users"**
3. Thực hiện các thao tác cần thiết

### Thêm user mới:

1. Click **"➕ Thêm User"**
2. Điền đầy đủ thông tin trong form
3. Chọn quyền Administrator nếu cần
4. Click **"💾 Tạo User"**

### Sửa user:

1. Click nút **"✏️"** trong hàng của user cần sửa
2. Cập nhật thông tin mong muốn
3. Điền mật khẩu mới nếu muốn đổi (hoặc để trống)
4. Click **"💾 Cập nhật"**

### Xóa user:

1. Click nút **"🗑️"** trong hàng của user cần xóa
2. Xem lại thông tin trong modal xác nhận
3. Click **"🗑️ Xác nhận xóa"** để thực hiện

## ⚠️ Lưu ý quan trọng

### Bảo mật:

-   ✅ Password được hash SHA256 trước khi lưu database
-   ✅ Không thể xóa chính mình
-   ✅ Validation username trùng lặp
-   ✅ Tất cả thao tác yêu cầu xác nhận

### Phân quyền:

-   **Administrator:**
    -   Xem tất cả tickets (mọi project)
    -   Quản lý toàn bộ users
    -   Truy cập menu "Quản lý Users"
-   **User thường:**
    -   Chỉ xem tickets của project mình
    -   Không có quyền quản lý users
    -   Chỉ có tab "Quản lý Tickets"

### Data integrity:

-   Tickets của user đã xóa vẫn tồn tại
-   Foreign key `created_by` được set NULL khi xóa user
-   Project filtering vẫn hoạt động bình thường

## 🔄 Best Practices

1. **Tạo user:**

    - Đặt username dễ nhớ và có ý nghĩa
    - Password đủ mạnh cho bảo mật
    - Gán đúng project cho user

2. **Phân quyền:**

    - Chỉ gán quyền admin khi thực sự cần thiết
    - Thường xuyên review danh sách admin

3. **Bảo trì:**
    - Xóa user không còn sử dụng
    - Cập nhật project khi có thay đổi tổ chức
    - Thay đổi password định kỳ

## 🚨 Troubleshooting

### Lỗi "Username đã tồn tại":

-   Chọn username khác
-   Kiểm tra user đã bị xóa chưa

### Không thể xóa user:

-   Không thể xóa chính mình (🚫 hiển thị)
-   Kiểm tra quyền administrator

### Modal không hiển thị:

-   Refresh trang web
-   Kiểm tra kết nối internet
-   Đảm bảo đang dùng tài khoản admin

### Lỗi cập nhật password:

-   Đảm bảo password không để trống khi tạo mới
-   Khi sửa: có thể để trống để giữ password cũ
