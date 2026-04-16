import mysql.connector
import customtkinter as ctk
import tkinter.messagebox as messagebox
from tkinter import ttk

DB_HOST     = "localhost"
DB_USER     = "root"
DB_NAME     = "PTIT_QuanLyKTX"
DB_PASSWORD = "123456"   

class KTXApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("Quản Lý Ký Túc Xá - PTIT")
        self.geometry("1000x750")

        
        self.conn   = None
        self.cursor = None
        self.connect_db()
        if not self.cursor:
            return  

        
        self.table_names   = ["SinhVien", "Phong", "PhanPhong", "QuanLyPhi", "ThietBi"]
        self.current_table = ctk.StringVar(value=self.table_names[0])
        self.columns       = []
        self.entries       = {}
        self.selected_pk   = None   

        self.build_ui()
        self.on_table_change(self.current_table.get())

   
    def connect_db(self):
        try:
            self.conn   = mysql.connector.connect(
                host=DB_HOST, user=DB_USER,
                password=DB_PASSWORD, database=DB_NAME
            )
            self.cursor = self.conn.cursor()
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi Kết Nối",
                f"Không thể kết nối MySQL!\n{e}\n\n"
                "Kiểm tra XAMPP - MySQL đã bật chưa?\n"
                "Kiểm tra mật khẩu trong biến DB_PASSWORD.")
            self.destroy()

    
    def build_ui(self):
        
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(pady=(20, 5))
        ctk.CTkLabel(top, text="🏠 Quản Lý Ký Túc Xá PTIT",
                     font=ctk.CTkFont(size=22, weight="bold")).pack()

       
        self.dropdown = ctk.CTkOptionMenu(
            top, values=self.table_names,
            variable=self.current_table, command=self.on_table_change,
            width=200)
        self.dropdown.pack(pady=8)

        
        self.lbl_selected = ctk.CTkLabel(
            self, text="📌 Chưa chọn hàng nào (click vào danh sách bên dưới để chọn)",
            font=ctk.CTkFont(size=12), text_color="orange")
        self.lbl_selected.pack(pady=(0, 5))

        
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=5)
        for col, (txt, cmd, color) in enumerate([
            ("🔄 View",   self.view_data,   "#4a90d9"),
            ("➕ Insert", self.insert_data, "#27ae60"),
            ("✏️ Update", self.update_data, "#e67e22"),
            ("🗑 Delete",  self.delete_data, "#e74c3c"),
            ("🧹 Clear",  self.clear_inputs,"#7f8c8d"),
        ]):
            ctk.CTkButton(btn_frame, text=txt, command=cmd,
                          width=110, fg_color=color,
                          hover_color="#555").grid(row=0, column=col, padx=6)

       
        self.input_outer = ctk.CTkScrollableFrame(
            self, fg_color="transparent", height=180)
        self.input_outer.pack(fill="x", padx=80, pady=10)

        
        tbl_frame = ctk.CTkFrame(self)
        tbl_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview",
            background="#2a2d2e", foreground="white",
            rowheight=28, fieldbackground="#2a2d2e")
        style.map("Treeview", background=[("selected", "#1f6aa5")])
        style.configure("Treeview.Heading",
            background="#36393f", foreground="white",
            font=("Calibri", 11, "bold"))

        self.tree = ttk.Treeview(tbl_frame, show="headings")
        vsb = ttk.Scrollbar(tbl_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tbl_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tbl_frame.rowconfigure(0, weight=1)
        tbl_frame.columnconfigure(0, weight=1)

        self.tree.bind("<ButtonRelease-1>", self.on_tree_select)

    
    def on_table_change(self, choice):
        if not self.cursor:
            return
        self.selected_pk = None
        self.lbl_selected.configure(
            text="📌 Chưa chọn hàng nào (click vào danh sách bên dưới để chọn)",
            text_color="orange")

        self.cursor.execute(f"DESCRIBE `{choice}`")
        self.columns = [row[0] for row in self.cursor.fetchall()]

        
        for w in self.input_outer.winfo_children():
            w.destroy()
        self.entries.clear()

        
        for i, col in enumerate(self.columns):
            r, c = divmod(i, 2)
            ctk.CTkLabel(self.input_outer, text=col, anchor="e", width=130).grid(
                row=r, column=c*2, padx=(10, 4), pady=4, sticky="e")
            entry = ctk.CTkEntry(self.input_outer, width=220)
            entry.grid(row=r, column=c*2+1, padx=(0, 20), pady=4, sticky="w")
            self.entries[col] = entry

        self.view_data()

    
    def on_tree_select(self, event):
        item = self.tree.focus()
        if not item:
            return
        vals = self.tree.item(item)["values"]
        if not vals:
            return

        
        self.selected_pk = str(vals[0])
        self.lbl_selected.configure(
            text=f"✅ Đã chọn hàng: {self.columns[0]} = '{self.selected_pk}'  (sửa thông tin bên trên rồi bấm Update)",
            text_color="#2ecc71")

        
        self.clear_inputs()
        for idx, col in enumerate(self.columns):
            if idx < len(vals):
                v = vals[idx]
                if v is not None and str(v) != "None":
                    self.entries[col].insert(0, str(v))

    # ------------------------------------------------------------------ #
    def clear_inputs(self):
        for entry in self.entries.values():
            entry.delete(0, "end")

    def get_inputs(self):
        return {col: entry.get() for col, entry in self.entries.items()}

    # ------------------------------------------------------------------ #
    def view_data(self):
        if not self.cursor:
            return
        table = self.current_table.get()
        try:
            self.cursor.execute(f"SELECT * FROM `{table}`")
            rows = self.cursor.fetchall()
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", str(e))
            return

        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = self.columns
        for col in self.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", minwidth=80, width=130)
        for row in rows:
            self.tree.insert("", "end", values=row)

    # ------------------------------------------------------------------ #
    def insert_data(self):
        table  = self.current_table.get()
        inputs = self.get_inputs()
        cols   = ", ".join([f"`{k}`" for k in inputs])
        ph     = ", ".join(["%s"] * len(inputs))
        vals   = tuple(v if v.strip() != "" else None for v in inputs.values())

        try:
            self.cursor.execute(f"INSERT INTO `{table}` ({cols}) VALUES ({ph})", vals)
            self.conn.commit()
            messagebox.showinfo("Thành công", f"Đã thêm dữ liệu vào {table}!")
            self.view_data()
            self.clear_inputs()
        except mysql.connector.Error as err:
            messagebox.showerror("Lỗi Insert", str(err.msg))

    # ------------------------------------------------------------------ #
    def update_data(self):
        
        if not self.selected_pk:
            messagebox.showwarning(
                "Chưa chọn hàng",
                "Hãy CLICK vào một hàng trong danh sách bên dưới trước,\n"
                "sau đó sửa thông tin rồi bấm Update!")
            return

        table   = self.current_table.get()
        inputs  = self.get_inputs()
        pk_col  = self.columns[0]

        
        other_cols = self.columns[1:]
        if not other_cols:
            messagebox.showwarning("Cảnh báo", "Bảng chỉ có 1 cột, không có gì để Update!")
            return

        set_clause = ", ".join([f"`{col}` = %s" for col in other_cols])
        vals = tuple(
            inputs[c] if inputs[c].strip() != "" else None
            for c in other_cols
        ) + (self.selected_pk,)

        query = f"UPDATE `{table}` SET {set_clause} WHERE `{pk_col}` = %s"
        try:
            self.cursor.execute(query, vals)
            self.conn.commit()
            if self.cursor.rowcount == 0:
                messagebox.showwarning(
                    "Không thay đổi",
                    "Dữ liệu không thay đổi hoặc bản ghi không tồn tại.")
            else:
                messagebox.showinfo("Thành công", f"Đã cập nhật bản ghi thành công!")
                self.selected_pk = None
                self.lbl_selected.configure(
                    text="📌 Chưa chọn hàng nào", text_color="orange")
                self.view_data()
                self.clear_inputs()
        except mysql.connector.Error as err:
            messagebox.showerror("Lỗi Update", str(err.msg))

    # ------------------------------------------------------------------ #
    def delete_data(self):
        if not self.selected_pk:
            messagebox.showwarning(
                "Chưa chọn hàng",
                "Hãy CLICK vào một hàng trong danh sách bên dưới trước,\n"
                "sau đó bấm Delete!")
            return

        table  = self.current_table.get()
        pk_col = self.columns[0]

        confirm = messagebox.askyesno(
            "Xác nhận", f"Bạn có chắc muốn xóa bản ghi:\n{pk_col} = '{self.selected_pk}'?")
        if not confirm:
            return

        try:
            self.cursor.execute(
                f"DELETE FROM `{table}` WHERE `{pk_col}` = %s", (self.selected_pk,))
            self.conn.commit()
            messagebox.showinfo("Thành công", "Đã xóa bản ghi!")
            self.selected_pk = None
            self.lbl_selected.configure(
                text="📌 Chưa chọn hàng nào", text_color="orange")
            self.view_data()
            self.clear_inputs()
        except mysql.connector.Error as err:
            messagebox.showerror("Lỗi Delete", str(err.msg))

# ======================================================================= #
if __name__ == "__main__":
    app = KTXApp()
    app.mainloop()
