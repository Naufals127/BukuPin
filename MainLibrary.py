import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import re
import os
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx
from matplotlib.patches import FancyBboxPatch
import numpy as np
from datetime import datetime, timedelta
import customtkinter as ctk
from tkcalendar import DateEntry
from tkinter import simpledialog

def normalize(text):
    return re.sub(r'\s+', ' ', text.strip().lower())

# ================== KELAS BST ==================
class BSTNode:
    def __init__(self, title, penulis, id_buku):
        self.title = title
        self.penulis = penulis
        self.id_buku = id_buku
        self.left = None
        self.right = None
        self.parent = None  # Tambahkan referensi parent untuk tracking

    def validate_bst(self):
        """Validasi struktur BST"""
        def validate_recursive(node, visited_ids=None):
            if visited_ids is None:
                visited_ids = set()
            
            if node is None:
                return True
            
            # Cek duplikasi object reference (bukan ID)
            node_memory_id = id(node)  # Python object ID
            if node_memory_id in visited_ids:
                print(f"ERROR: Shared object reference found at {node.title}")
                return False
            visited_ids.add(node_memory_id)
            
            # Cek parent-child relationship
            if node.left and node.left.parent != node:
                print(f"ERROR: Left child parent mismatch at {node.title}")
                return False
            if node.right and node.right.parent != node:
                print(f"ERROR: Right child parent mismatch at {node.title}")
                return False
            
            return (validate_recursive(node.left, visited_ids) and
                    validate_recursive(node.right, visited_ids))
        
        return validate_recursive(self)
    def get_all_nodes(self):
        """Mendapatkan semua node untuk debugging visualisasi"""
        nodes = []
        
        def collect_nodes(node):
            if node:
                nodes.append({
                    'node': node,
                    'title': node.title,
                    'id': node.id_buku,
                    'parent': node.parent.id_buku if node.parent else None,
                    'left_child': node.left.id_buku if node.left else None,
                    'right_child': node.right.id_buku if node.right else None
                })
                collect_nodes(node.left)
                collect_nodes(node.right)
        
        collect_nodes(self)
        return nodes

    def inorder_traversal(self):
        """In-order traversal untuk sorting buku"""
        books = []
        
        def inorder_helper(node):
            if node:
                inorder_helper(node.left)
                books.append({
                    'id_buku': node.id_buku,
                    'title': node.title,
                    'penulis': node.penulis
                })
                inorder_helper(node.right)
        
        inorder_helper(self)
        return books

    def dfs_partial_search(self, search_term):
        """DFS search untuk pencarian umum"""
        results = []
        search_lower = search_term.lower()
        
        def search_helper(node):
            if node:
                # Check if current node matches
                if (search_lower in node.title.lower() or 
                    search_lower in node.penulis.lower()):
                    results.append(node)
                
                # Continue searching in both subtrees
                search_helper(node.left)
                search_helper(node.right)
        
        search_helper(self)
        return results

class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("BukuPin Login")
        self.root.geometry("1200x600")  # Mengubah ukuran frame
        self.root.resizable(False, False)
        
        self.logged_in_user = None
        self.current_frame = None
        self.show_login_awal()
        print("Initializing LoginApp")

    def clear_window(self):
        """ Clear semua widgets dari main container.
        Memeriksa apakah self.main_frame ada dan memiliki metode winfo_children.
        Jika tidak, coba pakai self.root dengan pengecekan yang sama.
        """
        container = None

        # Cek main_frame dan root secara hati-hati agar aman
        if hasattr(self, 'main_frame') and callable(getattr(self.main_frame, 'winfo_children', None)):
            container = self.main_frame
        elif hasattr(self, 'root') and callable(getattr(self.root, 'winfo_children', None)):
            container = self.root
        else:
            print("Error: Tidak ada container valid dengan metode winfo_children.")
            return

        try:
            for widget in container.winfo_children():
                widget.destroy()
        except Exception as e:
            print(f"Error clearing window: {e}")
   
    def show_login_awal(self):
        """Menampilkan welcome screen dengan modern layout"""
        self.clear_window()

        # Main frame dengan background krem yang memenuhi seluruh window
        main_frame = tk.Frame(self.root, bg="#e6d3c5")
        main_frame.pack(fill="both", expand=True)

        # Left text content - disesuaikan posisi dan ukuran
        left_frame = tk.Frame(main_frame, bg="#e6d3c5")
        left_frame.place(relx=0.08, rely=0.15, relwidth=0.45, relheight=0.7)

        tk.Label(
            left_frame,
            text="HELLO",
            fg="#ac9c8d",
            bg="#e6d3c5",
            font=("Arial", 42, "bold")
        ).pack(anchor="w", pady=(20, 0))

        tk.Label(
            left_frame,
            text="WELCOME BACK!",
            fg="#5A2E35",
            bg="#e6d3c5",
            font=("Arial", 42, "bold")
        ).pack(anchor="w", pady=(0, 20))

        tk.Label(
            left_frame,
            text="Setiap buku adalah dunia baru.\nTemukan dan jelajahi berbagai cerita dan ilmu bersama kami.",
            fg="#7c5a52",
            bg="#e6d3c5",
            font=("Arial", 16),
            justify="left",
            wraplength=450
        ).pack(anchor="w", pady=(10, 40))

        tk.Button(
            left_frame,
            text="GET STARTED",
            command=self.show_login,
            bg="#5A2E35",
            activebackground="#0EA5E9",
            fg="white",
            font=("Arial", 16, "bold"),
            borderwidth=0,
            width=18,
            height=2,
            cursor="hand2"
        ).pack(anchor="w")

        # Right image - disesuaikan posisi dan ukuran
        right_frame = tk.Frame(main_frame, bg="#e6d3c5")
        right_frame.place(relx=0.55, rely=0.1, relwidth=0.4, relheight=0.8)

        try:
            image_path = "book2.png"
            image = Image.open(image_path).resize((450, 450))
            tk_img = ImageTk.PhotoImage(image)
            image_label = tk.Label(right_frame, image=tk_img, bg="#e6d3c5")
            image_label.image = tk_img
            image_label.pack(expand=True)
        except:
            tk.Label(
                right_frame, 
                text="[Gambar Tidak Ditemukan]", 
                fg="#7c5a52", 
                bg="#e6d3c5",
                font=("Arial", 14)
            ).pack(expand=True)

    def show_login(self):
        """Menampilkan login screen with 50:50 layout - gambar kiri, form krem kanan"""
        self.clear_window()

        # Left frame untuk gambar - tepat 50% dari lebar window
        left_frame = tk.Frame(self.root, bg="white", width=600, height=600)
        left_frame.pack(side="left", fill="both", expand=True)
        left_frame.pack_propagate(False)  # Mempertahankan ukuran frame
        
        try:
            image_path = "loginawal.jpeg"
            image = Image.open(image_path).resize((600, 600))
            tk_image = ImageTk.PhotoImage(image)
            label_image = tk.Label(left_frame, image=tk_image)
            label_image.image = tk_image
            label_image.place(x=0, y=0, relwidth=1, relheight=1)
        except:
            tk.Label(
                left_frame, 
                text="[Login Image Not Found]", 
                fg="gray",
                bg="white",
                font=("Arial", 14)
            ).pack(expand=True)

        # Right frame dengan background krem - tepat 50% dari lebar window
        right_frame = tk.Frame(self.root, bg="#e6d3c5", width=600, height=600)
        right_frame.pack(side="right", fill="both", expand=True)
        right_frame.pack_propagate(False)  # Mempertahankan ukuran frame

        # Content wrapper untuk centering
        content_wrapper = tk.Frame(right_frame, bg="#e6d3c5")
        content_wrapper.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8, relheight=0.9)

        # Title
        tk.Label(
            content_wrapper,
            text="BukuPin!",
            font=("Arial Rounded MT Bold", 28, "bold"),
            fg="#8B1E3F",
            bg="#e6d3c5"
        ).pack(pady=(0, 5))

        tk.Label(
            content_wrapper,
            text="LOG IN",
            font=("Arial Rounded MT Bold", 16, "bold"),
            fg="#5A2E35",
            bg="#e6d3c5"
        ).pack(pady=(0, 30))

        # Form container
        form_container = tk.Frame(content_wrapper, bg="#e6d3c5")
        form_container.pack(fill="x", expand=True)

        # Email field
        tk.Label(
            form_container, 
            text="Email", 
            font=("Arial", 12), 
            bg="#e6d3c5", 
            fg="#5A2E35",
            anchor="w"
        ).pack(fill="x", pady=(0, 5))
        
        self.email_entry = tk.Entry(
            form_container, 
            font=("Arial", 12),
            relief="solid",
            borderwidth=1,
            bg="white"
        )
        self.email_entry.pack(fill="x", pady=(0, 15), ipady=5)

        # Password field
        tk.Label(
            form_container, 
            text="Password", 
            font=("Arial", 12), 
            bg="#e6d3c5", 
            fg="#5A2E35",
            anchor="w"
        ).pack(fill="x", pady=(0, 5))
        
        self.password_entry = tk.Entry(
            form_container, 
            font=("Arial", 12), 
            show="*",
            relief="solid",
            borderwidth=1,
            bg="white"
        )
        self.password_entry.pack(fill="x", pady=(0, 10), ipady=5)

        # Forgot password link
        forgot_label = tk.Label(
            form_container,
            text="Forgot Password?",
            font=("Arial", 10, "italic"),
            fg="#A65D5D",
            bg="#e6d3c5",
            cursor="hand2"
        )
        forgot_label.pack(anchor="e", pady=(0, 20))
        forgot_label.bind("<Button-1>", lambda e: self.show_reset_window())

        # Login button
        login_btn = tk.Button(
            form_container,
            text="Log In",
            font=("Arial", 12, "bold"),
            bg="#DA8989",
            fg="white",
            activebackground="#C47777",
            activeforeground="white",
            relief="flat",
            borderwidth=0,
            cursor="hand2",
            height=2,
            command=self.handle_login
        )
        login_btn.pack(fill="x", pady=(0, 15))

        # Error label
        self.error_label = tk.Label(
            form_container, 
            text="", 
            font=("Arial", 10), 
            fg="red", 
            bg="#e6d3c5"
        )
        self.error_label.pack(pady=(0, 10))

        # Sign up link
        signup_label = tk.Label(
            form_container,
            text="Don't have an account? Sign in",
            font=("Arial", 10),
            fg="#5A2E35",
            bg="#e6d3c5",
            cursor="hand2"
        )
        signup_label.pack()
        signup_label.bind("<Button-1>", lambda e: self.show_signup_window())

    def verify_login(self, email, password):
        """Verifikasi data user dari file JSON"""
        try:
            with open(r"user_data.json") as json_file:
                user_data = json.load(json_file)
        except (FileNotFoundError, json.JSONDecodeError):
            return False
        for user in user_data:
            if user.get("email") == email and user.get("password") == password:
                return user
        return None

    def handle_login(self):
        """Handle tombol login"""
        email = self.email_entry.get()
        password = self.password_entry.get()
        user_data = self.verify_login(email, password)
        
        if user_data:
            self.logged_in_user = user_data
            self.username = user_data["username"]  # Menyimpan username untuk fitur pengembalian buku
            self.error_label.configure(text="Login berhasil!", fg="green")
            # Show dashboard after successful login
            self.show_dashboard(user_data["username"])
        else:
            self.error_label.configure(text="Email atau password salah!", fg="red")

    def show_dashboard(self, username=None):
        self.clear_window()  # Hapus tampilan login

        dashboard = LibraryGUI(self.root)  # Panggil tampilan utama
        dashboard.username = username or self.username  # Kirim username ke LibraryGUI
        self.dashboard = dashboard  # Simpan agar tidak terhapus

    def show_signup_window(self):
        """Menampilkan  signup form dengan layout 50:50"""
        self.clear_window()
        self.root.title("Sign In - BukuPin!")

        # Left frame untuk gambar - tepat 50% dari lebar window
        left_frame = tk.Frame(self.root, bg="white", width=600, height=600)
        left_frame.pack(side="left", fill="both", expand=True)
        left_frame.pack_propagate(False)
        
        try:
            image_path = "loginawal.jpeg"
            image = Image.open(image_path).resize((600, 600))
            tk_image = ImageTk.PhotoImage(image)
            label_image = tk.Label(left_frame, image=tk_image)
            label_image.image = tk_image
            label_image.place(x=0, y=0, relwidth=1, relheight=1)
        except:
            tk.Label(
                left_frame, 
                text="[Signup Image Not Found]", 
                fg="gray",
                bg="white",
                font=("Arial", 14)
            ).pack(expand=True)

        # Right frame dengan background krem - tepat 50% dari lebar window
        right_frame = tk.Frame(self.root, bg="#e6d3c5", width=600, height=600)
        right_frame.pack(side="right", fill="both", expand=True)
        right_frame.pack_propagate(False)

        # Content wrapper untuk centering
        content_wrapper = tk.Frame(right_frame, bg="#e6d3c5")
        content_wrapper.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8, relheight=0.9)

        # Title
        tk.Label(
            content_wrapper, 
            text="BukuPin!", 
            font=("Arial Black", 24, "bold"), 
            fg="#8B1E3F", 
            bg="#e6d3c5"
        ).pack(pady=(0, 5))
        
        tk.Label(
            content_wrapper, 
            text="SIGN IN", 
            font=("Arial", 16, "bold"), 
            fg="#5A2E35", 
            bg="#e6d3c5"
        ).pack(pady=(0, 20))

        # Form container
        form_container = tk.Frame(content_wrapper, bg="#e6d3c5")
        form_container.pack(fill="x", expand=True)

        # Fields setup
        fields = [
            ("Username", "username"),
            ("Phone Number", "phone"),
            ("Email", "email"),
            ("Password", "password"),
            ("Major", "major")
        ]
        
        self.entries = {}
        for label_text, field_name in fields:
            tk.Label(
                form_container, 
                text=label_text, 
                font=("Arial", 10), 
                bg="#e6d3c5", 
                fg="#5A2E35",
                anchor="w"
            ).pack(fill="x", pady=(0, 2))
            
            entry = tk.Entry(
                form_container, 
                font=("Arial", 10),
                relief="solid",
                borderwidth=1,
                bg="white"
            )
            entry.pack(fill="x", pady=(0, 8), ipady=3)
            self.entries[field_name] = entry

        # Sign In button
        tk.Button(
            form_container,
            text="Sign In",
            font=("Arial", 12, "bold"),
            borderwidth=0,
            height=2,
            bg="#ce7b6c",
            activebackground="#b15f53",
            fg="white",
            cursor="hand2",
            command=self.handle_signin
        ).pack(pady=(10, 0), fill="x")

    def show_reset_window(self):
        """Menampilkan password reset form dengan layout 50:50"""
        self.clear_window()
        self.root.title("Reset Password")

        # Left frame untuk gambar - tepat 50% dari lebar window
        left_frame = tk.Frame(self.root, bg="white", width=600, height=600)
        left_frame.pack(side="left", fill="both", expand=True)
        left_frame.pack_propagate(False)
        
        try:
            image_path = "loginawal.jpeg"
            image = Image.open(image_path).resize((600, 600))
            tk_image = ImageTk.PhotoImage(image)
            label_image = tk.Label(left_frame, image=tk_image)
            label_image.image = tk_image
            label_image.place(x=0, y=0, relwidth=1, relheight=1)
        except:
            tk.Label(
                left_frame, 
                text="[Reset Image Not Found]", 
                fg="gray",
                bg="white",
                font=("Arial", 14)
            ).pack(expand=True)

        # Right frame dengan background krem - tepat 50% dari lebar window
        right_frame = tk.Frame(self.root, bg="#e6d3c5", width=600, height=600)
        right_frame.pack(side="right", fill="both", expand=True)
        right_frame.pack_propagate(False)

        # Content wrapper untuk centering
        content_wrapper = tk.Frame(right_frame, bg="#e6d3c5")
        content_wrapper.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8, relheight=0.8)

        # Title
        tk.Label(
            content_wrapper, 
            text="BukuPin!", 
            font=("Arial Black", 24, "bold"), 
            fg="#8B1E3F", 
            bg="#e6d3c5"
        ).pack(pady=(0, 5))
        
        tk.Label(
            content_wrapper, 
            text="RESET PASSWORD", 
            font=("Arial", 16, "bold"), 
            fg="#5A2E35", 
            bg="#e6d3c5"
        ).pack(pady=(0, 25))

        # Form container
        form_container = tk.Frame(content_wrapper, bg="#e6d3c5")
        form_container.pack(fill="x", expand=True)

        # Email field
        tk.Label(
            form_container, 
            text="Email", 
            font=("Arial", 12), 
            bg="#e6d3c5", 
            fg="#5A2E35",
            anchor="w"
        ).pack(fill="x", pady=(0, 5))
        
        self.reset_email_entry = tk.Entry(
            form_container, 
            font=("Arial", 12),
            relief="solid",
            borderwidth=1,
            bg="white"
        )
        self.reset_email_entry.pack(fill="x", pady=(0, 15), ipady=5)

        # New Password field
        tk.Label(
            form_container, 
            text="New Password", 
            font=("Arial", 12), 
            bg="#e6d3c5", 
            fg="#5A2E35",
            anchor="w"
        ).pack(fill="x", pady=(0, 5))
        
        self.new_password_entry = tk.Entry(
            form_container, 
            font=("Arial", 12), 
            show="*",
            relief="solid",
            borderwidth=1,
            bg="white"
        )
        self.new_password_entry.pack(fill="x", pady=(0, 15), ipady=5)

        # Confirm New Password field
        tk.Label(
            form_container, 
            text="Confirm New Password", 
            font=("Arial", 12), 
            bg="#e6d3c5", 
            fg="#5A2E35",
            anchor="w"
        ).pack(fill="x", pady=(0, 5))
        
        self.confirm_password_entry = tk.Entry(
            form_container, 
            font=("Arial", 12), 
            show="*",
            relief="solid",
            borderwidth=1,
            bg="white"
        )
        self.confirm_password_entry.pack(fill="x", pady=(0, 15), ipady=5)

        # Error label
        self.reset_error_label = tk.Label(
            form_container, 
            text="", 
            font=("Arial", 10), 
            fg="red", 
            bg="#e6d3c5"
        )
        self.reset_error_label.pack(pady=(0, 15))

        # Reset Password button
        tk.Button(
            form_container,
            text="Reset Password",
            font=("Arial", 12, "bold"),
            bg="#ce7b6c",
            activebackground="#b15f53",
            fg="white",
            height=2,
            cursor="hand2",
            relief="flat",
            borderwidth=0,
            command=self.handle_reset_password
        ).pack(fill="x")
        
    def handle_signin(self):
        """Handle signin form submission"""
        username = self.entries["username"].get()
        phone = self.entries["phone"].get()
        email = self.entries["email"].get()
        password = self.entries["password"].get()
        major = self.entries["major"].get()

        if not phone.isdigit():
            messagebox.showerror("Error", "Nomor telepon hanya boleh angka!")
            return
        if len(password) < 6:
            messagebox.showerror("Error", "Password harus lebih dari 6 karakter!")
            return

        self.save_to_json(username, phone, email, password, major)
        messagebox.showinfo("Sukses", "Data berhasil disimpan!")
        self.show_login()

    def save_to_json(self, username, phone, email, password, major):
        """Menyimpan data user ke JSON file"""
        data = {
            "username": username,
            "phone": phone,
            "email": email,
            "password": password,
            "major": major
        }

        file_path = (r"user_data.json")

        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                try:
                    users = json.load(file)
                    if not isinstance(users, list):
                        users = []
                except json.JSONDecodeError:
                    users = []
        else:
            users = []

        users.append(data)

        with open(file_path, "w") as file:
            json.dump(users, file, indent=4)

    def validate_reset_password(self, new_password, confirm_password):
        """Validasi password reset fields"""
        if not new_password or not confirm_password:
            self.reset_error_label.configure(text="Password tidak boleh kosong!", fg="red")
            return False
        if new_password != confirm_password:
            self.reset_error_label.configure(text="Password tidak cocok! Silakan coba lagi.", fg="red")
            return False
        if len(new_password) <= 6:
            self.reset_error_label.configure(text="Password harus lebih dari 6 karakter!", fg="red")
            return False
        self.reset_error_label.configure(text="Password cocok! Silakan lanjutkan.", fg="green")
        return True

    def handle_reset_password(self):
        """Handle password reset submission"""
        new_password = self.new_password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        email = self.reset_email_entry.get()

        if self.validate_reset_password(new_password, confirm_password):
            if self.reset_password_in_json(email, new_password):
                self.reset_error_label.configure(text="Password berhasil diubah!", fg="green")
                self.root.after(2000, self.show_login)
            else:
                self.reset_error_label.configure(text="Email tidak terdaftar, coba lagi.", fg="red")

    def reset_password_in_json(self, email, new_password):
        """Update password di JSON file"""
        if not email or not new_password:  
            return False

        try:
            with open(r"user_data.json") as json_file:
                user_data = json.load(json_file)
        except (FileNotFoundError, json.JSONDecodeError):
            return False

        user_found = False
        for user in user_data:
            if user.get("email") == email:
                user["password"] = new_password  
                user_found = True
                break

        if not user_found:
            return False

        try:
            with open(r"user_data.json", "w") as json_file:
                json.dump(user_data, json_file, indent=4) 
            return True
        except Exception:
            return False

    def main():
        root = tk.Tk()
        app = LoginApp(root)
        root.mainloop()
     
# ================== MAIN GUI APPLICATION ==================
class LibraryGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Library Management System")
        self.root.geometry("1200x600")
        self.root.configure(bg='#8B4513')

        # Data - PERBAIKAN: Menggunakan nama atribut yang benar
        self.trees = {}  # Tetap untuk kompatibilitas backward
        self.trees_by_genre = {}  # Atribut yang diperlukan
        self.all_books = []
        self.load_default_data()
        
        self.setup_ui()
    
    def load_default_data(self):
        """Load data dari JSON file dengan cadangan ke sample data"""
        try:
            # Coba load dari file JSON utama
            base_dir = os.path.dirname(os.path.abspath(__file__))
            filepath = os.path.join(base_dir, "book.json")
            data = self.load_from_json(filepath)

            if data:
                self.build_trees(data)
                print(f"Successfully loaded {len(data)} books from book.json")
                return
        except Exception as e:
            print(f"Error loading book.json: {e}")
        
        # Jika gagal, coba file alternatif
        try:
            filepath2 = os.path.join(base_dir, "books.json")
            data = self.load_from_json(filepath2)
            if data:
                self.build_trees(data)
                print(f"Successfully loaded {len(data)} books from books.json")
                return
        except Exception as e:
            print(f"Error loading books.json: {e}")
        
        # Jika semua gagal, gunakan sample data
        print("Using sample data as fallback")
        sample_data = [
            {"ID": "001", "Judul": "To Kill a Mockingbird", "Penulis": "Harper Lee", "Genre": "Fiction"},
            {"ID": "002", "Judul": "1984", "Penulis": "George Orwell", "Genre": "Fiction"},
            {"ID": "003", "Judul": "Pride and Prejudice", "Penulis": "Jane Austen", "Genre": "Romance"},
            {"ID": "004", "Judul": "The Great Gatsby", "Penulis": "F. Scott Fitzgerald", "Genre": "Fiction"},
            {"ID": "005", "Judul": "Jane Eyre", "Penulis": "Charlotte Bronte", "Genre": "Romance"},
            {"ID": "006", "Judul": "A Brief History of Time", "Penulis": "Stephen Hawking", "Genre": "Science"},
            {"ID": "007", "Judul": "The Origin of Species", "Penulis": "Charles Darwin", "Genre": "Science"},
            {"ID": "008", "Judul": "Dune", "Penulis": "Frank Herbert", "Genre": "Sci-Fi"},
            {"ID": "009", "Judul": "Foundation", "Penulis": "Isaac Asimov", "Genre": "Sci-Fi"},
            {"ID": "010", "Judul": "The Hobbit", "Penulis": "J.R.R. Tolkien", "Genre": "Fantasy"}
        ]
        self.build_trees(sample_data)
        self.check_duplicate_books(sample_data)
        
        # Debug tree structure
        for genre, tree in self.trees.items():
            print(f"\n=== Tree structure for {genre} ===")
            self.debug_tree_structure(tree)
        
    def load_from_json(self, filename):
        """Load dan validasi JSON data"""
        try:
            filename = os.path.join(os.path.dirname(__file__), filename)
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Validasi struktur data
            if not isinstance(data, list):
                raise ValueError("JSON file should contain a list of books")
            
            validated_data = []
            for i, book in enumerate(data):
                try:
                    # Validasi field yang diperlukan
                    required_fields = ['ID', 'Judul', 'Penulis', 'Genre']
                    for field in required_fields:
                        if field not in book:
                            print(f"Warning: Book {i+1} missing field '{field}', skipping...")
                            continue
                    
                    # Normalisasi data
                    normalized_book = {
                        'ID': str(book['ID']).strip(),
                        'Judul': str(book['Judul']).strip(),
                        'Penulis': str(book['Penulis']).strip(),
                        'Genre': str(book['Genre']).strip()
                    }
                    
                    # Skip jika ada field kosong
                    if not all(normalized_book.values()):
                        print(f"Warning: Book {i+1} has empty fields, skipping...")
                        continue
                    
                    validated_data.append(normalized_book)
                    
                except Exception as e:
                    print(f"Error processing book {i+1}: {e}")
                    continue
            
            if not validated_data:
                raise ValueError("No valid books found in JSON file")
            
            return validated_data
            
        except FileNotFoundError:
            print(f"File {filename} not found")
            return None
        except json.JSONDecodeError as e:
            print(f"Invalid JSON format in {filename}: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error loading {filename}: {e}")
            return None
    
    def build_trees(self, data):
        """Membangun pohon dengan validasi untuk mencegah referensi bersama"""
        self.trees = {}
        self.trees_by_genre = {}  # PERBAIKAN: Mengisi kedua atribut
        self.all_books = data
        
        # Group books by genre
        genre_books = {}
        for book in data:
            genre = book["Genre"]
            if genre not in genre_books:
                genre_books[genre] = []
            genre_books[genre].append(book)
        
        # Build balanced BST for each genre
        for genre, books in genre_books.items():
            print(f"Building BST for genre: {genre} with {len(books)} books")
            # Sort books by title for balanced insertion
            sorted_books = sorted(books, key=lambda x: x["Judul"])
            tree_root = self.build_balanced_bst(sorted_books)
            
            # PERBAIKAN: Mengisi kedua dictionary
            self.trees[genre] = tree_root
            self.trees_by_genre[genre] = tree_root
            
            # Validate the tree after building
            if tree_root:
                is_valid = self.validate_bst_structure(tree_root)
                print(f"BST for {genre} is valid: {is_valid}")

    def build_balanced_bst(self, sorted_books):
        """Membangun BST seimbang dari daftar buku yang sudah diurutkan dengan validasi"""
        if not sorted_books:
            return None
        
        # Find middle element
        mid = len(sorted_books) // 2
        book = sorted_books[mid]
        
        # Create NEW node instance (crucial for preventing shared references)
        root = BSTNode(book["Judul"], book["Penulis"], book["ID"])
        
        # Add debug info
        print(f"Creating node: {book['ID']} - {book['Judul']}")
        
        # Recursively build left and right subtrees
        left_books = sorted_books[:mid]
        right_books = sorted_books[mid + 1:]
        
        if left_books:
            root.left = self.build_balanced_bst(left_books)
            if root.left:
                root.left.parent = root
        
        if right_books:
            root.right = self.build_balanced_bst(right_books)
            if root.right:
                root.right.parent = root
        
        return root
    
    def validate_bst_structure(self, root, visited_nodes=None):
        """Validasi struktur BST untuk memastikan tidak ada node yang memiliki banyak parent"""
        if visited_nodes is None:
            visited_nodes = set()
        
        if root is None:
            return True
        
        # Check if this node was already visited (indicates shared reference)
        node_id = id(root)
        if node_id in visited_nodes:
            print(f"ERROR: Node {root.book_id} ({root.title}) has shared reference!")
            return False
        
        visited_nodes.add(node_id)
        
        # Recursively validate children
        left_valid = self.validate_bst_structure(root.left, visited_nodes)
        right_valid = self.validate_bst_structure(root.right, visited_nodes)
        
        return left_valid and right_valid

    def debug_tree_structure(self, root, level=0, prefix="Root: "):
        """Fungsi debug untuk mencetak struktur pohon"""
        if root is None:
            return
        
        indent = "  " * level
        print(f"{indent}{prefix}{root.id_buku} - {root.title}")
        
        if root.left:
            self.debug_tree_structure(root.left, level + 1, "L--- ")
        if root.right:
            self.debug_tree_structure(root.right, level + 1, "R--- ")

    def check_duplicate_books(self, data):
        """Periksa buku-buku duplikat yang mungkin menyebabkan masalah."""
        seen_ids = {}
        seen_titles = {}
        
        for book in data:
            book_id = book["ID"]
            title = book["Judul"]
            
            if book_id in seen_ids:
                print(f"WARNING: Duplicate ID found: {book_id}")
                print(f"  First: {seen_ids[book_id]}")
                print(f"  Second: {book}")
            else:
                seen_ids[book_id] = book
            
            if title in seen_titles:
                print(f"WARNING: Duplicate title found: {title}")
                print(f"  First: {seen_titles[title]}")
                print(f"  Second: {book}")
            else:
                seen_titles[title] = book

    def setup_ui(self):
        # PERBAIKAN: Menggunakan main_frame sebagai atribut instance
        self.main_frame = tk.Frame(self.root, bg='#8B4513')
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left sidebar
        sidebar = tk.Frame(self.main_frame, bg='#654321', width=250)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        sidebar.pack_propagate(False)
        
        # Profile section
        profile_frame = tk.Frame(sidebar, bg='#654321')
        profile_frame.pack(pady=20)
        
        # Profile circle (simulated)
        profile_canvas = tk.Canvas(profile_frame, width=100, height=100, bg='#654321', highlightthickness=0)
        profile_canvas.pack()
        profile_canvas.create_oval(10, 10, 90, 90, fill='#8B4513', outline='white', width=3)
        profile_canvas.create_text(50, 50, text="👤", font=('Arial', 30), fill='white')
        
        tk.Label(profile_frame, text="My Profile", font=('Arial', 16, 'bold'), 
                fg='white', bg='#654321').pack(pady=10)
        
        # Menu buttons
        menu_frame = tk.Frame(sidebar, bg='#654321')
        menu_frame.pack(fill=tk.X, pady=20)
        
        buttons = [
            ("Dashboard", self.show_dashboard),
            ("Search Books", self.show_search),
            ("Browse by Genre", self.show_genre_browse),
            ("Tree Visualization", self.show_tree_visualization),
            ("Book Return", self.show_book_return),
        ]
        
        for text, command in buttons:
            btn = tk.Button(menu_frame, text=text, font=('Arial', 12), 
                          bg='#D2B48C', fg='#654321', relief=tk.RAISED,
                          command=command, width=20, pady=8)
            btn.pack(pady=5, padx=10, fill=tk.X)
        
        # Right content area
        self.content_frame = tk.Frame(self.main_frame, bg='white')
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header with search bar
        header_frame = tk.Frame(self.content_frame, bg='white', height=100)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        header_frame.pack_propagate(False)
        
        # Library image placeholder
        img_frame = tk.Frame(header_frame, bg='#8B4513', height=80)
        img_frame.pack(fill=tk.X, pady=0)
        tk.Label(img_frame, text="📚 LIBRARY MANAGEMENT SYSTEM 📚", 
                font=('Arial', 20, 'bold'), fg='white', bg='#8B4513').pack(expand=True)
        
        # Search bar
        search_frame = tk.Frame(header_frame, bg='white')
        search_frame.pack(fill=tk.X)
        
        # Main content area
        self.main_content = tk.Frame(self.content_frame, bg='white')
        self.main_content.pack(fill=tk.BOTH, expand=True)
        
        self.show_dashboard()
    
    def clear_content(self):
        if hasattr(self, 'main_content'):
            for widget in self.main_content.winfo_children():
                widget.destroy()

    def show_dashboard(self):
        """Method untuk menampilkan dashboard """
        self.clear_content()
        
        tk.Label(self.main_content, text="Welcome to Library Management System", 
                font=('Arial', 24, 'bold'), bg='white', fg='#654321').pack(pady=50)
        
        stats_frame = tk.Frame(self.main_content, bg='white')
        stats_frame.pack(pady=20)
        
        total_books = len(self.all_books)
        total_genres = len(self.trees)
        
        stats = [
            ("Total Books", total_books),
            ("Genres Available", total_genres),
            ("Library Sections", 5)
        ]
        
        for i, (label, value) in enumerate(stats):
            stat_frame = tk.Frame(stats_frame, bg='#E8E8E8', relief=tk.GROOVE, bd=2)
            stat_frame.grid(row=0, column=i, padx=20, pady=10, ipadx=20, ipady=10)
            
            tk.Label(stat_frame, text=str(value), font=('Arial', 20, 'bold'), 
                    bg='#E8E8E8', fg='#654321').pack()
            tk.Label(stat_frame, text=label, font=('Arial', 12), 
                    bg='#E8E8E8', fg='#654321').pack()
    
    def show_search(self):
        self.clear_content()

        # Frame utama hasil dan pencarian
        tree_frame = tk.Frame(self.main_content, bg='white')
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Search input dan button
        search_input_frame = tk.Frame(tree_frame, bg='white')
        search_input_frame.pack(anchor='w', pady=(0, 10))

        self.search_var_local = tk.StringVar()
        search_entry = tk.Entry(search_input_frame, textvariable=self.search_var_local,
                                font=('Arial', 14), width=50)
        search_entry.pack(side=tk.LEFT, padx=(0, 10), ipady=5)

        search_btn = tk.Button(search_input_frame, text="🔍 Search", font=('Arial', 12),
                            bg='#4CAF50', fg='white', command=self.perform_local_search)
        search_btn.pack(side=tk.LEFT)

        search_entry.bind('<Return>', lambda event: self.perform_local_search())

        # Treeview untuk hasil pencarian
        columns = ('ID', 'Title', 'Author', 'Genre', 'Status')
        self.search_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)

        for col in columns:
            self.search_tree.heading(col, text=col)
            self.search_tree.column(col, width=150)

        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.search_tree.yview)
        self.search_tree.configure(yscrollcommand=scrollbar.set)

        self.search_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Tombol untuk pinjam buku
        borrow_button = tk.Button(self.main_content, text="📚 Pinjam Buku", font=('Arial', 10),
                                bg='#2196F3', fg='white', command=self.pinjam_selected_book)
        borrow_button.pack(pady=10)

        # Tampilkan semua buku saat pertama kali
        self.populate_search_results(self.all_books)

    def perform_local_search(self):
        """Fungsi search khusus untuk halaman search books"""
        query = self.search_var_local.get().strip()
        if not query:
            self.populate_search_results(self.all_books)
            return
        
        # Search in all books
        results = []
        query_lower = normalize(query)
        
        for book in self.all_books:
            if (query_lower in normalize(book['Judul']) or 
                query_lower in normalize(book['Penulis']) or 
                query_lower in normalize(book['Genre'])):
                results.append(book)
        
        self.populate_search_results(results)
        
        if not results:
            messagebox.showinfo("Search Results", f"No books found matching '{query}'")
        
    def populate_search_results(self, books):
        # Clear existing items
        if hasattr(self, 'search_tree'):
            for item in self.search_tree.get_children():
                self.search_tree.delete(item)
            
            # Add books to treeview
            for book in books:
                status = "Dipinjam" if self.is_book_borrowed(book['ID']) else "Tersedia"
                self.search_tree.insert('', 'end', values=(
                    book['ID'], book['Judul'], book['Penulis'], book['Genre'], status))

    def show_genre_browse(self):
        self.clear_content()
        tk.Label(self.main_content, text="Browse Books by Genre", 
                font=('Arial', 18, 'bold'), bg='white', fg='#654321').pack(pady=20)

        # Control panel
        genre_section_frame = tk.Frame(self.main_content, bg='white')
        genre_section_frame.pack(pady=20, fill=tk.X, padx=20)

        # Genre selection
        genre_frame = tk.Frame(genre_section_frame, bg='white')
        genre_frame.pack(anchor='w', pady=(0, 5))
        tk.Label(genre_frame, text="Select Genre:", font=('Arial', 14), 
                bg='white', fg='#654321').pack(side=tk.LEFT, padx=(0, 10))
        self.genre_var = tk.StringVar()
        genre_combo = ttk.Combobox(genre_frame, textvariable=self.genre_var, 
                                values=list(self.trees.keys()), font=('Arial', 12))
        genre_combo.pack(side=tk.LEFT, padx=(0, 10))
        genre_combo.bind('<<ComboboxSelected>>', self.on_genre_selected)

        # Search within genre 
        search_frame = tk.Frame(genre_section_frame, bg='white')
        search_frame.pack(anchor='w')
        tk.Label(search_frame, text="Search in Genre:", font=('Arial', 14), 
                bg='white', fg='#654321').pack(side=tk.LEFT, padx=(0, 10))
        self.genre_search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.genre_search_var, 
                                font=('Arial', 12), width=25)
        search_entry.pack(side=tk.LEFT, padx=(0, 10))
        search_entry.bind('<KeyRelease>', self.on_genre_search)

        # Clear search button
        clear_btn = tk.Button(search_frame, text="Clear", font=('Arial', 10),
                            bg='#FF5722', fg='white', command=self.clear_genre_search)
        clear_btn.pack(side=tk.LEFT, padx=5)

        # Status label
        self.genre_status_label = tk.Label(self.main_content, text="Select a genre to view books", 
                                        font=('Arial', 12), bg='white', fg='#666666')
        self.genre_status_label.pack(pady=(10, 0))

        # Treeview untuk hasil pencarian tanpa kolom 'Status'
        columns = ('ID', 'Title', 'Author')
        self.genre_tree = ttk.Treeview(self.main_content, columns=columns, show='headings', height=15)

        for col in columns:
            self.genre_tree.heading(col, text=col)
            self.genre_tree.column(col, width=150)

        # Scrollbar
        scrollbar2 = ttk.Scrollbar(self.main_content, orient='vertical', command=self.genre_tree.yview)
        self.genre_tree.configure(yscrollcommand=scrollbar2.set)

        # Frame untuk treeview dan scrollbar
        tree_frame2 = tk.Frame(self.main_content, bg='white')
        tree_frame2.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        self.genre_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar2.pack(side=tk.RIGHT, fill=tk.Y)

    def on_genre_selected(self, event=None):
        selected_genre = self.genre_var.get()
        if selected_genre in self.trees:
            self.genre_search_var.set("")
            for item in self.genre_tree.get_children():
                self.genre_tree.delete(item)
            self.populate_genre_books(selected_genre)
        
    def on_genre_search(self, event=None):
        """Handle search dengan menyeleksi genre"""
        selected_genre = self.genre_var.get()
        search_term = self.genre_search_var.get().strip().lower()

        if not selected_genre or selected_genre not in self.trees:
            return

        if search_term:
            # Search within the genre using BST
            results = self.trees[selected_genre].dfs_partial_search(search_term)
            books = []
            for node in results:
                books.append({
                    'id_buku': node.id_buku,
                    'title': node.title,
                    'penulis': node.penulis
                })
            self.populate_genre_tree(books)
            
            # Update status
            if books:
                self.genre_status_label.config(
                    text=f"Found {len(books)} book(s) matching '{self.genre_search_var.get()}' in {selected_genre}",
                    fg='#4CAF50'
                )
            else:
                self.genre_status_label.config(
                    text=f"No books found matching '{self.genre_search_var.get()}' in {selected_genre}",
                    fg='#FF5722'
                )
        else:
            # Show all books in genre if no search term
            self.populate_genre_books(selected_genre)

    def populate_genre_books(self, genre):
        """Isi pohon dengan semua buku dari genre yang dipilih."""
        if genre in self.trees:
            # Get books from BST in sorted order
            books = self.trees[genre].inorder_traversal()
            self.populate_genre_tree(books)
            # Update status
            self.genre_status_label.config(
                text=f"Showing {len(books)} book(s) in {genre} genre",
                fg='#654321')

    def clear_genre_search(self):
        """Bersihkan search field dan tampilkan semua buku dalam genre yang dipilih"""
        self.genre_search_var.set("")
        selected_genre = self.genre_var.get()
        if selected_genre and selected_genre in self.trees:
            self.populate_genre_books(selected_genre)

    def show_tree_visualization(self):
        self.clear_content()
        
        tk.Label(self.main_content, text="BST Tree Visualization", 
                font=('Arial', 18, 'bold'), bg='white', fg='#654321').pack(pady=20)
        
        # Control panel
        control_frame = tk.Frame(self.main_content, bg='white')
        control_frame.pack(pady=10, fill=tk.X, padx=20)
        
        # Genre selection
        genre_frame = tk.Frame(control_frame, bg='white')
        genre_frame.pack(side=tk.LEFT)
        
        tk.Label(genre_frame, text="Genre:", font=('Arial', 12), 
                bg='white', fg='#654321').pack(side=tk.LEFT, padx=(0, 5))
        
        self.viz_genre_var = tk.StringVar()
        viz_combo = ttk.Combobox(genre_frame, textvariable=self.viz_genre_var, 
                                values=list(self.trees.keys()), font=('Arial', 10), width=15)
        viz_combo.pack(side=tk.LEFT, padx=(0, 10))
        viz_combo.bind('<<ComboboxSelected>>', lambda e: self.create_tree_visualization())
        
        # Search frame
        search_frame = tk.Frame(control_frame, bg='white')
        search_frame.pack(side=tk.LEFT, padx=20)
        
        tk.Label(search_frame, text="Search:", font=('Arial', 12), 
                bg='white', fg='#654321').pack(side=tk.LEFT, padx=(0, 5))
        
        self.viz_search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.viz_search_var, 
                               font=('Arial', 10), width=20)
        search_entry.pack(side=tk.LEFT, padx=(0, 5))
        search_entry.bind('<KeyRelease>', lambda e: self.create_tree_visualization())
        
        search_btn = tk.Button(search_frame, text="Clear", font=('Arial', 10),
                             bg='#FF5722', fg='white', command=self.clear_search)
        search_btn.pack(side=tk.LEFT, padx=5)
        
        # Control buttons
        btn_frame = tk.Frame(control_frame, bg='white')
        btn_frame.pack(side=tk.RIGHT)
        
        # Zoom controls
        zoom_frame = tk.Frame(btn_frame, bg='white')
        zoom_frame.pack(side=tk.LEFT, padx=10)
        
        tk.Button(zoom_frame, text="🔍+", font=('Arial', 12), width=3,
                 bg='#4CAF50', fg='white', command=self.zoom_in).pack(side=tk.LEFT, padx=2)
        tk.Button(zoom_frame, text="🔍-", font=('Arial', 12), width=3,
                 bg='#4CAF50', fg='white', command=self.zoom_out).pack(side=tk.LEFT, padx=2)
        tk.Button(zoom_frame, text="↻", font=('Arial', 12), width=3,
                 bg='#4CAF50', fg='white', command=self.reset_view).pack(side=tk.LEFT, padx=2)
        
        # Canvas for tree visualization
        self.viz_canvas_frame = tk.Frame(self.main_content, bg='white', relief=tk.SUNKEN, bd=2)
        self.viz_canvas_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Initialize zoom and pan variables
        self.zoom_factor = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self.drag_data = {"x": 0, "y": 0}
    
    def create_tree_visualization(self):
        selected_genre = self.viz_genre_var.get()
        if not selected_genre or selected_genre not in self.trees:
            # Clear visualization if no genre selected
            for widget in self.viz_canvas_frame.winfo_children():
                widget.destroy()
            return
        
        # Clear previous visualization
        for widget in self.viz_canvas_frame.winfo_children():
            widget.destroy()
        
        # Create custom canvas with scrollbars
        canvas_container = tk.Frame(self.viz_canvas_frame, bg='white')
        canvas_container.pack(fill=tk.BOTH, expand=True)
        
        # Create scrollable canvas
        self.tree_canvas = tk.Canvas(canvas_container, bg='#f8f9fa', 
                                    scrollregion=(-1000, -800, 1000, 800))
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(canvas_container, orient="vertical", command=self.tree_canvas.yview)
        h_scrollbar = ttk.Scrollbar(canvas_container, orient="horizontal", command=self.tree_canvas.xview)
        self.tree_canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack scrollbars and canvas
        self.tree_canvas.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        
        # Bind mouse events for dragging
        self.tree_canvas.bind("<ButtonPress-1>", self.start_drag)
        self.tree_canvas.bind("<B1-Motion>", self.drag_canvas)
        self.tree_canvas.bind("<MouseWheel>", self.mouse_zoom)  # Windows
        self.tree_canvas.bind("<Button-4>", self.mouse_zoom)    # Linux
        self.tree_canvas.bind("<Button-5>", self.mouse_zoom)    # Linux
        
        # Draw the tree
        self.draw_bst_tree(selected_genre)
    
    def calculate_tree_width(self, root, level=0):
        """Kalkulasi total lebar yang dibutuhkan untuk pohon seimbang"""
        if not root:
            return 0
        
        tree_depth = self.get_tree_depth(root)
        
        # For balanced tree, calculate width based on maximum level
        max_nodes_at_bottom = 2 ** (tree_depth - 1)
        min_spacing = 100 * self.zoom_factor
        
        return max_nodes_at_bottom * min_spacing

    def get_tree_depth(self, root):
        """Kalkulasi kedalaman pohon"""
        if not root:
            return 0
        
        left_depth = self.get_tree_depth(root.left)
        right_depth = self.get_tree_depth(root.right)
        
        return max(left_depth, right_depth) + 1
    def reset_view(self):
        """Reset view dengan posisi optimal"""
        self.zoom_factor = 1.0
        self.pan_x = 0
        self.pan_y = 50  # Tambah margin atas
        self.refresh_tree_view()
        
        # Auto-center tree
        if hasattr(self, 'tree_canvas'):
            self.tree_canvas.update_idletasks()
            # Center horizontally, top-align vertically
            self.tree_canvas.xview_moveto(0.1)
            self.tree_canvas.yview_moveto(0.0)

    def calculate_tree_positions_reingold_tilford(self, root):
        """Implementasi Reingold-Tilford Algorithm"""
        if not root:
            return []
        
        # Reset counter untuk menghindari konflik
        self._node_positions = {}
        self._leaf_counter = 0
        
        # Step 1: Calculate initial positions using post-order traversal
        self.assign_initial_x(root)
        
        # Step 2: Calculate final positions dengan tracking yang konsisten
        positions = []
        self.calculate_final_positions(root, 0, 0, positions)
        
        return positions

    def assign_initial_x(self, node, depth=0):
        """Post-order traversal untuk assign posisi X awal """
        if not node:
            return
        
        # Process children first (post-order)
        if node.left:
            self.assign_initial_x(node.left, depth + 1)
        if node.right:
            self.assign_initial_x(node.right, depth + 1)
        
        # Calculate position for current node
        if not node.left and not node.right:
            # Leaf node: posisi berdasarkan urutan dalam level
            node.initial_x = self._leaf_counter
            self._leaf_counter += 1
        elif not node.right:
            # Hanya left child
            node.initial_x = node.left.initial_x
        elif not node.left:
            # Hanya right child
            node.initial_x = node.right.initial_x
        else:
            # Both children: posisi di tengah
            node.initial_x = (node.left.initial_x + node.right.initial_x) / 2
        
        # PENTING: Simpan referensi posisi untuk tracking
        self._node_positions[id(node)] = node.initial_x

    def calculate_final_positions(self, node, x_offset, depth, positions, parent_pos=None):
        """Kalkulasi final positions dengan konsistensi koordinat"""
        if not node:
            return
        
        # Spacing configuration yang konsisten
        horizontal_spacing = 120 * self.zoom_factor
        vertical_spacing = 100 * self.zoom_factor
        
        # Calculate final position dengan offset yang tepat
        final_x = (node.initial_x * horizontal_spacing) + x_offset + self.pan_x
        final_y = (depth * vertical_spacing) + self.pan_y
        
        # Store position dengan referensi node yang jelas
        positions.append({
            'node': node,
            'node_id': id(node),  # Tambahkan unique identifier
            'pos': (final_x, final_y),
            'parent_pos': parent_pos,
            'level': depth
        })
        
        # Process children dengan parent position yang akurat
        current_pos = (final_x, final_y)
        if node.left:
            self.calculate_final_positions(node.left, x_offset, depth + 1, positions, current_pos)
        if node.right:
            self.calculate_final_positions(node.right, x_offset, depth + 1, positions, current_pos)

    def draw_bst_tree(self, genre):
        """Draw BST tree dengan sinkronisasi node-arrow yang tepat"""
        if not hasattr(self, 'tree_canvas'):
            return

        root = self.trees[genre]
        search_term = self.viz_search_var.get().lower().strip()
        
        # PENTING: Reset semua counter dan data tracking
        self._leaf_counter = 0
        self._node_positions = {}
        
        # Clear canvas
        self.tree_canvas.delete("all")
        
        # Calculate positions dengan algoritma yang sudah diperbaiki
        tree_structure = self.calculate_tree_positions_reingold_tilford(root)
        
        if not tree_structure:
            return
        
        # Update scroll region berdasarkan posisi aktual
        positions = [pos['pos'] for pos in tree_structure]
        min_x = min(pos[0] for pos in positions) - 100
        max_x = max(pos[0] for pos in positions) + 300
        min_y = min(pos[1] for pos in positions) - 50
        max_y = max(pos[1] for pos in positions) + 100
        
        self.tree_canvas.configure(scrollregion=(min_x, min_y, max_x, max_y))
        
        # KUNCI PERBAIKAN: Draw connections dan nodes dalam urutan yang tepat
        # 1. Gambar semua connections terlebih dahulu
        for node_data in tree_structure:
            if node_data['parent_pos']:
                self.draw_connection_fixed(node_data['parent_pos'], node_data['pos'])
        
        # 2. Gambar semua nodes di atas connections
        for node_data in tree_structure:
            is_highlighted = (search_term and 
                            search_term in normalize(node_data['node'].title))
            self.draw_tree_node_fixed(node_data['pos'], node_data['node'], is_highlighted)
        
        # Add legend
        self.draw_balanced_tree_legend(root)


    def draw_balanced_tree_legend(self, root):
        """Draw legend untuk balanced BST dengan info algoritma"""
        tree_depth = self.get_tree_depth(root)
        total_nodes = len(list(self.inorder_traversal_for_count(root)))
        
        legend_x = 20
        legend_y = 20
        
        # Legend background
        self.tree_canvas.create_rectangle(
            legend_x - 10, legend_y - 10,
            legend_x + 280, legend_y + 120,
            fill='#F8F9FA', outline='#1976D2', width=2, tags="legend")
        
        # Legend title
        self.tree_canvas.create_text(
            legend_x + 135, legend_y + 15,
            text="Binary Search Tree",
            font=('Arial', 12, 'bold'),
            fill='#1976D2', tags="legend")
        
        # Legend items dengan informasi algoritma
        legend_items = [
            f"📊 Total Nodes: {total_nodes}",
            f"📏 Tree Depth: {tree_depth} levels", 
            f"⚖️ Layout: Reingold-Tilford Algorithm",
            f"← Left: Alphabetically smaller titles",
            f"→ Right: Alphabetically larger titles",
            f"🔍 Search highlights matching nodes"
        ]
        
        for i, item in enumerate(legend_items):
            self.tree_canvas.create_text(
                legend_x + 15, legend_y + 40 + (i * 12),
                text=item,
                font=('Arial', 9),
                fill='#424242',
                anchor='w',
                tags="legend")

    def inorder_traversal_for_count(self, node):
        """Helper untuk menghitung total nodes"""
        if node:
            yield from self.inorder_traversal_for_count(node.left)
            yield node
            yield from self.inorder_traversal_for_count(node.right)

        
    def draw_connection_fixed(self, parent_pos, child_pos):
        """Draw connection dengan koordinat yang akurat """
        px, py = parent_pos
        cx, cy = child_pos
        
        # Gunakan koordinat langsung tanpa offset tambahan yang menyebabkan misalignment
        canvas_px = px
        canvas_py = py
        canvas_cx = cx
        canvas_cy = cy
        
        # Draw straight line dulu untuk debugging
        self.tree_canvas.create_line(
            canvas_px, canvas_py, canvas_cx, canvas_cy,
            fill='#666666', width=2, tags="connection"
        )
        
        # Optional: Add arrow indicator tanpa mengubah posisi dasar
        if abs(canvas_cx - canvas_px) > 5:  # Hindari arrow pada node yang terlalu dekat
            # Calculate arrow direction
            angle = np.arctan2(canvas_cy - canvas_py, canvas_cx - canvas_px)
            arrow_length = 15
            arrow_x = canvas_cx - arrow_length * np.cos(angle)
            arrow_y = canvas_cy - arrow_length * np.sin(angle)
            
            # Small arrowhead
            self.tree_canvas.create_line(
                arrow_x, arrow_y, canvas_cx, canvas_cy,
                fill='#444444', width=3, tags="arrow"
            )

    def draw_tree_node_fixed(self, pos, node, is_highlighted=False):
        """Draw tree node dengan positioning yang konsisten"""
        x, y = pos
        
        # Node styling
        base_radius = 35
        node_radius = max(20, min(50, base_radius * self.zoom_factor))
        
        # Colors
        if is_highlighted:
            fill_color = '#FFD54F'
            outline_color = '#F57F17'
            text_color = '#1B5E20'
            outline_width = 3
        else:
            fill_color = '#E3F2FD'
            outline_color = '#1976D2'
            text_color = '#0D47A1'
            outline_width = 2
        
        # Shadow (optional, untuk estetika)
        shadow_offset = 3
        self.tree_canvas.create_oval(
            x - node_radius + shadow_offset, y - node_radius + shadow_offset,
            x + node_radius + shadow_offset, y + node_radius + shadow_offset,
            fill='#E0E0E0', outline='', tags="shadow"
        )
        
        # Main circle - posisi harus sama dengan yang digunakan untuk connection
        self.tree_canvas.create_oval(
            x - node_radius, y - node_radius,
            x + node_radius, y + node_radius,
            fill=fill_color, outline=outline_color, width=outline_width, tags="node"
        )
        
        # Text
        display_text = node.title
        max_chars = max(6, int(12 * self.zoom_factor))
        if len(display_text) > max_chars:
            display_text = display_text[:max_chars-3] + "..."
        
        font_size = max(8, min(12, int(9 * self.zoom_factor)))
        
        # Node title
        self.tree_canvas.create_text(
            x, y - 2,
            text=display_text,
            font=('Arial', font_size, 'bold'),
            fill=text_color,
            width=node_radius * 1.6,
            tags="text"
        )
        
        # ID display
        self.tree_canvas.create_text(
            x, y + node_radius + 12,
            text=f"#{node.id_buku}",
            font=('Arial', max(6, font_size - 2)),
            fill='#666666',
            tags="info"
        )
    def start_drag(self, event):
        """Mulai operasi dragging"""
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y
    
    def drag_canvas(self, event):
        """Handle canvas dragging"""
        dx = event.x - self.drag_data["x"]
        dy = event.y - self.drag_data["y"]
        
        self.pan_x += dx
        self.pan_y += dy
        
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y
        
        # Redraw tree with new pan position
        self.refresh_tree_view()
    
    def mouse_zoom(self, event):
        """Handle mouse wheel zoom"""
        if event.delta > 0 or event.num == 4:  # Zoom in
            self.zoom_factor = min(2.0, self.zoom_factor * 1.1)
        elif event.delta < 0 or event.num == 5:  # Zoom out
            self.zoom_factor = max(0.3, self.zoom_factor * 0.9)
        
        self.refresh_tree_view()
    
    def zoom_in(self):
        """Zoom in tombol handler"""
        self.zoom_factor = min(2.0, self.zoom_factor * 1.2)
        self.refresh_tree_view()
    
    def zoom_out(self):
        """Zoom out tombol handler"""
        self.zoom_factor = max(0.3, self.zoom_factor * 0.8)
        self.refresh_tree_view()
    
    def refresh_tree_view(self):
        """Refresh tree view dengan pembersihan yang lebih teliti """
        if hasattr(self, 'tree_canvas'):
            # Clear canvas completely
            self.tree_canvas.delete("all")
            
            # Reset semua tracking variables
            if hasattr(self, '_leaf_counter'):
                self._leaf_counter = 0
            if hasattr(self, '_node_positions'):
                self._node_positions.clear()
            
            # Redraw dengan data yang bersih
            selected_genre = self.viz_genre_var.get()
            if selected_genre and selected_genre in self.trees:
                self.draw_bst_tree(selected_genre)

    def clear_search(self):
        """Hapus kata kunci pencarian dan refresh view"""
        self.viz_search_var.set("")
        self.refresh_tree_view()
    
    def load_json_file(self):
        """Load JSON file melalui file dialog"""
        file_path = filedialog.askopenfilename(
            title="Select JSON File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                data = self.load_from_json(file_path)
                if data:
                    self.build_trees(data)
                    messagebox.showinfo("Success", 
                                      f"Successfully loaded {len(data)} books from {file_path.split('/')[-1]}")
                    # Refresh current view
                    self.show_dashboard()
                else:
                    messagebox.showerror("Error", 
                                       "Failed to load JSON file. Please check the file format.")
            except Exception as e:
                messagebox.showerror("Error", f"Error loading file: {str(e)}")
    
    def export_data(self):
        """Export data terbaru ke JSON file"""
        if not self.all_books:
            messagebox.showwarning("Warning", "No data to export")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Save JSON File",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.all_books, f, indent=2, ensure_ascii=False)
                messagebox.showinfo("Success", f"Data exported to {file_path.split('/')[-1]}")
            except Exception as e:
                messagebox.showerror("Error", f"Error exporting file: {str(e)}")
    
    def find_by_id(self, node, target_id):
        if node is None:
            return None
        if node.id_buku == target_id:
            return node
        left = self.find_by_id(node.left, target_id)
        if left:
            return left
        return self.find_by_id(node.right, target_id)

    def borrow_book(self, book_id, return_date, borrow_date):
        for genre, tree in self.trees_by_genre.items():
            node = self.find_by_id(tree, book_id)
            if node and not hasattr(node, 'borrowed_until'):
                node.borrowed_until = return_date
                node.borrow_date = borrow_date
                return True
        return False

    def show_book_return(self):
        self.clear_content()

        content_frame = tk.Frame(self.main_content, bg='white')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20)

        tk.Label(content_frame, text="Daftar Peminjaman Buku",
                font=('Arial', 14, 'bold'), bg='white', fg='#654321').pack(pady=(0, 10), anchor='w')

        table_frame = tk.Frame(content_frame, bg='white')
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("ID", "Judul", "Genre", "Tanggal Pinjam", "Tanggal Kembali", "Status")
        self.return_table = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)

        column_widths = {"ID": 60,"Judul": 180, "Genre": 100, "Tanggal Pinjam": 100,"Tanggal Kembali": 100, 
                         "Status": 100}

        for col in columns:
            self.return_table.heading(col, text=col)
            self.return_table.column(col, width=column_widths[col], minwidth=column_widths[col])

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.return_table.yview)
        self.return_table.configure(yscrollcommand=scrollbar.set)

        self.return_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        info_label = tk.Label(content_frame, text="Double-click pada baris untuk mengembalikan buku",
                            font=('Arial', 10), bg='white', fg='#666666')
        info_label.pack(pady=(10, 0), anchor='w')

        def update_return_table():
            self.return_table.delete(*self.return_table.get_children())
            borrowed_count = 0
            for genre, tree in self.trees_by_genre.items():
                borrowed_count += self.collect_returns(tree, self.return_table, genre)

            if borrowed_count == 0:
                info_label.config(text="Tidak ada buku yang sedang dipinjam.")

        def return_selected_book():
            selected = self.return_table.focus()
            if not selected:
                messagebox.showwarning("Peringatan", "Pilih buku yang akan dikembalikan terlebih dahulu.")
                return

            values = self.return_table.item(selected, "values")
            if not values:
                return

            id_buku = values[0]
            judul_buku = values[1]

            for genre, tree in self.trees_by_genre.items():
                node = self.find_by_id(tree, id_buku)
                if node and hasattr(node, 'borrowed_until'):
                    node.borrowed_until = None
                    node.borrow_date = None

                    self.simpan_log_pengembalian(id_buku, node.title
                                                if hasattr(self, 'username') else 'User',
                                                datetime.now().strftime('%d-%m-%Y'))
                    messagebox.showinfo("Berhasil", f"Buku '{judul_buku}' berhasil dikembalikan!")
                    update_return_table()
                    return

            messagebox.showerror("Error", "Buku tidak ditemukan atau sudah dikembalikan.")

        self.return_table.bind("<Double-1>", lambda e: return_selected_book())

        button_frame = tk.Frame(content_frame, bg='white')
        button_frame.pack(fill=tk.X, pady=20)

        tk.Button(button_frame, text="🔄 Refresh", font=('Arial', 10),
                bg='#4CAF50', fg='white', command=update_return_table,
                padx=20, pady=5).pack(side=tk.LEFT, padx=(0, 10))

        tk.Button(button_frame, text="📤 Kembalikan Buku", font=('Arial', 10),
                bg='#2196F3', fg='white', command=return_selected_book,
                padx=20, pady=5).pack(side=tk.LEFT, padx=(0, 10))

        tk.Button(button_frame, text="🔙 Kembali ke Dashboard", font=('Arial', 10),
                bg='#FF5722', fg='white', command=self.show_dashboard,
                padx=20, pady=5).pack(side=tk.RIGHT)

        update_return_table()

    def collect_returns(self, node, tree, genre):
        if not node:
            return 0
        count = 0

        if hasattr(node, 'borrowed_until') and node.borrowed_until:
            status = "Dipinjam" if node.borrowed_until >= datetime.now().date() else "Terlambat"
            borrow_date = getattr(node, 'borrow_date', '-')
            return_date = node.borrowed_until

            if isinstance(borrow_date, datetime):
                borrow_date = borrow_date.strftime("%Y-%m-%d")
            if isinstance(return_date, datetime):
                return_date = return_date.strftime("%Y-%m-%d")

            tree.insert("", "end", values=(
                node.id_buku,
                node.title,
                genre,
                borrow_date,
                return_date,
                status
            ))
            count += 1

        count += self.collect_returns(node.left, tree, genre)
        count += self.collect_returns(node.right, tree, genre)
        return count

    def is_book_borrowed(self, book_id):
        for tree in self.trees_by_genre.values():
            node = self.find_by_id(tree, book_id)
            if node and hasattr(node, 'borrowed_until') and node.borrowed_until:
                return True
        return False

    def simpan_log_pengembalian(self,id_buku, judul, username, tanggal):
        """Simpan log pengembalian ke file"""
        try:
            log_entry = {
                'id_buku': id_buku,
                'judul': judul,
                'username': username,
                'tanggal_kembali': tanggal,
                'timestamp': datetime.now().isoformat()
            }
            
            # Save to JSON log file
            log_file = 'return_log.json'
            logs = []
            
            if os.path.exists(log_file):
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        logs = json.load(f)
                except:
                    logs = []
            
            logs.append(log_entry)
            
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, indent=2, ensure_ascii=False)
                
            print(f"Return logged: {judul} returned by {username}")
            
        except Exception as e:
            print(f"Error saving return log: {e}")

    def pinjam_selected_book(self):
        selected = self.search_tree.focus()
        if not selected:
            messagebox.showwarning("Pilih Buku", "Silakan pilih buku terlebih dahulu.")
            return

        values = self.search_tree.item(selected, 'values')
        if not values:
            return

        book_id = values[0]
        title = values[1]

        # Cek apakah sudah dipinjam
        if self.is_book_borrowed(book_id):
            messagebox.showwarning("Buku Tidak Tersedia", "Buku ini sedang dipinjam.")
            return

        # Window input tanggal pinjam dan kembali
        borrow_window = tk.Toplevel(self.root)
        borrow_window.title("Peminjaman Buku")
        borrow_window.geometry("350x200")
        borrow_window.update_idletasks()

        # Mencari ukuran root utama
        root_x = self.root.winfo_rootx()
        root_y = self.root.winfo_rooty()
        root_width = self.root.winfo_width()
        root_height = self.root.winfo_height()

        # Mencari ukuran borrow_window
        window_width = borrow_window.winfo_width()
        window_height = borrow_window.winfo_height()

        # Cari posisi agar ditengah root
        x = root_x + (root_width // 2) - (window_width // 2)
        y = root_y + (root_height // 2) - (window_height // 2)

        borrow_window.geometry(f"+{x}+{y}")
        borrow_window.grab_set()

        judul_label = tk.Label(
            borrow_window,
            text=f"Judul Buku: {title}",
            font=("Arial", 10, "bold"),
            wraplength=300,           # Maksimum lebar sebelum dipotong
            justify='left',           # Rata kiri
            anchor='w',               # Posisi kiri
            bg='SystemButtonFace'     # Sesuaikan dengan background
        )
        judul_label.pack(pady=(10, 5), anchor='w', padx=10)

        tk.Label(borrow_window, text="Tanggal Pinjam:").pack()
        borrow_date_entry = DateEntry(borrow_window, width=20)
        borrow_date_entry.pack(pady=5)

        tk.Label(borrow_window, text="Tanggal Kembali:").pack()
        return_date_entry = DateEntry(borrow_window, width=20)
        return_date_entry.pack(pady=5)

        def confirm_borrow():
            borrow_date = borrow_date_entry.get_date()
            return_date = return_date_entry.get_date()

            if borrow_date < datetime.now().date():
                messagebox.showwarning("Tanggal tidak valid", "Tanggal peminjaman tidak boleh sebelum hari ini.")
                return
            if return_date <= borrow_date:
                messagebox.showwarning("Tanggal tidak valid", "Tanggal kembali harus setelah tanggal pinjam.")
                return

            success = self.borrow_book(book_id, return_date, borrow_date)
            if success:
                borrow_window.grab_release() 
                borrow_window.destroy()
                messagebox.showinfo("Berhasil", f"Buku '{title}' berhasil dipinjam.")
                self.perform_local_search()
            else:
                messagebox.showerror("Gagal", "Gagal meminjam buku.")

        tk.Button(borrow_window, text="Pinjam",bg="#4CAF50", fg="white",
                font=("Arial", 10), command=confirm_borrow).pack(pady=7)

    def populate_genre_tree(self, books):
        """Isi pohon genre dengan buku-buku yang diberikan + tombol pinjam"""
        # Clear existing items
        for item in self.genre_tree.get_children():
            self.genre_tree.delete(item)
            
        for book in books: 
            self.genre_tree.insert('', 'end', values=(
                book['id_buku'], 
                book['title'], 
                book['penulis']))

    def get_current_books(self):
        """Mengembalikan semua buku dari genre aktif atau seluruh buku"""
        selected_genre = self.genre_var.get()
        if selected_genre and selected_genre in self.trees_by_genre:
            # Ambil semua buku dari genre yang dipilih
            root = self.trees_by_genre[selected_genre]
            return root.inorder_traversal()  # Pastikan inorder_traversal() ada dan bekerja
        else:
            # Jika tidak ada genre dipilih, kembalikan semua buku
            all_books = []
            for genre, tree in self.trees_by_genre.items():
                all_books.extend(tree.inorder_traversal())
            return all_books


# ================== MAIN ==================
def main():
    root = tk.Tk()
    app = LoginApp(root)
    root.mainloop()
if __name__ == "__main__":
    main()
