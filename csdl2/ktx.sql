CREATE DATABASE IF NOT EXISTS PTIT_QuanLyKTX;
USE PTIT_QuanLyKTX;

------------------------------------------------------
CREATE TABLE IF NOT EXISTS SinhVien (
    mssv VARCHAR(15) PRIMARY KEY, 
    ho_ten VARCHAR(100) NOT NULL,
    nam_sinh INT,
    lop VARCHAR(50), 
    sdt VARCHAR(15),
    trang_thai VARCHAR(20) DEFAULT 'Dang o'
);

------------------------------------------------------
CREATE TABLE IF NOT EXISTS Phong (
    ma_phong VARCHAR(10) PRIMARY KEY,
    loai_phong VARCHAR(50),
    SoLuongToiDa INT NOT NULL,
    SoLuongHienTai INT DEFAULT 0,
    tinh_trang VARCHAR(20) DEFAULT 'Con trong',
    gia_phong DECIMAL(10, 2)
);

------------------------------------------------------
CREATE TABLE IF NOT EXISTS PhanPhong (
    id_pp INT AUTO_INCREMENT PRIMARY KEY,
    mssv VARCHAR(15),
    ma_phong VARCHAR(10),
    ngay_vao DATE,
    ngay_ra DATE, 
    FOREIGN KEY (mssv) REFERENCES SinhVien(mssv),
    FOREIGN KEY (ma_phong) REFERENCES Phong(ma_phong)
);

------------------------------------------------------
CREATE TABLE IF NOT EXISTS QuanLyPhi (
    ma_hd INT AUTO_INCREMENT PRIMARY KEY,
    ma_phong VARCHAR(10),
    mssv VARCHAR(15),
    thang INT,
    nam INT,
    tien_phong DECIMAL(10, 2),
    tien_dien DECIMAL(10, 2),
    tien_nuoc DECIMAL(10, 2),
    trang_thai VARCHAR(20) DEFAULT 'Chua dong',
    FOREIGN KEY (ma_phong) REFERENCES Phong(ma_phong),
    FOREIGN KEY (mssv) REFERENCES SinhVien(mssv)
);

------------------------------------------------------
CREATE TABLE IF NOT EXISTS ThietBi (
    ma_tb INT AUTO_INCREMENT PRIMARY KEY,
    ma_phong VARCHAR(10),
    ten_tb VARCHAR(50),
    tinh_trang VARCHAR(20) DEFAULT 'Tot',
    FOREIGN KEY (ma_phong) REFERENCES Phong(ma_phong)
);

------------------------------------------------------
DELIMITER $

------------------------------------------------------
CREATE TRIGGER `Check_Phong_Day`
BEFORE INSERT ON `PhanPhong` FOR EACH ROW
BEGIN
    DECLARE v_hien_tai INT;
    DECLARE v_toi_da INT;
    SELECT SoLuongHienTai, SoLuongToiDa INTO v_hien_tai, v_toi_da 
    FROM Phong WHERE ma_phong = NEW.ma_phong;
    IF v_hien_tai >= v_toi_da THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Loi: Phong nay da day (full), khong the them sinh vien!';
    END IF;
END$

------------------------------------------------------
CREATE TRIGGER `Update_Phong_After_In`
AFTER INSERT ON `PhanPhong` FOR EACH ROW
BEGIN
    UPDATE Phong SET SoLuongHienTai = SoLuongHienTai + 1 WHERE ma_phong = NEW.ma_phong;
    UPDATE Phong SET tinh_trang = 'Day' WHERE ma_phong = NEW.ma_phong AND SoLuongHienTai >= SoLuongToiDa;
END$

------------------------------------------------------
CREATE TRIGGER `Update_Phong_After_Out`
AFTER UPDATE ON `PhanPhong` FOR EACH ROW
BEGIN
    IF NEW.ngay_ra IS NOT NULL AND OLD.ngay_ra IS NULL THEN
        UPDATE Phong SET SoLuongHienTai = SoLuongHienTai - 1, tinh_trang = 'Con trong' WHERE ma_phong = NEW.ma_phong;
    END IF;
END$

------------------------------------------------------
CREATE TRIGGER `Check_Phi_Am`
BEFORE INSERT ON `QuanLyPhi` FOR EACH ROW
BEGIN
    IF NEW.tien_dien < 0 OR NEW.tien_nuoc < 0 OR NEW.tien_phong < 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Loi: Cac khoan phi khong duoc la so am!';
    END IF;
END$

DELIMITER ;

