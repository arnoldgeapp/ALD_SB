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
        
        # Ensure necessary columns exist
        if 'Category' not in self.books_df.columns:
            self.books_df['Category'] = 'General'
        if 'CustomOrder' not in self.books_df.columns:
            self.books_df['CustomOrder'] = 0
            
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
        self.selected_category = "All"
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

        codes = self.get_filtered_codes()
        total_pages = max(1, (len(codes) + self.codes_per_page - 1) // self.codes_per_page)

        self.prev_btn.config(state="normal" if self.page_index > 0 else "disabled")
        self.next_btn.config(state="normal" if self.page_index < total_pages - 1 else "disabled")
        self.page_label.config(text=f"Page {self.page_index + 1} of {total_pages}")

    def get_filtered_codes(self):
        """Get codes filtered by selected category"""
        if not self.selected_book:
            return pd.DataFrame()
            
        codes = self.books_df[self.books_df["Book"] == self.selected_book].copy()
        
        if self.selected_category != "All":
            codes = codes[codes["Category"] == self.selected_category]
        
        # Sort by CustomOrder, then by Code
        codes = codes.sort_values(["CustomOrder", "Code"]).reset_index(drop=True)
        return codes

    def create_codes_panel(self, parent):
        """Create modern codes display panel with category tabs"""
        self.codes_card = tk.Frame(parent, bg='#2d3748', relief='ridge', bd=1)
        self.codes_card.grid(row=0, column=1, sticky='nsew')
        
        # Header with title and navigation
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
        
        # Category tabs
        self.tabs_frame = tk.Frame(self.codes_card, bg='#2d3748')
        self.tabs_frame.pack(fill='x', padx=15, pady=(5, 10))
        
        # Codes container
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
    
    def update_category_tabs(self):
        """Update the category tabs based on selected book"""
        # Clear existing tabs
        for widget in self.tabs_frame.winfo_children():
            widget.destroy()
        
        if not self.selected_book:
            return
        
        # Get unique categories for this book
        book_codes = self.books_df[self.books_df["Book"] == self.selected_book]
        categories = ["All"] + sorted(book_codes["Category"].unique().tolist())
        
        # Create tab buttons
        for cat in categories:
            btn_color = '#3b82f6' if cat == self.selected_category else '#4b5563'
            
            tab_btn = tk.Button(
                self.tabs_frame,
                text=f"📁 {cat}",
                command=lambda c=cat: self.select_category(c),
                font=('Segoe UI', 10),
                bg=btn_color,
                fg='#ffffff',
                relief='flat',
                cursor='hand2',
                padx=15,
                pady=5
            )
            tab_btn.pack(side='left', padx=2)
            
            def on_tab_enter(event, button=tab_btn, category=cat):
                if category != self.selected_category:
                    button.config(bg='#6b7280')
            
            def on_tab_leave(event, button=tab_btn, category=cat):
                if category != self.selected_category:
                    button.config(bg='#4b5563')
            
            tab_btn.bind('<Enter>', on_tab_enter)
            tab_btn.bind('<Leave>', on_tab_leave)
    
    def select_category(self, category):
        """Select a category tab"""
        self.selected_category = category
        self.page_index = 0
        self.update_category_tabs()
        self.update_code_grid()
    
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

        codes = self.get_filtered_codes()
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
        """Update the code grid with modern card style and Code 39 barcodes"""
        
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

        codes = self.get_filtered_codes()
        
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

            # Show category if not "All" filter
            if self.selected_category == "All":
                category = row.get('Category', 'General')
                cat_label = tk.Label(
                    content_frame,
                    text=f"[{category}]",
                    font=('Segoe UI', 8),
                    fg='#64748b',
                    bg='#1e293b'
                )
                cat_label.pack()

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
        self.selected_category = "All"
        self.codes_title_label.config(text=f"🔤 Codes for: {book_name}")
        self.page_index = 0
        self.update_category_tabs()
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

        # Sort by CustomOrder, then by Code
        codes = codes.sort_values(["CustomOrder", "Code"]).reset_index(drop=True)

        output_filename = f"{self.selected_book}_printout.pdf"
        try:
            # Pass categories for enhanced PDF generation
            generate_pdf(self.selected_book, codes.to_dict(orient="records"), output_path=output_filename)
            messagebox.showinfo("PDF Created", f"Printable PDF with Code 39 barcodes generated:\n{output_filename}")
            os.startfile(output_filename)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate PDF:\n{str(e)}")

    def edit_book(self):
        """Edit book with custom sorting and categories"""
        if not self.selected_book:
            messagebox.showwarning("No Selection", "Please select a book to edit.")
            return

        popup = tk.Toplevel(self)
        popup.title("Edit Book")
        popup.geometry("1200x800")
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

        # Create three-column layout for edit dialog
        main_container = tk.Frame(content_frame, bg='#2d3748')
        main_container.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Left panel - Code selection
        left_panel = tk.Frame(main_container, bg='#2d3748')
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Middle panel - Selected codes with sorting
        middle_panel = tk.Frame(main_container, bg='#374151', relief='ridge', bd=1, width=350)
        middle_panel.pack(side='left', fill='both', padx=(10, 10))
        middle_panel.pack_propagate(False)
        
        # Right panel - Category management
        right_panel = tk.Frame(main_container, bg='#404956', relief='ridge', bd=1, width=250)
        right_panel.pack(side='right', fill='both', padx=(10, 0))
        right_panel.pack_propagate(False)

        # Book name entry in left panel
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
            text="Available codes to add:",
            font=('Segoe UI', 12),
            fg='#94a3b8',
            bg='#2d3748'
        ).pack(pady=(5, 5))

        # Category selector for adding new codes
        add_cat_frame = tk.Frame(left_panel, bg='#2d3748')
        add_cat_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(
            add_cat_frame,
            text="Add new codes as:",
            font=('Segoe UI', 11),
            fg='#94a3b8',
            bg='#2d3748'
        ).pack(side='left', padx=(0, 10))
        
        add_category_var = tk.StringVar(value="General")
        add_category_combo = ttk.Combobox(
            add_cat_frame,
            textvariable=add_category_var,
            values=["General", "Safety", "Quality", "Production", "Maintenance"],
            font=('Segoe UI', 11),
            width=20,
            state='readonly'
        )
        add_category_combo.pack(side='left', fill='x', expand=True)

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

        # Middle panel - Selected codes with custom sorting
        middle_title = tk.Label(
            middle_panel,
            text=f"📖 Custom Order & Categories",
            font=('Segoe UI', 12, 'bold'),
            fg='#ffffff',
            bg='#374151'
        )
        middle_title.pack(pady=(10, 5))

        # Instructions
        instructions_label = tk.Label(
            middle_panel,
            text="Select a code below to change its category:",
            font=('Segoe UI', 9),
            fg='#94a3b8',
            bg='#374151'
        )
        instructions_label.pack(pady=(0, 5))

        # Category change frame
        cat_change_frame = tk.Frame(middle_panel, bg='#374151')
        cat_change_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        tk.Label(
            cat_change_frame,
            text="Change category to:",
            font=('Segoe UI', 10),
            fg='#94a3b8',
            bg='#374151'
        ).pack(side='left', padx=(0, 10))
        
        change_category_var = tk.StringVar(value="General")
        change_category_combo = ttk.Combobox(
            cat_change_frame,
            textvariable=change_category_var,
            values=["General", "Safety", "Quality", "Production", "Maintenance"],
            font=('Segoe UI', 10),
            width=15,
            state='readonly'
        )
        change_category_combo.pack(side='left', fill='x', expand=True)
        
        apply_cat_btn = tk.Button(
            cat_change_frame,
            text="Apply",
            font=('Segoe UI', 10),
            bg='#10b981',
            fg='#ffffff',
            relief='flat',
            cursor='hand2',
            width=8,
            command=lambda: apply_category_change()
        )
        apply_cat_btn.pack(side='left', padx=(5, 0))

        # Selected codes listbox with drag & drop support
        selected_container = tk.Frame(middle_panel, bg='#374151')
        selected_container.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        selected_scrollbar = ttk.Scrollbar(selected_container)
        selected_scrollbar.pack(side='right', fill='y')
        
        selected_listbox = tk.Listbox(
            selected_container,
            font=('Segoe UI', 10),
            bg='#2d3748',
            fg='#ffffff',
            selectmode='single',
            selectbackground='#8b5cf6',
            selectforeground='#ffffff',
            relief='flat',
            highlightthickness=0,
            yscrollcommand=selected_scrollbar.set
        )
        selected_listbox.pack(side='left', fill='both', expand=True)
        selected_scrollbar.config(command=selected_listbox.yview)

        # Sorting and action buttons
        sort_buttons_frame = tk.Frame(middle_panel, bg='#374151')
        sort_buttons_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        move_up_btn = tk.Button(
            sort_buttons_frame,
            text="⬆️ Move Up",
            font=('Segoe UI', 10),
            bg='#6366f1',
            fg='#ffffff',
            relief='flat',
            cursor='hand2',
            command=lambda: move_item_up()
        )
        move_up_btn.pack(side='left', padx=2, fill='x', expand=True)
        
        move_down_btn = tk.Button(
            sort_buttons_frame,
            text="⬇️ Move Down",
            font=('Segoe UI', 10),
            bg='#6366f1',
            fg='#ffffff',
            relief='flat',
            cursor='hand2',
            command=lambda: move_item_down()
        )
        move_down_btn.pack(side='left', padx=2, fill='x', expand=True)
        
        remove_btn = tk.Button(
            sort_buttons_frame,
            text="❌ Remove",
            font=('Segoe UI', 10),
            bg='#ef4444',
            fg='#ffffff',
            relief='flat',
            cursor='hand2',
            command=lambda: remove_selected_item()
        )
        remove_btn.pack(side='left', padx=2, fill='x', expand=True)

        # Right panel - Category management
        cat_title = tk.Label(
            right_panel,
            text="📁 Categories",
            font=('Segoe UI', 12, 'bold'),
            fg='#ffffff',
            bg='#404956'
        )
        cat_title.pack(pady=(10, 10))

        # Add new category
        new_cat_frame = tk.Frame(right_panel, bg='#404956')
        new_cat_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        new_cat_entry = tk.Entry(
            new_cat_frame,
            font=('Segoe UI', 10),
            bg='#2d3748',
            fg='#ffffff',
            relief='flat',
            insertbackground='#ffffff'
        )
        new_cat_entry.pack(side='left', fill='x', expand=True, ipady=4)
        
        add_cat_btn = tk.Button(
            new_cat_frame,
            text="➕",
            font=('Segoe UI', 10),
            bg='#10b981',
            fg='#ffffff',
            relief='flat',
            cursor='hand2',
            width=3,
            command=lambda: add_new_category()
        )
        add_cat_btn.pack(side='left', padx=(5, 0))

        # Categories listbox
        cat_listbox_frame = tk.Frame(right_panel, bg='#404956')
        cat_listbox_frame.pack(fill='both', expand=True, padx=10)
        
        cat_scrollbar = ttk.Scrollbar(cat_listbox_frame)
        cat_scrollbar.pack(side='right', fill='y')
        
        cat_listbox = tk.Listbox(
            cat_listbox_frame,
            font=('Segoe UI', 10),
            bg='#2d3748',
            fg='#ffffff',
            selectmode='single',
            selectbackground='#ec4899',
            selectforeground='#ffffff',
            relief='flat',
            highlightthickness=0,
            yscrollcommand=cat_scrollbar.set
        )
        cat_listbox.pack(side='left', fill='both', expand=True)
        cat_scrollbar.config(command=cat_listbox.yview)
        
        # Delete category button
        delete_cat_btn = tk.Button(
            right_panel,
            text="🗑️ Delete Selected Category",
            font=('Segoe UI', 10),
            bg='#ef4444',
            fg='#ffffff',
            relief='flat',
            cursor='hand2',
            command=lambda: delete_category()
        )
        delete_cat_btn.pack(fill='x', padx=10, pady=(10, 10))

        # Load existing categories
        def load_categories():
            cat_listbox.delete(0, tk.END)
            existing_cats = set(['General', 'Safety', 'Quality', 'Production', 'Maintenance'])
            book_codes = self.books_df[self.books_df["Book"] == self.selected_book]
            if not book_codes.empty:
                existing_cats.update(book_codes["Category"].unique())
            for cat in sorted(existing_cats):
                cat_listbox.insert(tk.END, cat)
            
            # Update both combo boxes
            sorted_cats = sorted(existing_cats)
            add_category_combo['values'] = sorted_cats
            change_category_combo['values'] = sorted_cats

        def add_new_category():
            new_cat = new_cat_entry.get().strip()
            if new_cat:
                current_cats = list(cat_listbox.get(0, tk.END))
                if new_cat not in current_cats:
                    cat_listbox.insert(tk.END, new_cat)
                    new_cat_entry.delete(0, tk.END)
                    # Update both combo boxes
                    sorted_cats = sorted(list(cat_listbox.get(0, tk.END)))
                    add_category_combo['values'] = sorted_cats
                    change_category_combo['values'] = sorted_cats
                else:
                    messagebox.showinfo("Category Exists", f"Category '{new_cat}' already exists.")

        def delete_category():
            selection = cat_listbox.curselection()
            if not selection:
                messagebox.showwarning("No Selection", "Please select a category to delete.")
                return
            
            cat_to_delete = cat_listbox.get(selection[0])
            if cat_to_delete == "General":
                messagebox.showwarning("Cannot Delete", "Cannot delete the 'General' category.")
                return
            
            # Check if category is in use
            codes_with_cat = [item for item in selected_codes_data if item[2] == cat_to_delete]
            if codes_with_cat:
                response = messagebox.askyesno(
                    "Category In Use",
                    f"Category '{cat_to_delete}' is assigned to {len(codes_with_cat)} code(s).\n"
                    f"These will be reassigned to 'General'. Continue?"
                )
                if response:
                    # Reassign codes to General
                    for item in selected_codes_data:
                        if item[2] == cat_to_delete:
                            item[2] = "General"
                    update_selected_codes_display()
                else:
                    return
            
            cat_listbox.delete(selection[0])
            # Update both combo boxes
            sorted_cats = sorted(list(cat_listbox.get(0, tk.END)))
            add_category_combo['values'] = sorted_cats
            change_category_combo['values'] = sorted_cats

        def apply_category_change():
            selection = selected_listbox.curselection()
            if not selection:
                messagebox.showwarning("No Selection", "Please select a code to change its category.")
                return
            
            idx = selection[0]
            new_category = change_category_var.get()
            selected_codes_data[idx][2] = new_category
            update_selected_codes_display()
            # Keep the same item selected
            selected_listbox.selection_set(idx)

        # Storage for selected codes with their categories
        selected_codes_data = []

        def update_selected_codes_display():
            """Update the display of selected codes with their categories"""
            selected_listbox.delete(0, tk.END)
            for i, (code, desc, cat, order) in enumerate(selected_codes_data):
                display = f"[{cat}] {code} - {desc}"
                selected_listbox.insert(tk.END, display)

        def move_item_up():
            selection = selected_listbox.curselection()
            if selection and selection[0] > 0:
                idx = selection[0]
                # Swap items
                selected_codes_data[idx], selected_codes_data[idx-1] = selected_codes_data[idx-1], selected_codes_data[idx]
                update_selected_codes_display()
                selected_listbox.selection_set(idx-1)

        def move_item_down():
            selection = selected_listbox.curselection()
            if selection and selection[0] < len(selected_codes_data) - 1:
                idx = selection[0]
                # Swap items
                selected_codes_data[idx], selected_codes_data[idx+1] = selected_codes_data[idx+1], selected_codes_data[idx]
                update_selected_codes_display()
                selected_listbox.selection_set(idx+1)

        def remove_selected_item():
            selection = selected_listbox.curselection()
            if selection:
                idx = selection[0]
                del selected_codes_data[idx]
                update_selected_codes_display()

        # Load existing codes for this book
        existing_codes = self.books_df[self.books_df["Book"] == self.selected_book].copy()
        existing_codes = existing_codes.sort_values(["CustomOrder", "Code"]).reset_index(drop=True)
        
        for _, row in existing_codes.iterrows():
            code = format_code(row['Code'])
            desc = str(row.get('Description', '')).strip()
            cat = row.get('Category', 'General')
            order = row.get('CustomOrder', 0)
            selected_codes_data.append([code, desc, cat, order])
        
        update_selected_codes_display()
        
        available_codes = []
        
        def filter_codes(event=None):
            search_term = search_entry.get().lower()
            codes_listbox.delete(0, tk.END)
            available_codes.clear()
            
            # Load available codes for filtering
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
                except Exception as e:
                    codes_listbox.insert(tk.END, f"Error loading codes: {str(e)}")

        def add_selected_codes():
            """Add selected codes to the book with category"""
            selected_indices = codes_listbox.curselection()
            category = add_category_var.get()
            
            added_count = 0
            for idx in selected_indices:
                if idx < len(available_codes):
                    code, desc = available_codes[idx]
                    # Check if not already added
                    if not any(item[0] == code for item in selected_codes_data):
                        selected_codes_data.append([code, desc, category, 0])
                        added_count += 1
            
            if added_count > 0:
                update_selected_codes_display()
                messagebox.showinfo("Codes Added", 
                    f"Added {added_count} code(s) to category '{category}'")
            else:
                messagebox.showinfo("No New Codes", 
                    "All selected codes are already in the book.")
            
            codes_listbox.selection_clear(0, tk.END)

        # Add button for adding codes
        add_codes_btn = tk.Button(
            left_panel,
            text="➕ Add Selected Codes",
            command=add_selected_codes,
            font=('Segoe UI', 11),
            bg='#10b981',
            fg='#ffffff',
            relief='flat',
            cursor='hand2',
            pady=8
        )
        add_codes_btn.pack(fill='x', pady=(0, 10))

        search_entry.bind('<KeyRelease>', filter_codes)

        # Initial load
        filter_codes()
        load_categories()

        # Button frame at bottom
        button_frame = tk.Frame(content_frame, bg='#2d3748')
        button_frame.pack(fill='x', pady=10)

        def on_submit():
            new_name = name_entry.get().strip()
            if not new_name:
                messagebox.showwarning("Missing Name", "Please enter a book name.")
                return

            if new_name != self.selected_book and new_name in self.books_df["Book"].values:
                messagebox.showwarning("Duplicate Book", "That book already exists.")
                return

            # Delete old book entries
            self.books_df = self.books_df[self.books_df["Book"] != self.selected_book]
            
            # Create new entries with custom order
            new_entries = []
            for i, (code, desc, cat, _) in enumerate(selected_codes_data):
                new_entries.append({
                    "Book": new_name,
                    "Code": code,
                    "Description": desc,
                    "Category": cat,
                    "CustomOrder": i  # Use position as custom order
                })

            if not new_entries:
                new_entries.append({
                    "Book": new_name, 
                    "Code": "", 
                    "Description": "",
                    "Category": "General",
                    "CustomOrder": 0
                })

            new_df = pd.DataFrame(new_entries)
            self.books_df = pd.concat([self.books_df, new_df], ignore_index=True)
            save_books(self.books_df)

            self.selected_book = new_name
            self.refresh_book_list()
            self.codes_title_label.config(text=f"🔤 Codes for: {new_name}")
            self.update_category_tabs()
            self.update_code_grid()

            messagebox.showinfo("Book Updated", f"Book '{new_name}' updated successfully with custom order and categories.")
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
        """Create new book with custom sorting and categories"""
        popup = tk.Toplevel(self)
        popup.title("Create New Book")
        popup.geometry("1200x800")
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

        # Create three-column layout
        main_container = tk.Frame(content_frame, bg='#2d3748')
        main_container.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Left panel - Code selection
        left_panel = tk.Frame(main_container, bg='#2d3748')
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Middle panel - Selected codes with sorting
        middle_panel = tk.Frame(main_container, bg='#374151', relief='ridge', bd=1, width=350)
        middle_panel.pack(side='left', fill='both', padx=(10, 10))
        middle_panel.pack_propagate(False)
        
        # Right panel - Category management
        right_panel = tk.Frame(main_container, bg='#404956', relief='ridge', bd=1, width=250)
        right_panel.pack(side='right', fill='both', padx=(10, 0))
        right_panel.pack_propagate(False)

        # Book name entry
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

        tk.Label(
            left_panel,
            text="Available codes to add:",
            font=('Segoe UI', 12),
            fg='#94a3b8',
            bg='#2d3748'
        ).pack(pady=(5, 5))

        # Category selector for adding new codes
        add_cat_frame = tk.Frame(left_panel, bg='#2d3748')
        add_cat_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(
            add_cat_frame,
            text="Add new codes as:",
            font=('Segoe UI', 11),
            fg='#94a3b8',
            bg='#2d3748'
        ).pack(side='left', padx=(0, 10))
        
        add_category_var = tk.StringVar(value="General")
        add_category_combo = ttk.Combobox(
            add_cat_frame,
            textvariable=add_category_var,
            values=["General", "Safety", "Quality", "Production", "Maintenance"],
            font=('Segoe UI', 11),
            width=20,
            state='readonly'
        )
        add_category_combo.pack(side='left', fill='x', expand=True)

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

        # Middle panel - Selected codes with custom sorting
        middle_title = tk.Label(
            middle_panel,
            text=f"📖 Custom Order & Categories",
            font=('Segoe UI', 12, 'bold'),
            fg='#ffffff',
            bg='#374151'
        )
        middle_title.pack(pady=(10, 5))

        # Instructions
        instructions_label = tk.Label(
            middle_panel,
            text="Select a code below to change its category:",
            font=('Segoe UI', 9),
            fg='#94a3b8',
            bg='#374151'
        )
        instructions_label.pack(pady=(0, 5))

        # Category change frame
        cat_change_frame = tk.Frame(middle_panel, bg='#374151')
        cat_change_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        tk.Label(
            cat_change_frame,
            text="Change category to:",
            font=('Segoe UI', 10),
            fg='#94a3b8',
            bg='#374151'
        ).pack(side='left', padx=(0, 10))
        
        change_category_var = tk.StringVar(value="General")
        change_category_combo = ttk.Combobox(
            cat_change_frame,
            textvariable=change_category_var,
            values=["General", "Safety", "Quality", "Production", "Maintenance"],
            font=('Segoe UI', 10),
            width=15,
            state='readonly'
        )
        change_category_combo.pack(side='left', fill='x', expand=True)
        
        apply_cat_btn = tk.Button(
            cat_change_frame,
            text="Apply",
            font=('Segoe UI', 10),
            bg='#10b981',
            fg='#ffffff',
            relief='flat',
            cursor='hand2',
            width=8,
            command=lambda: apply_category_change()
        )
        apply_cat_btn.pack(side='left', padx=(5, 0))

        # Selected codes listbox
        selected_container = tk.Frame(middle_panel, bg='#374151')
        selected_container.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        selected_scrollbar = ttk.Scrollbar(selected_container)
        selected_scrollbar.pack(side='right', fill='y')
        
        selected_listbox = tk.Listbox(
            selected_container,
            font=('Segoe UI', 10),
            bg='#2d3748',
            fg='#ffffff',
            selectmode='single',
            selectbackground='#8b5cf6',
            selectforeground='#ffffff',
            relief='flat',
            highlightthickness=0,
            yscrollcommand=selected_scrollbar.set
        )
        selected_listbox.pack(side='left', fill='both', expand=True)
        selected_scrollbar.config(command=selected_listbox.yview)

        # Sorting buttons
        sort_buttons_frame = tk.Frame(middle_panel, bg='#374151')
        sort_buttons_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        move_up_btn = tk.Button(
            sort_buttons_frame,
            text="⬆️ Move Up",
            font=('Segoe UI', 10),
            bg='#6366f1',
            fg='#ffffff',
            relief='flat',
            cursor='hand2',
            command=lambda: move_item_up()
        )
        move_up_btn.pack(side='left', padx=2, fill='x', expand=True)
        
        move_down_btn = tk.Button(
            sort_buttons_frame,
            text="⬇️ Move Down",
            font=('Segoe UI', 10),
            bg='#6366f1',
            fg='#ffffff',
            relief='flat',
            cursor='hand2',
            command=lambda: move_item_down()
        )
        move_down_btn.pack(side='left', padx=2, fill='x', expand=True)
        
        remove_btn = tk.Button(
            sort_buttons_frame,
            text="❌ Remove",
            font=('Segoe UI', 10),
            bg='#ef4444',
            fg='#ffffff',
            relief='flat',
            cursor='hand2',
            command=lambda: remove_selected_item()
        )
        remove_btn.pack(side='left', padx=2, fill='x', expand=True)

        # Right panel - Category management
        cat_title = tk.Label(
            right_panel,
            text="📁 Categories",
            font=('Segoe UI', 12, 'bold'),
            fg='#ffffff',
            bg='#404956'
        )
        cat_title.pack(pady=(10, 10))

        # Add new category
        new_cat_frame = tk.Frame(right_panel, bg='#404956')
        new_cat_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        new_cat_entry = tk.Entry(
            new_cat_frame,
            font=('Segoe UI', 10),
            bg='#2d3748',
            fg='#ffffff',
            relief='flat',
            insertbackground='#ffffff'
        )
        new_cat_entry.pack(side='left', fill='x', expand=True, ipady=4)
        
        add_cat_btn = tk.Button(
            new_cat_frame,
            text="➕",
            font=('Segoe UI', 10),
            bg='#10b981',
            fg='#ffffff',
            relief='flat',
            cursor='hand2',
            width=3,
            command=lambda: add_new_category()
        )
        add_cat_btn.pack(side='left', padx=(5, 0))

        # Categories listbox
        cat_listbox_frame = tk.Frame(right_panel, bg='#404956')
        cat_listbox_frame.pack(fill='both', expand=True, padx=10)
        
        cat_scrollbar = ttk.Scrollbar(cat_listbox_frame)
        cat_scrollbar.pack(side='right', fill='y')
        
        cat_listbox = tk.Listbox(
            cat_listbox_frame,
            font=('Segoe UI', 10),
            bg='#2d3748',
            fg='#ffffff',
            selectmode='single',
            selectbackground='#ec4899',
            selectforeground='#ffffff',
            relief='flat',
            highlightthickness=0,
            yscrollcommand=cat_scrollbar.set
        )
        cat_listbox.pack(side='left', fill='both', expand=True)
        cat_scrollbar.config(command=cat_listbox.yview)
        
        # Delete category button
        delete_cat_btn = tk.Button(
            right_panel,
            text="🗑️ Delete Selected Category",
            font=('Segoe UI', 10),
            bg='#ef4444',
            fg='#ffffff',
            relief='flat',
            cursor='hand2',
            command=lambda: delete_category()
        )
        delete_cat_btn.pack(fill='x', padx=10, pady=(10, 10))

        # Load default categories
        def load_categories():
            cat_listbox.delete(0, tk.END)
            default_cats = ['General', 'Safety', 'Quality', 'Production', 'Maintenance']
            for cat in default_cats:
                cat_listbox.insert(tk.END, cat)
            add_category_combo['values'] = default_cats
            change_category_combo['values'] = default_cats

        def add_new_category():
            new_cat = new_cat_entry.get().strip()
            if new_cat:
                current_cats = list(cat_listbox.get(0, tk.END))
                if new_cat not in current_cats:
                    cat_listbox.insert(tk.END, new_cat)
                    new_cat_entry.delete(0, tk.END)
                    sorted_cats = sorted(list(cat_listbox.get(0, tk.END)))
                    add_category_combo['values'] = sorted_cats
                    change_category_combo['values'] = sorted_cats
                else:
                    messagebox.showinfo("Category Exists", f"Category '{new_cat}' already exists.")
        
        def delete_category():
            selection = cat_listbox.curselection()
            if not selection:
                messagebox.showwarning("No Selection", "Please select a category to delete.")
                return
            
            cat_to_delete = cat_listbox.get(selection[0])
            if cat_to_delete == "General":
                messagebox.showwarning("Cannot Delete", "Cannot delete the 'General' category.")
                return
            
            # Check if category is in use
            codes_with_cat = [item for item in selected_codes_data if item[2] == cat_to_delete]
            if codes_with_cat:
                response = messagebox.askyesno(
                    "Category In Use",
                    f"Category '{cat_to_delete}' is assigned to {len(codes_with_cat)} code(s).\n"
                    f"These will be reassigned to 'General'. Continue?"
                )
                if response:
                    # Reassign codes to General
                    for item in selected_codes_data:
                        if item[2] == cat_to_delete:
                            item[2] = "General"
                    update_selected_codes_display()
                else:
                    return
            
            cat_listbox.delete(selection[0])
            sorted_cats = sorted(list(cat_listbox.get(0, tk.END)))
            add_category_combo['values'] = sorted_cats
            change_category_combo['values'] = sorted_cats
        
        def apply_category_change():
            selection = selected_listbox.curselection()
            if not selection:
                messagebox.showwarning("No Selection", "Please select a code to change its category.")
                return
            
            idx = selection[0]
            new_category = change_category_var.get()
            selected_codes_data[idx][2] = new_category
            update_selected_codes_display()
            selected_listbox.selection_set(idx)

        # Storage for selected codes
        selected_codes_data = []

        def update_selected_codes_display():
            selected_listbox.delete(0, tk.END)
            for i, (code, desc, cat, order) in enumerate(selected_codes_data):
                display = f"[{cat}] {code} - {desc}"
                selected_listbox.insert(tk.END, display)

        def move_item_up():
            selection = selected_listbox.curselection()
            if selection and selection[0] > 0:
                idx = selection[0]
                selected_codes_data[idx], selected_codes_data[idx-1] = selected_codes_data[idx-1], selected_codes_data[idx]
                update_selected_codes_display()
                selected_listbox.selection_set(idx-1)

        def move_item_down():
            selection = selected_listbox.curselection()
            if selection and selection[0] < len(selected_codes_data) - 1:
                idx = selection[0]
                selected_codes_data[idx], selected_codes_data[idx+1] = selected_codes_data[idx+1], selected_codes_data[idx]
                update_selected_codes_display()
                selected_listbox.selection_set(idx+1)

        def remove_selected_item():
            selection = selected_listbox.curselection()
            if selection:
                idx = selection[0]
                del selected_codes_data[idx]
                update_selected_codes_display()

        available_codes = []
        
        def filter_codes(event=None):
            search_term = search_entry.get().lower()
            codes_listbox.delete(0, tk.END)
            available_codes.clear()
            
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
                        raw = str(row['Code']).strip()
                        code = format_code(raw)
                        desc = str(row.get('Description', '')).strip()
                        if code and code.lower() != 'nan':
                            display = f"{code} - {desc}"
                            if search_term == '' or search_term in code.lower() or search_term in desc.lower():
                                available_codes.append((code, desc))
                                codes_listbox.insert(tk.END, display)
                except Exception as e:
                    codes_listbox.insert(tk.END, f"Error loading codes: {str(e)}")

        def add_selected_codes():
            selected_indices = codes_listbox.curselection()
            category = add_category_var.get()
            
            added_count = 0
            for idx in selected_indices:
                if idx < len(available_codes):
                    code, desc = available_codes[idx]
                    if not any(item[0] == code for item in selected_codes_data):
                        selected_codes_data.append([code, desc, category, 0])
                        added_count += 1
            
            if added_count > 0:
                update_selected_codes_display()
                messagebox.showinfo("Codes Added", 
                    f"Added {added_count} code(s) to category '{category}'")
            else:
                messagebox.showinfo("No New Codes", 
                    "All selected codes are already in the book.")
            
            codes_listbox.selection_clear(0, tk.END)

        # Add button
        add_codes_btn = tk.Button(
            left_panel,
            text="➕ Add Selected Codes",
            command=add_selected_codes,
            font=('Segoe UI', 11),
            bg='#10b981',
            fg='#ffffff',
            relief='flat',
            cursor='hand2',
            pady=8
        )
        add_codes_btn.pack(fill='x', pady=(0, 10))

        search_entry.bind('<KeyRelease>', filter_codes)

        # Initial load
        filter_codes()
        load_categories()

        # Button frame
        button_frame = tk.Frame(content_frame, bg='#2d3748')
        button_frame.pack(fill='x', pady=10)

        def on_submit():
            new_name = name_entry.get().strip()
            if not new_name:
                messagebox.showwarning("Missing Name", "Please enter a book name.")
                return

            if new_name in self.books_df["Book"].values:
                messagebox.showwarning("Duplicate Book", "That book already exists.")
                return

            # Create new entries
            new_entries = []
            if selected_codes_data:
                for i, (code, desc, cat, _) in enumerate(selected_codes_data):
                    new_entries.append({
                        "Book": new_name,
                        "Code": code,
                        "Description": desc,
                        "Category": cat,
                        "CustomOrder": i
                    })
            else:
                new_entries.append({
                    "Book": new_name,
                    "Code": "",
                    "Description": "",
                    "Category": "General",
                    "CustomOrder": 0
                })

            new_df = pd.DataFrame(new_entries)
            self.books_df = pd.concat([self.books_df, new_df], ignore_index=True)
            save_books(self.books_df)

            self.selected_book = new_name
            self.refresh_book_list()
            
            # Select the new book in the list
            book_list = self.book_listbox.get(0, tk.END)
            if new_name in book_list:
                index = book_list.index(new_name)
                self.book_listbox.selection_clear(0, tk.END)
                self.book_listbox.selection_set(index)
                self.book_listbox.see(index)
                self.codes_title_label.config(text=f"🔤 Codes for: {new_name}")
                self.update_category_tabs()
                self.update_code_grid()

            messagebox.showinfo("Book Created", 
                f"New book '{new_name}' created with {len(selected_codes_data)} codes.")
            popup.destroy()

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