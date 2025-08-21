import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import os
import math
from utils.file_io import load_books, save_books
from utils.pdf_generator import generate_pdf


def format_code(code):
    """Normalize a code string and pad with leading zeros to at least 4 chars."""
    if code is None:
        return ''
    s = str(code).strip()
    # remove trailing .0 if present from numeric-like exports
    if s.endswith('.0'):
        try:
            iv = int(float(s))
            if str(float(iv)) == s:
                s = str(iv)
        except Exception:
            pass
    # ensure at least 4 characters with leading zeros
    if len(s) < 4:
        s = s.zfill(4)
    return s


class BookGalleryScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg='#0f1419')
        self.controller = controller
        
        self.books_df = load_books()
        # Ensure Codes are normalized/padded and persist a one-time migration if values changed
        if 'Code' in self.books_df.columns:
            try:
                # Build a consistently-typed formatted series
                formatted = self.books_df['Code'].astype(str).apply(format_code)
            except Exception:
                # best-effort fallback
                formatted = self.books_df['Code'].apply(lambda v: format_code(str(v)) if pd.notnull(v) else '')

            # Compare against current stored string values; persist only if different
            try:
                current_as_str = self.books_df['Code'].astype(str)
            except Exception:
                current_as_str = self.books_df['Code'].apply(lambda v: '' if pd.isna(v) else str(v))

            if not formatted.equals(current_as_str):
                self.books_df['Code'] = formatted
                try:
                    save_books(self.books_df)
                except Exception as e:
                    # don't block UI; log migration save failure
                    print(f"Warning: failed to save normalized codes: {e}")
        self.selected_book = None
        self.page_index = 0
        self.codes_per_page = 27

        self.create_background()
        self.create_content()

    def get_unique_books(self):
        return self.books_df["Book"].dropna().unique()

    def create_background(self):
        """Create animated gradient background"""
        self.bg_canvas = tk.Canvas(self, highlightthickness=0)
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        
    def refresh_book_list(self):
        self.book_listbox.delete(0, tk.END)
        books = self.get_unique_books()
        for book in books:
            self.book_listbox.insert(tk.END, book)
        self.books_count_label.config(text=f"({len(books)} books)")
    
    def create_content(self):
        """Create main content with glass morphism effect"""
        self.content_frame = tk.Frame(self, bg='#1e293b', relief='ridge', bd=1)
        self.content_frame.place(relx=0.5, rely=0.5, anchor='center', 
                                relwidth=0.9, relheight=0.9)
        
        border_frame = tk.Frame(self.content_frame, bg='#334155', height=2)
        border_frame.pack(fill='x')
        
        close_btn = tk.Button(
            self.content_frame,
            text='✕',
            command=lambda: self.controller.show_frame("ModernMainMenu"),
            font=('Arial', 16, 'bold'),
            bg='#ef4444',
            fg='#ffffff',
            relief='flat',
            cursor='hand2',
            width=3,
            height=1
        )
        close_btn.place(relx=0.98, rely=0.02, anchor='ne')
        
        close_btn.bind('<Enter>', lambda e: close_btn.config(bg='#dc2626'))
        close_btn.bind('<Leave>', lambda e: close_btn.config(bg='#ef4444'))
        
        self.create_header()
        self.create_main_content()
        self.create_footer()
        
        self.refresh_book_list()
    
    def create_header(self):
        """Create animated header section"""
        header_frame = tk.Frame(self.content_frame, bg='#1e293b')
        header_frame.pack(pady=(20, 15))
        
        title_label = tk.Label(header_frame,
                              text="Book Gallery",
                              font=('Segoe UI', 24, 'bold'),
                              fg='#ffffff',
                              bg='#1e293b')
        title_label.pack()
        
        subtitle_label = tk.Label(header_frame,
                                 text="Browse and manage your book collections",
                                 font=('Segoe UI', 11),
                                 fg='#94a3b8',
                                 bg='#1e293b')
        subtitle_label.pack(pady=(5, 0))
        
        accent_canvas = tk.Canvas(header_frame, width=150, height=3,
                                 bg='#1e293b', highlightthickness=0)
        accent_canvas.pack(pady=8)
        self.accent_canvas = accent_canvas
    
    def create_main_content(self):
        """Create main content area with books list and codes display"""
        main_container = tk.Frame(self.content_frame, bg='#1e293b')
        main_container.pack(expand=True, fill='both', padx=20, pady=5)
        
        main_container.grid_rowconfigure(0, weight=1)
        main_container.grid_columnconfigure(0, weight=0)
        main_container.grid_columnconfigure(1, weight=1)
        
        self.create_books_panel(main_container)
        self.create_codes_panel(main_container)
    
    def create_books_panel(self, parent):
        """Create modern books list panel"""
        books_card = tk.Frame(parent, bg='#2d3748', relief='ridge', bd=1, width=350)
        books_card.grid(row=0, column=0, sticky='ns', padx=(0, 10))
        books_card.grid_propagate(False)
        
        header_frame = tk.Frame(books_card, bg='#2d3748')
        header_frame.pack(fill='x', padx=15, pady=(10, 5))
        
        books_label = tk.Label(header_frame,
                              text="📚 Your Books",
                              font=('Segoe UI', 14, 'bold'),
                              fg='#ffffff',
                              bg='#2d3748')
        books_label.pack(side='left')
        
        self.books_count_label = tk.Label(header_frame,
                                         text=f"({len(self.get_unique_books())} books)",
                                         font=('Segoe UI', 10),
                                         fg='#64748b',
                                         bg='#2d3748')
        self.books_count_label.pack(side='left', padx=(10, 0))
        
        listbox_frame = tk.Frame(books_card, bg='#1e293b', relief='groove', bd=1)
        listbox_frame.pack(fill='both', expand=True, padx=15, pady=(0, 10))
        
        scrollbar = ttk.Scrollbar(listbox_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.book_listbox = tk.Listbox(
            listbox_frame,
            width=30,
            yscrollcommand=scrollbar.set,
            font=('Segoe UI', 10),
            bg='#1e293b',
            fg='#ffffff',
            selectbackground='#3b82f6',
            selectforeground='#ffffff',
            relief='flat',
            highlightthickness=0,
            activestyle='none'
        )
        self.book_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.book_listbox.yview)
        self.book_listbox.bind("<<ListboxSelect>>", self.on_book_select)
        
        self.create_action_buttons(books_card)
    
    def create_action_buttons(self, parent):
        """Create modern action buttons"""
        buttons_frame = tk.Frame(parent, bg='#2d3748')
        buttons_frame.pack(fill='x', padx=15, pady=(5, 15))
        
        button_configs = [
            {'text': '➕ New Book', 'command': self.create_book, 'color': '#10b981'},
            {'text': '✏️ Edit Book', 'command': self.edit_book, 'color': '#3b82f6'},
            {'text': '🗑️Delete Book', 'command': self.delete_book, 'color': '#ef4444'},
            {'text': '🖨️ Print Book', 'command': self.print_book, 'color': '#8b5cf6'},
        ]
        
        for config in button_configs:
            btn_frame = tk.Frame(buttons_frame, bg=config['color'], relief='flat')
            btn_frame.pack(fill='x', pady=3)
            
            btn = tk.Button(
                btn_frame,
                text=config['text'],
                command=config['command'],
                font=('Segoe UI', 10),
                bg=config['color'],
                fg='#ffffff',
                relief='flat',
                cursor='hand2',
                pady=6
            )
            btn.pack(fill='both', expand=True)
            
            def on_enter(event, button=btn, color=config['color']):
                r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
                darker = f"#{max(0, r-20):02x}{max(0, g-20):02x}{max(0, b-20):02x}"
                button.config(bg=darker)
            
            def on_leave(event, button=btn, color=config['color']):
                button.config(bg=color)
            
            btn.bind('<Enter>', on_enter)
            btn.bind('<Leave>', on_leave)

    def update_nav_buttons(self):
        if not self.selected_book:
            self.prev_btn.config(state="disabled")
            self.next_btn.config(state="disabled")
            self.page_label.config(text="Page 0 of 0")
            return

        codes = self.books_df[self.books_df["Book"] == self.selected_book]
        total_pages = max(1, (len(codes) + self.codes_per_page - 1) // self.codes_per_page)

        self.prev_btn.config(state="normal" if self.page_index > 0 else "disabled")
        self.next_btn.config(state="normal" if self.page_index < total_pages - 1 else "disabled")
        self.page_label.config(text=f"Page {self.page_index + 1} of {total_pages}")

    def create_codes_panel(self, parent):
        """Create modern codes display panel"""
        self.codes_card = tk.Frame(parent, bg='#2d3748', relief='ridge', bd=1)
        self.codes_card.grid(row=0, column=1, sticky='nsew')
        
        header_frame = tk.Frame(self.codes_card, bg='#2d3748')
        header_frame.pack(fill='x', padx=15, pady=(10, 5))
        
        title_frame = tk.Frame(header_frame, bg='#2d3748')
        title_frame.pack(side='left', fill='x', expand=True)
        
        self.codes_title_label = tk.Label(
            title_frame,
            text="🔤 Select a book to view codes",
            font=('Segoe UI', 12, 'bold'),
            fg='#ffffff',
            bg='#2d3748'
        )
        self.codes_title_label.pack(side='left')
        
        nav_frame = tk.Frame(header_frame, bg='#2d3748')
        nav_frame.pack(side='right')
        
        self.prev_btn = tk.Button(
            nav_frame,
            text='◄',
            command=self.prev_page,
            font=('Segoe UI', 10, 'bold'),
            bg='#3b82f6',
            fg='#ffffff',
            relief='flat',
            cursor='hand2',
            width=3,
            padx=5,
            pady=4
        )
        self.prev_btn.pack(side='left', padx=2)
        
        self.page_label = tk.Label(
            nav_frame,
            text="Page 1 of 1",
            font=('Segoe UI', 10),
            fg='#94a3b8',
            bg='#2d3748',
            width=12
        )
        self.page_label.pack(side='left', padx=5)
        
        self.next_btn = tk.Button(
            nav_frame,
            text='►',
            command=self.next_page,
            font=('Segoe UI', 10, 'bold'),
            bg='#3b82f6',
            fg='#ffffff',
            relief='flat',
            cursor='hand2',
            width=3,
            padx=5,
            pady=4
        )
        self.next_btn.pack(side='left', padx=2)
        
        for btn in [self.prev_btn, self.next_btn]:
            btn.bind('<Enter>', lambda e, b=btn: b.config(bg='#2563eb'))
            btn.bind('<Leave>', lambda e, b=btn: b.config(bg='#3b82f6'))
        
        codes_container = tk.Frame(self.codes_card, bg='#2d3748')
        codes_container.pack(fill='both', expand=True, padx=15, pady=(0, 10))
        
        self.codes_canvas = tk.Canvas(codes_container, bg='#2d3748', highlightthickness=0)
        v_scrollbar = ttk.Scrollbar(codes_container, orient='vertical', command=self.codes_canvas.yview)
        self.codes_canvas.configure(yscrollcommand=v_scrollbar.set)
        
        v_scrollbar.pack(side='right', fill='y')
        self.codes_canvas.pack(side='left', fill='both', expand=True)
        
        self.code_grid_frame = tk.Frame(self.codes_canvas, bg='#2d3748')
        self.canvas_window = self.codes_canvas.create_window(0, 0, anchor='nw', window=self.code_grid_frame)
        
        self.codes_canvas.bind('<Configure>', self.on_codes_canvas_configure)
        self.code_grid_frame.bind('<Configure>', self.on_grid_frame_configure)
        
        self.update_nav_buttons()
    
    def on_codes_canvas_configure(self, event):
        """Handle canvas resize"""
        canvas_width = event.width
        self.codes_canvas.itemconfig(self.canvas_window, width=canvas_width)
    
    def on_grid_frame_configure(self, event):
        """Update scroll region when grid frame changes"""
        self.codes_canvas.configure(scrollregion=self.codes_canvas.bbox("all"))
    
    def create_footer(self):
        """Create footer with back button"""
        footer_frame = tk.Frame(self.content_frame, bg='#1e293b')
        footer_frame.pack(side='bottom', fill='x', pady=(10, 20))
        
        separator = tk.Frame(footer_frame, bg='#334155', height=1)
        separator.pack(fill='x', pady=(0, 10))
        
        button_container = tk.Frame(footer_frame, bg='#1e293b')
        button_container.pack()
        
        back_btn = tk.Button(
            button_container,
            text='🏠 Back to Main Menu',
            command=lambda: self.controller.show_frame("ModernMainMenu"),
            font=('Segoe UI', 14, 'bold'),
            bg='#3b82f6',
            fg='#ffffff',
            relief='flat',
            cursor='hand2',
            padx=30,
            pady=10,
            bd=2
        )
        back_btn.pack()
        
        def on_enter(e):
            back_btn.config(bg='#2563eb')
        
        def on_leave(e):
            back_btn.config(bg='#3b82f6')
        
        back_btn.bind('<Enter>', on_enter)
        back_btn.bind('<Leave>', on_leave)
    
    def prev_page(self):
        if self.page_index > 0:
            self.page_index -= 1
            self.update_code_grid()

    def next_page(self):
        if not self.selected_book:
            return

        codes = self.books_df[self.books_df["Book"] == self.selected_book]
        total_pages = max(1, (len(codes) + self.codes_per_page - 1) // self.codes_per_page)

        if self.page_index < total_pages - 1:
            self.page_index += 1
            self.update_code_grid()
    
    def create_barcode_image(self, code_value, width=200, height=60):
        """Create a barcode image for UI display"""
        try:
            import barcode
            from barcode.writer import ImageWriter
            from PIL import Image, ImageTk
            import tempfile
            import os
            
            # Generate barcode (use Code 128)
            code128 = barcode.get('code128', code_value, writer=ImageWriter())
            
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            barcode_path = temp_file.name.replace('.png', '')
            temp_file.close()
            
            # Save barcode without human-readable text embedded (UI will show the code above)
            writer_options = {
                'module_width': 0.2,
                'module_height': 8.0,
                'font_size': 10,
                'write_text': False,
                'quiet_zone': 1.0,
                'background': 'white',
                'foreground': 'black',
                'dpi': 150,
            }
            filename = code128.save(barcode_path, options=writer_options)
            
            # Load and resize image
            with Image.open(filename) as img:
                # Resize to fit UI
                img = img.resize((width, height), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
            
            # Clean up temp file
            os.unlink(filename)
            
            return photo
            
        except ImportError:
            # Fallback to text if libraries not available
            return None
        except Exception as e:
            print(f"Error creating barcode image: {e}")
            return None
    
    def generate_mini_code128_display(self, code_value):
        """Generate a compact text representation for Code 128 display"""
        # Code 128 is not delimited by '*' characters; show the plain code
        return str(code_value)
    
    def update_code_grid(self):
        """Update the code grid with modern card style and Code 39 barcodes - FIXED VERSION"""
        
        for widget in self.code_grid_frame.winfo_children():
            widget.destroy()

        if not self.selected_book:
            empty_label = tk.Label(
                self.code_grid_frame,
                text="Select a book from the list to view its codes",
                font=('Segoe UI', 12),
                fg='#64748b',
                bg='#2d3748'
            )
            empty_label.pack(pady=50)
            return

        codes = self.books_df[self.books_df["Book"] == self.selected_book]
        codes = codes.sort_values("Code", key=lambda col: col.astype(str)).reset_index(drop=True)
        
        start = self.page_index * self.codes_per_page
        end = start + self.codes_per_page
        page_codes = codes[start:end]

        cols = 3
        rows = 9
        
        for i in range(rows):
            self.code_grid_frame.grid_rowconfigure(i, weight=1, minsize=60)
        for i in range(cols):
            self.code_grid_frame.grid_columnconfigure(i, weight=1, minsize=200)

        for i, (_, row) in enumerate(page_codes.iterrows()):
            row_idx = i // cols
            col_idx = i % cols

            code_card = tk.Frame(self.code_grid_frame, bg='#1e293b', relief='ridge', bd=1)
            code_card.grid(row=row_idx, column=col_idx, padx=5, pady=3, sticky="nsew")

            content_frame = tk.Frame(code_card, bg='#1e293b')
            content_frame.pack(fill='both', expand=True, padx=10, pady=8)

            # Normalize and format code for display and barcode generation
            code_value = format_code(row.get('Code', ''))

            # Display the processed code value
            code_label = tk.Label(
                content_frame,
                text=code_value,
                font=('Segoe UI', 12, 'bold'),
                fg='#3b82f6',
                bg='#1e293b'
            )
            code_label.pack()

            # IMPORTANT: Use the SAME code_value for barcode generation
            # Debug: ensure consistent formatted code used for display and barcode
            # print(f"Debug: Code header='{code_value}' | Barcode input='{code_value}'")
            
            # Try to create actual barcode image first
            barcode_photo = self.create_barcode_image(code_value, 180, 50)
            
            if barcode_photo:
                # Display actual barcode image
                barcode_label = tk.Label(
                    content_frame,
                    image=barcode_photo,
                    bg='white'
                )
                barcode_label.image = barcode_photo  # Keep reference
                barcode_label.pack(pady=(5, 5))
            else:
                # Fallback: Create a text-based barcode representation for Code 128
                barcode_text = str(code_value)
                barcode_label = tk.Label(
                    content_frame,
                    text=barcode_text,
                    font=('Courier New', 12, 'normal'),  # Monospace font
                    bg='white',
                    fg='black',
                    width=20,
                    anchor='center',
                    pady=2
                )
                barcode_label.pack(pady=(5, 5))

            # Description
            desc_text = str(row.get("Description", "")).strip()
            if desc_text and desc_text != "nan":
                desc_label = tk.Label(
                    content_frame,
                    text=desc_text,
                    font=('Segoe UI', 9),
                    fg='#94a3b8',
                    bg='#1e293b',
                    wraplength=160,
                    justify='center'
                )
                desc_label.pack(pady=(0, 5), fill='x', expand=True)

        self.update_nav_buttons()
        
        self.codes_canvas.update_idletasks()
        self.codes_canvas.configure(scrollregion=self.codes_canvas.bbox("all"))

    def on_book_select(self, event):
        """Handle book selection from listbox"""
        selection = self.book_listbox.curselection()
        if not selection:
            return

        index = selection[0]
        book_name = self.book_listbox.get(index)
        self.selected_book = book_name
        self.codes_title_label.config(text=f"🔤 Codes for: {book_name}")
        self.page_index = 0
        self.update_code_grid()

    def delete_book(self):
        if not self.selected_book:
            messagebox.showwarning("No Selection", "Please select a book to delete.")
            return

        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete the book '{self.selected_book}'?"
        )
        if not confirm:
            return

        self.books_df = self.books_df[self.books_df["Book"] != self.selected_book]
        save_books(self.books_df)

        self.selected_book = None
        self.refresh_book_list()
        self.codes_title_label.config(text="🔤 Select a book to view codes")
        self.update_code_grid()

        messagebox.showinfo("Book Deleted", "The book has been deleted successfully.")

    def print_book(self):
        if not self.selected_book:
            messagebox.showwarning("No Selection", "Please select a book to print.")
            return

        codes = self.books_df[self.books_df["Book"] == self.selected_book]
        if codes.empty:
            messagebox.showinfo("No Codes", "This book doesn't have any codes to print.")
            return

        codes = codes.reset_index(drop=True)

        output_filename = f"{self.selected_book}_printout.pdf"
        try:
            generate_pdf(self.selected_book, codes.to_dict(orient="records"), output_path=output_filename)
            messagebox.showinfo("PDF Created", f"Printable PDF with Code 39 barcodes generated:\n{output_filename}")
            os.startfile(output_filename)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate PDF:\n{str(e)}")

    def edit_book(self):
        if not self.selected_book:
            messagebox.showwarning("No Selection", "Please select a book to edit.")
            return

        popup = tk.Toplevel(self)
        popup.title("Edit Book")
        popup.geometry("1000x700")
        popup.configure(bg='#1e293b')
        popup.transient(self)
        popup.grab_set()

        popup.update_idletasks()
        x = (popup.winfo_screenwidth() // 2) - (popup.winfo_width() // 2)
        y = (popup.winfo_screenheight() // 2) - (popup.winfo_height() // 2)
        popup.geometry(f"+{x}+{y}")

        content_frame = tk.Frame(popup, bg='#2d3748', relief='ridge', bd=1)
        content_frame.place(relx=0.5, rely=0.5, anchor='center', relwidth=0.95, relheight=0.95)

        title_label = tk.Label(
            content_frame,
            text="Edit Book",
            font=('Segoe UI', 18, 'bold'),
            fg='#ffffff',
            bg='#2d3748'
        )
        title_label.pack(pady=(20, 10))

        # Create two-column layout for edit dialog
        main_container = tk.Frame(content_frame, bg='#2d3748')
        main_container.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Left panel - Code selection
        left_panel = tk.Frame(main_container, bg='#2d3748')
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Right panel - Selected codes gallery
        right_panel = tk.Frame(main_container, bg='#374151', relief='ridge', bd=1, width=300)
        right_panel.pack(side='right', fill='both', padx=(10, 0))
        right_panel.pack_propagate(False)

        # Move name entry to left panel
        name_frame = tk.Frame(left_panel, bg='#2d3748')
        name_frame.pack(fill='x', pady=(0, 15))

        tk.Label(
            name_frame,
            text="Book Name:",
            font=('Segoe UI', 12),
            fg='#94a3b8',
            bg='#2d3748'
        ).pack(side='left', padx=(0, 10))

        name_entry = tk.Entry(
            name_frame,
            width=30,
            font=('Segoe UI', 12),
            bg='#1e293b',
            fg='#ffffff',
            relief='flat',
            insertbackground='#ffffff'
        )
        name_entry.pack(side='left', fill='x', expand=True, ipady=6)
        name_entry.insert(0, self.selected_book)
        name_entry.focus()

        tk.Label(
            left_panel,
            text="Available codes to add/remove:",
            font=('Segoe UI', 12),
            fg='#94a3b8',
            bg='#2d3748'
        ).pack(pady=(5, 5))

        search_frame = tk.Frame(left_panel, bg='#2d3748')
        search_frame.pack(fill='x', pady=(0, 10))

        tk.Label(
            search_frame,
            text="🔍",
            font=('Segoe UI', 11),
            fg='#94a3b8',
            bg='#2d3748'
        ).pack(side='left')

        search_entry = tk.Entry(
            search_frame,
            font=('Segoe UI', 11),
            bg='#1e293b',
            fg='#ffffff',
            relief='flat',
            insertbackground='#ffffff'
        )
        search_entry.pack(side='left', fill='x', expand=True, padx=(10, 0), ipady=4)

        listbox_frame = tk.Frame(left_panel, bg='#1e293b', relief='groove', bd=1)
        listbox_frame.pack(fill='both', expand=True, pady=(0, 15))

        scrollbar = ttk.Scrollbar(listbox_frame)
        scrollbar.pack(side='right', fill='y')

        codes_listbox = tk.Listbox(
            listbox_frame,
            font=('Segoe UI', 11),
            bg='#1e293b',
            fg='#ffffff',
            selectmode='multiple',
            selectbackground='#10b981',
            selectforeground='#ffffff',
            relief='flat',
            highlightthickness=0,
            yscrollcommand=scrollbar.set
        )
        codes_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=codes_listbox.yview)

        # Right panel - Selected codes gallery
        gallery_title = tk.Label(
            right_panel,
            text=f"📖 Codes in '{self.selected_book}'",
            font=('Segoe UI', 12, 'bold'),
            fg='#ffffff',
            bg='#374151'
        )
        gallery_title.pack(pady=(10, 5))

        # Gallery container with scrolling
        gallery_container = tk.Frame(right_panel, bg='#374151')
        gallery_container.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        gallery_canvas = tk.Canvas(gallery_container, bg='#374151', highlightthickness=0)
        gallery_scrollbar = ttk.Scrollbar(gallery_container, orient='vertical', command=gallery_canvas.yview)
        gallery_canvas.configure(yscrollcommand=gallery_scrollbar.set)
        
        gallery_scrollbar.pack(side='right', fill='y')
        gallery_canvas.pack(side='left', fill='both', expand=True)
        
        gallery_frame = tk.Frame(gallery_canvas, bg='#374151')
        gallery_window = gallery_canvas.create_window(0, 0, anchor='nw', window=gallery_frame)
        
        def update_gallery_scroll(event):
            gallery_canvas.configure(scrollregion=gallery_canvas.bbox("all"))
            gallery_canvas.itemconfig(gallery_window, width=event.width)
        
        gallery_canvas.bind('<Configure>', update_gallery_scroll)

        def update_selected_codes_gallery():
            """Update the gallery showing currently selected codes"""
            for widget in gallery_frame.winfo_children():
                widget.destroy()
            
            selected_indices = codes_listbox.curselection()
            if not selected_indices:
                no_codes_label = tk.Label(
                    gallery_frame,
                    text="No codes selected\nfor this book",
                    font=('Segoe UI', 10),
                    fg='#9ca3af',
                    bg='#374151',
                    justify='center'
                )
                no_codes_label.pack(pady=20)
                gallery_canvas.configure(scrollregion=gallery_canvas.bbox("all"))
                return
            
            # Create code cards in 2x2 grid
            cols = 2
            row = 0
            col = 0
            
            for idx in selected_indices:
                if idx < len(available_codes):
                    code, desc = available_codes[idx]
                    
                    # Create code card
                    card = tk.Frame(gallery_frame, bg='#1e293b', relief='ridge', bd=1)
                    card.grid(row=row, column=col, padx=3, pady=3, sticky='ew')
                    
                    # Code number
                    code_label = tk.Label(
                        card,
                        text=code,
                        font=('Segoe UI', 9, 'bold'),
                        fg='#3b82f6',
                        bg='#1e293b'
                    )
                    code_label.pack(pady=(3, 1))
                    
                    # Mini barcode representation
                    barcode_text = self.generate_mini_code128_display(code)
                    barcode_label = tk.Label(
                        card,
                        text=barcode_text,
                        font=('Courier New', 6),
                        fg='black',
                        bg='white',
                        width=15
                    )
                    barcode_label.pack(pady=1)
                    
                    # Description (truncated)
                    if desc and desc != "nan":
                        desc_short = desc[:15] + "..." if len(desc) > 15 else desc
                        desc_label = tk.Label(
                            card,
                            text=desc_short,
                            font=('Segoe UI', 7),
                            fg='#94a3b8',
                            bg='#1e293b'
                        )
                        desc_label.pack(pady=(1, 3))
                    
                    # Update grid position
                    col += 1
                    if col >= cols:
                        col = 0
                        row += 1
            
            # Configure grid weights
            for i in range(cols):
                gallery_frame.grid_columnconfigure(i, weight=1)
            
            gallery_canvas.configure(scrollregion=gallery_canvas.bbox("all"))

        def on_codes_listbox_select(event):
            """Handle selection changes in the codes listbox"""
            update_selected_codes_gallery()

        codes_listbox.bind('<<ListboxSelect>>', on_codes_listbox_select)

        available_codes = []
        existing_codes = set(format_code(code) for code in self.books_df[self.books_df["Book"] == self.selected_book]["Code"])

        def filter_codes(event=None):
            search_term = search_entry.get().lower()
            codes_listbox.delete(0, tk.END)
            available_codes.clear()
            listbox_index = 0
            
            # Reload available codes for filtering
            if os.path.exists("ALD_codes.csv"):
                try:
                    # Try UTF-8 first, then fallback encodings
                    try:
                        master_codes = pd.read_csv("ALD_codes.csv", encoding='utf-8')
                    except UnicodeDecodeError:
                        try:
                            master_codes = pd.read_csv("ALD_codes.csv", encoding='cp1252')
                        except UnicodeDecodeError:
                            master_codes = pd.read_csv("ALD_codes.csv", encoding='latin-1')
                    
                    master_codes['Code'] = master_codes['Code'].astype(str).str.replace('\xa0', ' ').str.strip()
                    master_codes['Description'] = master_codes['Description'].astype(str).str.replace('\xa0', ' ').str.strip()
                    
                    for _, row in master_codes.iterrows():
                        raw = str(row['Code']).strip()
                        code = format_code(raw)
                        desc = str(row.get('Description', '')).strip()
                        if code and code.lower() != 'nan':
                            display = f"{code} - {desc}"
                            if search_term == '' or search_term in code.lower() or search_term in desc.lower():
                                available_codes.append((code, desc))
                                codes_listbox.insert(tk.END, display)

                                # Check if this code is in the book and select it
                                if code in existing_codes:
                                    codes_listbox.selection_set(listbox_index)

                                listbox_index += 1
                except Exception as e:
                    codes_listbox.insert(tk.END, f"Error loading codes: {str(e)}")
            
            update_selected_codes_gallery()

        search_entry.bind('<KeyRelease>', filter_codes)

        # Initial load
        filter_codes()

        # Button frame at bottom of left panel
        button_frame = tk.Frame(left_panel, bg='#2d3748')
        button_frame.pack(fill='x', pady=10)

        def on_submit():
            new_name = name_entry.get().strip()
            if not new_name:
                messagebox.showwarning("Missing Name", "Please enter a book name.")
                return

            if new_name != self.selected_book and new_name in self.books_df["Book"].values:
                messagebox.showwarning("Duplicate Book", "That book already exists.")
                return

            selected_indices = codes_listbox.curselection()
            new_entries = []

            for idx in selected_indices:
                if idx < len(available_codes):
                    code, desc = available_codes[idx]
                    new_entries.append({"Book": new_name, "Code": code, "Description": desc})

            if not new_entries:
                new_entries.append({"Book": new_name, "Code": "", "Description": ""})

            self.books_df = self.books_df[self.books_df["Book"] != self.selected_book]
            
            new_df = pd.DataFrame(new_entries)
            self.books_df = pd.concat([self.books_df, new_df], ignore_index=True)
            save_books(self.books_df)

            self.selected_book = new_name
            self.refresh_book_list()
            self.codes_title_label.config(text=f"🔤 Codes for: {new_name}")
            self.update_code_grid()

            messagebox.showinfo("Book Updated", f"Book '{new_name}' updated successfully.")
            popup.destroy()

        save_btn = tk.Button(
            button_frame,
            text="✅ Save Changes",
            command=on_submit,
            font=('Segoe UI', 12, 'bold'),
            bg='#10b981',
            fg='#ffffff',
            relief='flat',
            cursor='hand2',
            padx=30,
            pady=12,
            width=15
        )
        save_btn.pack(side='left', padx=5)

        cancel_btn = tk.Button(
            button_frame,
            text="❌ Cancel",
            command=popup.destroy,
            font=('Segoe UI', 12),
            bg='#ef4444',
            fg='#ffffff',
            relief='flat',
            cursor='hand2',
            padx=30,
            pady=12,
            width=15
        )
        cancel_btn.pack(side='left', padx=5)

    def create_book(self):
        popup = tk.Toplevel(self)
        popup.title("New Book")
        popup.geometry("1000x700")
        popup.configure(bg='#1e293b')
        popup.transient(self)
        popup.grab_set()
            
        popup.update_idletasks()
        x = (popup.winfo_screenwidth() // 2) - (popup.winfo_width() // 2)
        y = (popup.winfo_screenheight() // 2) - (popup.winfo_height() // 2)
        popup.geometry(f"+{x}+{y}")
            
        content_frame = tk.Frame(popup, bg='#2d3748', relief='ridge', bd=1)
        content_frame.place(relx=0.5, rely=0.5, anchor='center', relwidth=0.95, relheight=0.95)
            
        title_label = tk.Label(
            content_frame,
            text="Create New Book",
            font=('Segoe UI', 18, 'bold'),
            fg='#ffffff',
            bg='#2d3748'
        )
        title_label.pack(pady=(20, 10))

        # Create two-column layout for new book dialog
        main_container = tk.Frame(content_frame, bg='#2d3748')
        main_container.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Left panel - Code selection
        left_panel = tk.Frame(main_container, bg='#2d3748')
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Right panel - Selected codes gallery
        right_panel = tk.Frame(main_container, bg='#374151', relief='ridge', bd=1, width=300)
        right_panel.pack(side='right', fill='both', padx=(10, 0))
        right_panel.pack_propagate(False)

        # Move name entry to left panel
        name_frame = tk.Frame(left_panel, bg='#2d3748')
        name_frame.pack(fill='x', pady=(0, 15))
        
        tk.Label(
            name_frame,
            text="Book Name:",
            font=('Segoe UI', 12),
            fg='#94a3b8',
            bg='#2d3748'
        ).pack(side='left', padx=(0, 10))
        
        name_entry = tk.Entry(
            name_frame,
            width=30,
            font=('Segoe UI', 12),
            bg='#1e293b',
            fg='#ffffff',
            relief='flat',
            insertbackground='#ffffff'
        )
        name_entry.pack(side='left', fill='x', expand=True, ipady=6)
        name_entry.focus()
        
        codes_label = tk.Label(
            left_panel,
            text="Select codes for this book (optional):",
            font=('Segoe UI', 12),
            fg='#94a3b8',
            bg='#2d3748'
        )
        codes_label.pack(pady=(5, 5))
        
        search_frame = tk.Frame(left_panel, bg='#2d3748')
        search_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(
            search_frame,
            text="🔍",
            font=('Segoe UI', 11),
            fg='#94a3b8',
            bg='#2d3748'
        ).pack(side='left')
        
        search_entry = tk.Entry(
            search_frame,
            font=('Segoe UI', 11),
            bg='#1e293b',
            fg='#ffffff',
            relief='flat',
            insertbackground='#ffffff'
        )
        search_entry.pack(side='left', fill='x', expand=True, padx=(10, 0), ipady=4)
        
        listbox_frame = tk.Frame(left_panel, bg='#1e293b', relief='groove', bd=1)
        listbox_frame.pack(fill='both', expand=True, pady=(0, 15))
        
        scrollbar = ttk.Scrollbar(listbox_frame)
        scrollbar.pack(side='right', fill='y')
        
        codes_listbox = tk.Listbox(
            listbox_frame,
            font=('Segoe UI', 11),
            bg='#1e293b',
            fg='#ffffff',
            selectmode='multiple',
            selectbackground='#10b981',
            selectforeground='#ffffff',
            relief='flat',
            highlightthickness=0,
            yscrollcommand=scrollbar.set
        )
        codes_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=codes_listbox.yview)

        # Right panel - New book codes gallery
        gallery_title = tk.Label(
            right_panel,
            text="📖 Codes for New Book",
            font=('Segoe UI', 12, 'bold'),
            fg='#ffffff',
            bg='#374151'
        )
        gallery_title.pack(pady=(10, 5))

        # Gallery container with scrolling
        new_book_gallery_container = tk.Frame(right_panel, bg='#374151')
        new_book_gallery_container.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        new_book_gallery_canvas = tk.Canvas(new_book_gallery_container, bg='#374151', highlightthickness=0)
        new_book_gallery_scrollbar = ttk.Scrollbar(new_book_gallery_container, orient='vertical', command=new_book_gallery_canvas.yview)
        new_book_gallery_canvas.configure(yscrollcommand=new_book_gallery_scrollbar.set)
        
        new_book_gallery_scrollbar.pack(side='right', fill='y')
        new_book_gallery_canvas.pack(side='left', fill='both', expand=True)
        
        new_book_gallery_frame = tk.Frame(new_book_gallery_canvas, bg='#374151')
        new_book_gallery_window = new_book_gallery_canvas.create_window(0, 0, anchor='nw', window=new_book_gallery_frame)
        
        def update_new_book_gallery_scroll(event):
            new_book_gallery_canvas.configure(scrollregion=new_book_gallery_canvas.bbox("all"))
            new_book_gallery_canvas.itemconfig(new_book_gallery_window, width=event.width)
        
        new_book_gallery_canvas.bind('<Configure>', update_new_book_gallery_scroll)

        def update_new_book_selected_codes_gallery():
            """Update the gallery showing codes selected for the new book"""
            for widget in new_book_gallery_frame.winfo_children():
                widget.destroy()
            
            selected_indices = codes_listbox.curselection()
            if not selected_indices:
                no_codes_label = tk.Label(
                    new_book_gallery_frame,
                    text="No codes selected\nfor new book",
                    font=('Segoe UI', 10),
                    fg='#9ca3af',
                    bg='#374151',
                    justify='center'
                )
                no_codes_label.pack(pady=20)
                new_book_gallery_canvas.configure(scrollregion=new_book_gallery_canvas.bbox("all"))
                return
            
            # Create code cards in 2x2 grid
            cols = 2
            row = 0
            col = 0
            
            for idx in selected_indices:
                if idx < len(available_codes):
                    code, desc = available_codes[idx]
                    
                    # Create code card
                    card = tk.Frame(new_book_gallery_frame, bg='#1e293b', relief='ridge', bd=1)
                    card.grid(row=row, column=col, padx=3, pady=3, sticky='ew')
                    
                    # Code number
                    code_label = tk.Label(
                        card,
                        text=code,
                        font=('Segoe UI', 9, 'bold'),
                        fg='#3b82f6',
                        bg='#1e293b'
                    )
                    code_label.pack(pady=(3, 1))
                    
                    # Mini barcode representation
                    barcode_text = self.generate_mini_code128_display(code)
                    barcode_label = tk.Label(
                        card,
                        text=barcode_text,
                        font=('Courier New', 6),
                        fg='black',
                        bg='white',
                        width=15
                    )
                    barcode_label.pack(pady=1)
                    
                    # Description (truncated)
                    if desc and desc != "nan":
                        desc_short = desc[:15] + "..." if len(desc) > 15 else desc
                        desc_label = tk.Label(
                            card,
                            text=desc_short,
                            font=('Segoe UI', 7),
                            fg='#94a3b8',
                            bg='#1e293b'
                        )
                        desc_label.pack(pady=(1, 3))
                    
                    # Update grid position
                    col += 1
                    if col >= cols:
                        col = 0
                        row += 1
            
            # Configure grid weights
            for i in range(cols):
                new_book_gallery_frame.grid_columnconfigure(i, weight=1)
            
            new_book_gallery_canvas.configure(scrollregion=new_book_gallery_canvas.bbox("all"))

        def on_new_book_codes_listbox_select(event):
            """Handle selection changes in the new book codes listbox"""
            update_new_book_selected_codes_gallery()

        codes_listbox.bind('<<ListboxSelect>>', on_new_book_codes_listbox_select)
        
        available_codes = []
        
        def filter_codes(event=None):
            search_term = search_entry.get().lower()
            codes_listbox.delete(0, tk.END)
            available_codes.clear()
            
            # Reload available codes for filtering
            if os.path.exists("ALD_codes.csv"):
                try:
                    try:
                        master_codes = pd.read_csv("ALD_codes.csv", encoding='utf-8')
                    except UnicodeDecodeError:
                        try:
                            master_codes = pd.read_csv("ALD_codes.csv", encoding='cp1252')
                        except UnicodeDecodeError:
                            master_codes = pd.read_csv("ALD_codes.csv", encoding='latin-1')
                    
                    master_codes['Code'] = master_codes['Code'].astype(str).str.replace('\xa0', ' ').str.strip()
                    master_codes['Description'] = master_codes['Description'].astype(str).str.replace('\xa0', ' ').str.strip()
                    
                    for _, row in master_codes.iterrows():
                        raw_code = str(row['Code']).strip()
                        code = format_code(raw_code)
                        desc = str(row.get('Description', '')).strip()
                        if code and code.lower() != 'nan':
                            display = f"{code} - {desc}"
                            if search_term == '' or search_term in code.lower() or search_term in desc.lower():
                                available_codes.append((code, desc))
                                codes_listbox.insert(tk.END, display)
                except Exception as e:
                    codes_listbox.insert(tk.END, f"Error loading codes: {str(e)}")
            
            if len(available_codes) == 0:
                codes_listbox.insert(tk.END, "No codes available. Add codes in Code Management.")
            
            update_new_book_selected_codes_gallery()
        
        search_entry.bind('<KeyRelease>', filter_codes)
        
        # Initial load
        filter_codes()

        # Button frame at bottom of left panel
        button_frame = tk.Frame(left_panel, bg='#2d3748')
        button_frame.pack(fill='x', pady=10)
        
        def on_submit():
            new_name = name_entry.get().strip()
            if new_name:
                if new_name in self.books_df["Book"].values:
                    messagebox.showwarning("Duplicate", "That book already exists.")
                    return
                
                selected_indices = codes_listbox.curselection()
                
                if selected_indices:
                    new_entries = []
                    for idx in selected_indices:
                        if idx < len(available_codes):
                            code, desc = available_codes[idx]
                            new_entries.append({
                                "Book": new_name,
                                "Code": code,
                                "Description": desc
                            })
                    new_df = pd.DataFrame(new_entries)
                else:
                    new_df = pd.DataFrame([{"Book": new_name, "Code": "", "Description": ""}])
                
                self.books_df = pd.concat([self.books_df, new_df], ignore_index=True)
                save_books(self.books_df)
                self.refresh_book_list()
                
                book_list = self.book_listbox.get(0, tk.END)
                if new_name in book_list:
                    index = book_list.index(new_name)
                    self.book_listbox.selection_clear(0, tk.END)
                    self.book_listbox.selection_set(index)
                    self.book_listbox.see(index)
                    self.selected_book = new_name
                    self.codes_title_label.config(text=f"🔤 Codes for: {new_name}")
                    self.update_code_grid()
                
                popup.destroy()
                
                if selected_indices:
                    messagebox.showinfo("Book Created", 
                        f"New book '{new_name}' created with {len(selected_indices)} Code 39 barcode(s).")
                else:
                    messagebox.showinfo("Book Created", 
                        f"New book '{new_name}' created. You can add Code 39 barcodes later by editing the book.")

        create_btn = tk.Button(
            button_frame,
            text="✅ Create Book",
            command=on_submit,
            font=('Segoe UI', 12, 'bold'),
            bg='#10b981',
            fg='#ffffff',
            relief='flat',
            cursor='hand2',
            padx=30,
            pady=12,
            width=15
        )
        create_btn.pack(side='left', padx=5)
        
        cancel_btn = tk.Button(
            button_frame,
            text="❌ Cancel",
            command=popup.destroy,
            font=('Segoe UI', 12),
            bg='#ef4444',
            fg='#ffffff',
            relief='flat',
            cursor='hand2',
            padx=30,
            pady=12,
            width=15
        )
        cancel_btn.pack(side='left', padx=5)
        
        def on_create_enter(e):
            create_btn.config(bg='#059669')
        def on_create_leave(e):
            create_btn.config(bg='#10b981')
        
        def on_cancel_enter(e):
            cancel_btn.config(bg='#dc2626')
        def on_cancel_leave(e):
            cancel_btn.config(bg='#ef4444')
        
        create_btn.bind('<Enter>', on_create_enter)
        create_btn.bind('<Leave>', on_create_leave)
        cancel_btn.bind('<Enter>', on_cancel_enter)
        cancel_btn.bind('<Leave>', on_cancel_leave)
        
        name_entry.bind("<Return>", lambda e: on_submit())