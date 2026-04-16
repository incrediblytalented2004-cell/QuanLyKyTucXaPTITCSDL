import mysql.connector

def setup_database():
    try:
        print("=" * 55)
        print("  SETUP DATABASE - QUAN LY KY TUC XA (PTIT)")
        print("=" * 55)
        nhap_pass = input("=> Nhap mat khau MySQL (khong co thi Enter): ")

        print("\nDang ket noi toi MySQL Server...")
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password=nhap_pass
        )
        cursor = conn.cursor()
        print("Ket noi thanh cong!")

        
        print("\nDang tao co so du lieu 'PTIT_QuanLyKTX'...")
        cursor.execute("CREATE DATABASE IF NOT EXISTS PTIT_QuanLyKTX")
        cursor.execute("USE PTIT_QuanLyKTX")

      
        print("Xoa cac bang cu (neu co)...")
        cursor.execute("DROP TABLE IF EXISTS ThietBi")
        cursor.execute("DROP TABLE IF EXISTS QuanLyPhi")
        cursor.execute("DROP TABLE IF EXISTS PhanPhong")
        cursor.execute("DROP TABLE IF EXISTS SinhVien")
        cursor.execute("DROP TABLE IF EXISTS Phong")

        
        cursor.execute("DROP TRIGGER IF EXISTS Check_Phong_Day")
        cursor.execute("DROP TRIGGER IF EXISTS Update_Phong_After_In")
        cursor.execute("DROP TRIGGER IF EXISTS Update_Phong_After_Out")
        cursor.execute("DROP TRIGGER IF EXISTS Check_Phi_Am")

        
        print("Dang tao bang SinhVien...")
        cursor.execute("""
            CREATE TABLE SinhVien (
                mssv VARCHAR(15) PRIMARY KEY,
                ho_ten VARCHAR(100) NOT NULL,
                nam_sinh INT,
                lop VARCHAR(50),
                sdt VARCHAR(15),
                trang_thai VARCHAR(20) DEFAULT 'Dang o'
            )
        """)

        
        print("Dang tao bang Phong...")
        cursor.execute("""
            CREATE TABLE Phong (
                ma_phong VARCHAR(10) PRIMARY KEY,
                loai_phong VARCHAR(50),
                SoLuongToiDa INT NOT NULL,
                SoLuongHienTai INT DEFAULT 0,
                tinh_trang VARCHAR(20) DEFAULT 'Con trong',
                gia_phong DECIMAL(10, 2)
            )
        """)

       
        print("Dang tao bang PhanPhong...")
        cursor.execute("""
            CREATE TABLE PhanPhong (
                id_pp INT AUTO_INCREMENT PRIMARY KEY,
                mssv VARCHAR(15),
                ma_phong VARCHAR(10),
                ngay_vao DATE,
                ngay_ra DATE,
                FOREIGN KEY (mssv) REFERENCES SinhVien(mssv),
                FOREIGN KEY (ma_phong) REFERENCES Phong(ma_phong)
            )
        """)

        
        print("Dang tao bang QuanLyPhi...")
        cursor.execute("""
            CREATE TABLE QuanLyPhi (
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
            )
        """)

        
        print("Dang tao bang ThietBi...")
        cursor.execute("""
            CREATE TABLE ThietBi (
                ma_tb INT AUTO_INCREMENT PRIMARY KEY,
                ma_phong VARCHAR(10),
                ten_tb VARCHAR(50),
                tinh_trang VARCHAR(20) DEFAULT 'Tot',
                FOREIGN KEY (ma_phong) REFERENCES Phong(ma_phong)
            )
        """)

        
        print("Dang cay cac Triggers...")

        cursor.execute("""
            CREATE TRIGGER `Check_Phong_Day`
            BEFORE INSERT ON `PhanPhong` FOR EACH ROW
            BEGIN
                DECLARE v_hien_tai INT;
                DECLARE v_toi_da INT;
                SELECT SoLuongHienTai, SoLuongToiDa INTO v_hien_tai, v_toi_da
                FROM Phong WHERE ma_phong = NEW.ma_phong;
                IF v_hien_tai >= v_toi_da THEN
                    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Loi: Phong nay da day, khong the them sinh vien!';
                END IF;
            END
        """)

        cursor.execute("""
            CREATE TRIGGER `Update_Phong_After_In`
            AFTER INSERT ON `PhanPhong` FOR EACH ROW
            BEGIN
                UPDATE Phong SET SoLuongHienTai = SoLuongHienTai + 1 WHERE ma_phong = NEW.ma_phong;
                UPDATE Phong SET tinh_trang = 'Day' WHERE ma_phong = NEW.ma_phong AND SoLuongHienTai >= SoLuongToiDa;
            END
        """)

        cursor.execute("""
            CREATE TRIGGER `Update_Phong_After_Out`
            AFTER UPDATE ON `PhanPhong` FOR EACH ROW
            BEGIN
                IF NEW.ngay_ra IS NOT NULL AND OLD.ngay_ra IS NULL THEN
                    UPDATE Phong SET SoLuongHienTai = SoLuongHienTai - 1, tinh_trang = 'Con trong'
                    WHERE ma_phong = NEW.ma_phong;
                END IF;
            END
        """)

        cursor.execute("""
            CREATE TRIGGER `Check_Phi_Am`
            BEFORE INSERT ON `QuanLyPhi` FOR EACH ROW
            BEGIN
                IF NEW.tien_dien < 0 OR NEW.tien_nuoc < 0 OR NEW.tien_phong < 0 THEN
                    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Loi: Cac khoan phi khong duoc la so am!';
                END IF;
            END
        """)

        conn.commit()
        conn.close()

        print("\n" + "=" * 55)
        print("  SETUP HOAN TAT! Database da san sang.")
        print("  Chay 'python main.py' de mo ung dung.")
        print("=" * 55)

    except mysql.connector.Error as e:
        print(f"\n[LOI KET NOI MYSQL]: {e}")
        print("=> Kiem tra XAMPP - MySQL da bat chua? Mat khau co dung khong?")


if __name__ == "__main__":
    setup_database()
