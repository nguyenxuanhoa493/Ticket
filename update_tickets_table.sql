-- Script để cập nhật bảng tickets với các cột mới
-- Chạy script này trong SQL Editor của Supabase

-- Thêm cột created_by (references users.id)
ALTER TABLE tickets 
ADD COLUMN IF NOT EXISTS created_by INTEGER REFERENCES users(id) ON DELETE SET NULL;

-- Thêm cột project 
ALTER TABLE tickets 
ADD COLUMN IF NOT EXISTS project TEXT;

-- Cập nhật project cho các tickets hiện tại (nếu có)
-- Gán project mặc định cho tickets chưa có project
UPDATE tickets 
SET project = 'DEFAULT_PROJECT' 
WHERE project IS NULL;

-- Tạo index để tăng performance
CREATE INDEX IF NOT EXISTS idx_tickets_project ON tickets(project);
CREATE INDEX IF NOT EXISTS idx_tickets_created_by ON tickets(created_by);

-- Thêm comment để ghi chú
COMMENT ON COLUMN tickets.created_by IS 'ID của user tạo ticket';
COMMENT ON COLUMN tickets.project IS 'Project mà ticket thuộc về'; 