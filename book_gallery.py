import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import os
import math

class BookGalleryScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg='#0f1419')
        self.controller = controller

        self.books_df = self.load_books()
        self.selected_book = None
        self.page_index = 0
        self.codes_per_page = 27
        
        # Animation variables
        self.animation_frame = 0
        self.hover_animations = {}
        
        self.create_background()
        self.create_content()
        self.start_animations()

    def create_background(self):
        """Create animated gradient background"""
        # Create canvas for background effects
        self.bg_canvas = tk.Canvas(self, highlightthickness=0)
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Bind resize event
        self.bg_canvas.bind('<Configure>', self.on_canvas_resize)
        
        # Initialize background
        self.draw_background()
    
    def draw_background(self):
        """Draw animated gradient background with floating shapes"""
        self.bg_canvas.delete("all")
        
        width = self.bg_canvas.winfo_width()
        height = self.bg_canvas.winfo_height()
        
        if width <= 1 or height <= 1:
            return
        
        # Create gradient background
        gradient_steps = 50
        for i in range(gradient_steps):
            progress = i / gradient_steps
            time_offset = self.animation_frame * 0.01
            
            r1, g1, b1 = 15, 20, 25   # Dark blue-gray
            r2, g2, b2 = 25, 35, 50   # Slightly lighter blue-gray
            
            # Add subtle animation to gradient
            wave = math.sin(progress * math.pi + time_offset) * 0.1
            
            r = int(r1 + (r2 - r1) * (progress + wave))
            g = int(g1 + (g2 - g1) * (progress + wave))
            b = int(b1 + (b2 - b1) * (progress + wave))
            
            color = f"#{r:02x}{g:02x}{b:02x}"
            
            y = i * height // gradient_steps
            next_y = (i + 1) * height // gradient_steps
            
            self.bg_canvas.create_rectangle(0, y, width, next_y, 
                                          fill=color, outline=color)
        
        # Add floating geometric shapes
        self.draw_floating_shapes(width, height)
    
    def draw_floating_shapes(self, width, height):
        """Draw animated floating geometric shapes"""
        shapes = [
            {'type': 'circle', 'x': 0.15, 'y': 0.2, 'size': 50, 'color': '#1e40af', 'speed': 0.4},
            {'type': 'circle', 'x': 0.85, 'y': 0.7, 'size': 70, 'color': '#1d4ed8', 'speed': 0.6},
            {'type': 'rect', 'x': 0.95, 'y': 0.15, 'size': 45, 'color': '#2563eb', 'speed': 0.5},
            {'type': 'rect', 'x': 0.08, 'y': 0.85, 'size': 60, 'color': '#3730a3', 'speed': 0.7},
        ]
        
        for shape in shapes:
            base_x = shape['x'] * width
            base_y = shape['y'] * height
            
            # Floating animation
            float_x = base_x + math.sin(self.animation_frame * 0.02 * shape['speed']) * 20
            float_y = base_y + math.cos(self.animation_frame * 0.015 * shape['speed']) * 15
            
            size = shape['size']
            
            if shape['type'] == 'circle':
                self.bg_canvas.create_oval(float_x - size//2, float_y - size//2,
                                         float_x + size//2, float_y + size//2,
                                         fill=shape['color'], outline="")
            else:
                self.bg_canvas.create_rectangle(float_x - size//2, float_y - size//2,
                                              float_x + size//2, float_y + size//2,
                                              fill=shape['color'], outline="")
    
    def on_canvas_resize(self, event):
        """Handle canvas resize"""
        self.draw_background()
    
    def create_content(self):
        """Create main content with glass morphism effect"""
        # Main content container with glass effect
        self.content_frame = tk.Frame(self, bg='#1e293b', relief='ridge', bd=1)
        self.content_frame.place(relx=0.5, rely=0.5, anchor='center', 
                                relwidth=0.9, relheight=0.9)
        
        # Add subtle border
        border_frame = tk.Frame(self.content_frame, bg='#334155', height=2)
        border_frame.pack(fill='x')
        
        # Add close button at top right
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
        
        # Hover effects for close button
        close_btn.bind('<Enter>', lambda e: close_btn.config(bg='#dc2626'))
        close_btn.bind('<Leave>', lambda e: close_btn.config(bg='#ef4444'))
        
        # Header section
        self.create_header()
        
        # Main content area
        self.create_main_content()
        
        # Footer with back button
        self.create_footer()
        
        # Load initial data
        self.refresh_book_list()
    
    def create_header(self):
        """Create animated header section"""
        header_frame = tk.Frame(self.content_frame, bg='#1e293b')
        header_frame.pack(pady=(30, 20))
        
        # Main title
        title_label = tk.Label(header_frame,
                              text="Book Gallery",
                              font=('Segoe UI', 32, 'bold'),
                              fg='#ffffff',
                              bg='#1e293b')
        title_label.pack()
        
        # Subtitle
        subtitle_label = tk.Label(header_frame,
                                 text="Browse and manage your book collections",
                                 font=('Segoe UI', 12),
                                 fg='#94a3b8',
                                 bg='#1e293b')
        subtitle_label.pack(pady=(5, 0))
        
        # Animated accent line
        accent_canvas = tk.Canvas(header_frame, width=150, height=3,
                                 bg='#1e293b', highlightthickness=0)
        accent_canvas.pack(pady=10)
        self.accent_canvas = accent_canvas
        self.draw_accent_line()
    
    def draw_accent_line(self):
        """Draw animated accent line"""
        self.accent_canvas.delete("all")
        
        width = 150
        progress = (math.sin(self.animation_frame * 0.03) + 1) / 2
        
        for i in range(width):
            x_progress = i / width
            intensity = progress * (1 - abs(x_progress - 0.5) * 2)
            
            if intensity > 0.1:
                if intensity > 0.8:
                    color = '#3b82f6'
                elif intensity > 0.5:
                    color = '#2563eb'
                else:
                    color = '#1e40af'
                
                self.accent_canvas.create_line(i, 1, i+1, 1, fill=color, width=2)
    
    def create_main_content(self):
        """Create main content area with books list and codes display"""
        main_container = tk.Frame(self.content_frame, bg='#1e293b')
        main_container.pack(expand=True, fill='both', padx=40, pady=20)
        
        # Left panel - Books list
        self.create_books_panel(main_container)
        
        # Right panel - Codes display
        self.create_codes_panel(main_container)
    
    def create_books_panel(self, parent):
        """Create modern books list panel"""
        # Books panel card
        books_card = tk.Frame(parent, bg='#2d3748', relief='ridge', bd=1)
        books_card.pack(side='left', fill='both', padx=(0, 20))
        
        # Panel header
        header_frame = tk.Frame(books_card, bg='#2d3748')
        header_frame.pack(fill='x', padx=20, pady=(20, 10))
        
        books_label = tk.Label(header_frame,
                              text="📚 Your Books",
                              font=('Segoe UI', 16, 'bold'),
                              fg='#ffffff',
                              bg='#2d3748')
        books_label.pack(side='left')
        
        # Books count
        self.books_count_label = tk.Label(header_frame,
                                         text=f"({len(self.get_unique_books())} books)",
                                         font=('Segoe UI', 11),
                                         fg='#64748b',
                                         bg='#2d3748')
        self.books_count_label.pack(side='left', padx=(10, 0))
        
        # Listbox container with modern styling
        listbox_frame = tk.Frame(books_card, bg='#1e293b', relief='groove', bd=1)
        listbox_frame.pack(fill='both', expand=True, padx=20, pady=(0, 10))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(listbox_frame)
        scrollbar.pack(side='right', fill='y')
        
        # Modern listbox
        self.book_listbox = tk.Listbox(
            listbox_frame,
            width=35,
            height=15,
            yscrollcommand=scrollbar.set,
            font=('Segoe UI', 11),
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
        
        # Action buttons with modern styling
        self.create_action_buttons(books_card)
    
    def create_action_buttons(self, parent):
        """Create modern action buttons"""
        buttons_frame = tk.Frame(parent, bg='#2d3748')
        buttons_frame.pack(fill='x', padx=20, pady=(10, 20))
        
        button_configs = [
            {'text': '➕ New Book', 'command': self.create_book, 'color': '#10b981'},
            {'text': '✏️ Edit Book', 'command': self.edit_book, 'color': '#3b82f6'},
            {'text': '🗑️ Delete Book', 'command': self.delete_book, 'color': '#ef4444'},
            {'text': '🖨️ Print Book', 'command': self.print_book, 'color': '#8b5cf6'},
        ]
        
        for config in button_configs:
            btn_frame = tk.Frame(buttons_frame, bg=config['color'], relief='flat')
            btn_frame.pack(fill='x', pady=5)
            
            btn = tk.Button(
                btn_frame,
                text=config['text'],
                command=config['command'],
                font=('Segoe UI', 11),
                bg=config['color'],
                fg='#ffffff',
                relief='flat',
                cursor='hand2',
                pady=8
            )
            btn.pack(fill='both', expand=True)
            
            # Hover effects
            def on_enter(event, button=btn, color=config['color']):
                # Darken color on hover
                r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
                darker = f"#{max(0, r-20):02x}{max(0, g-20):02x}{max(0, b-20):02x}"
                button.config(bg=darker)
            
            def on_leave(event, button=btn, color=config['color']):
                button.config(bg=color)
            
            btn.bind('<Enter>', on_enter)
            btn.bind('<Leave>', on_leave)
    
    def create_codes_panel(self, parent):
        """Create modern codes display panel"""
        # Codes panel card
        self.codes_card = tk.Frame(parent, bg='#2d3748', relief='ridge', bd=1)
        self.codes_card.pack(side='left', fill='both', expand=True)
        
        # Panel header
        header_frame = tk.Frame(self.codes_card, bg='#2d3748')
        header_frame.pack(fill='x', padx=20, pady=(20, 10))
        
        self.codes_title_label = tk.Label(
            header_frame,
            text="🔤 Select a book to view codes",
            font=('Segoe UI', 16, 'bold'),
            fg='#ffffff',
            bg='#2d3748'
        )
        self.codes_title_label.pack(side='left')
        
        # Codes container
        codes_container = tk.Frame(self.codes_card, bg='#2d3748')
        codes_container.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Code grid frame
        self.code_grid_frame = tk.Frame(codes_container, bg='#2d3748')
        self.code_grid_frame.pack(expand=True)
        
        # Navigation controls
        self.create_navigation_controls(codes_container)
    
    def create_navigation_controls(self, parent):
        """Create modern navigation controls"""
        nav_frame = tk.Frame(parent, bg='#2d3748')
        nav_frame.pack(side='bottom', pady=10)
        
        # Previous button
        self.prev_btn = tk.Button(
            nav_frame,
            text='◄ Previous',
            command=self.prev_page,
            font=('Segoe UI', 11),
            bg='#3b82f6',
            fg='#ffffff',
            relief='flat',
            cursor='hand2',
            padx=20,
            pady=8
        )
        self.prev_btn.pack(side='left', padx=5)
        
        # Page indicator
        self.page_label = tk.Label(
            nav_frame,
            text="Page 1 of 1",
            font=('Segoe UI', 11),
            fg='#94a3b8',
            bg='#2d3748'
        )
        self.page_label.pack(side='left', padx=20)
        
        # Next button
        self.next_btn = tk.Button(
            nav_frame,
            text='Next ►',
            command=self.next_page,
            font=('Segoe UI', 11),
            bg='#3b82f6',
            fg='#ffffff',
            relief='flat',
            cursor='hand2',
            padx=20,
            pady=8
        )
        self.next_btn.pack(side='left', padx=5)
        
        # Add hover effects to nav buttons
        for btn in [self.prev_btn, self.next_btn]:
            btn.bind('<Enter>', lambda e, b=btn: b.config(bg='#2563eb'))
            btn.bind('<Leave>', lambda e, b=btn: b.config(bg='#3b82f6'))
        
        self.update_nav_buttons()
    
    def create_footer(self):
        """Create footer with back button"""
        # Create a more prominent footer frame at the bottom of the content frame
        footer_frame = tk.Frame(self.content_frame, bg='#1e293b')
        footer_frame.pack(side='bottom', fill='x', pady=(20, 30))
        
        # Separator line above footer
        separator = tk.Frame(footer_frame, bg='#334155', height=1)
        separator.pack(fill='x', pady=(0, 20))
        
        # Back button container for centering
        button_container = tk.Frame(footer_frame, bg='#1e293b')
        button_container.pack()
        
        # Back button with highly visible styling
        back_btn = tk.Button(
            button_container,
            text='🏠 Back to Main Menu',
            command=lambda: self.controller.show_frame("ModernMainMenu"),
            font=('Segoe UI', 16, 'bold'),
            bg='#3b82f6',
            fg='#ffffff',
            relief='flat',
            cursor='hand2',
            padx=50,
            pady=15,
            bd=2
        )
        back_btn.pack()
        
        # Hover effects
        def on_enter(e):
            back_btn.config(bg='#2563eb')
        
        def on_leave(e):
            back_btn.config(bg='#3b82f6')
        
        back_btn.bind('<Enter>', on_enter)
        back_btn.bind('<Leave>', on_leave)
    
    def update_code_grid(self):
        """Update the code grid with modern card style"""
        for widget in self.code_grid_frame.winfo_children():
            widget.destroy()

        if not self.selected_book:
            # Empty state
            empty_label = tk.Label(
                self.code_grid_frame,
                text="Select a book from the list to view its codes",
                font=('Segoe UI', 14),
                fg='#64748b',
                bg='#2d3748'
            )
            empty_label.pack(pady=100)
            return

        codes = self.books_df[self.books_df["Book"] == self.selected_book]
        codes = codes.sort_values("Code", key=lambda col: col.astype(str)).reset_index(drop=True)
        
        start = self.page_index * self.codes_per_page
        end = start + self.codes_per_page
        page_codes = codes[start:end]

        for i, (_, row) in enumerate(page_codes.iterrows()):
            row_idx = i // 3
            col_idx = i % 3
            
            # Code card with modern styling
            code_card = tk.Frame(self.code_grid_frame, bg='#1e293b', relief='ridge', bd=1)
            code_card.grid(row=row_idx, column=col_idx, padx=8, pady=8, sticky="nsew")
            
            # Card content
            content_frame = tk.Frame(code_card, bg='#1e293b')
            content_frame.pack(fill='both', expand=True, padx=15, pady=15)
            
            # Code label
            code_label = tk.Label(
                content_frame,
                text=str(row['Code']),
                font=('Segoe UI', 14, 'bold'),
                fg='#3b82f6',
                bg='#1e293b'
            )
            code_label.pack()
            
            # Description label
            desc_label = tk.Label(
                content_frame,
                text=str(row['Description']),
                font=('Segoe UI', 10),
                fg='#94a3b8',
                bg='#1e293b',
                wraplength=150
            )
            desc_label.pack(pady=(5, 0))
            
            # Hover effect
            def on_enter(event, card=code_card):
                card.config(bg='#334155')
                for child in card.winfo_children():
                    child.config(bg='#334155')
                    for subchild in child.winfo_children():
                        subchild.config(bg='#334155')
            
            def on_leave(event, card=code_card):
                card.config(bg='#1e293b')
                for child in card.winfo_children():
                    child.config(bg='#1e293b')
                    for subchild in child.winfo_children():
                        subchild.config(bg='#1e293b')
            
            code_card.bind('<Enter>', on_enter)
            code_card.bind('<Leave>', on_leave)

        # Update page label
        total_codes = len(codes)
        total_pages = max(1, (total_codes + self.codes_per_page - 1) // self.codes_per_page)
        current_page = self.page_index + 1
        self.page_label.config(text=f"Page {current_page} of {total_pages}")
    
    def create_book(self):
        """Create new book with modern dialog"""
        popup = tk.Toplevel(self)
        popup.title("New Book")
        popup.geometry("500x250")
        popup.configure(bg='#1e293b')
        popup.transient(self)
        popup.grab_set()
        
        # Center the popup
        popup.update_idletasks()
        x = (popup.winfo_screenwidth() // 2) - (popup.winfo_width() // 2)
        y = (popup.winfo_screenheight() // 2) - (popup.winfo_height() // 2)
        popup.geometry(f"+{x}+{y}")
        
        # Content with glass morphism
        content_frame = tk.Frame(popup, bg='#2d3748', relief='ridge', bd=1)
        content_frame.place(relx=0.5, rely=0.5, anchor='center', relwidth=0.9, relheight=0.85)
        
        # Title
        title_label = tk.Label(
            content_frame,
            text="Create New Book",
            font=('Segoe UI', 18, 'bold'),
            fg='#ffffff',
            bg='#2d3748'
        )
        title_label.pack(pady=(30, 10))
        
        # Input frame
        input_frame = tk.Frame(content_frame, bg='#2d3748')
        input_frame.pack(pady=20)
        
        tk.Label(
            input_frame,
            text="Book Name:",
            font=('Segoe UI', 12),
            fg='#94a3b8',
            bg='#2d3748'
        ).pack()
        
        # Modern entry
        entry = tk.Entry(
            input_frame,
            width=30,
            font=('Segoe UI', 12),
            bg='#1e293b',
            fg='#ffffff',
            relief='flat',
            insertbackground='#ffffff'
        )
        entry.pack(pady=10, ipady=8)
        entry.focus()

        def on_submit():
            new_name = entry.get().strip()
            if new_name:
                if new_name in self.books_df["Book"].values:
                    messagebox.showwarning("Duplicate", "That book already exists.")
                    return
                new_entry = pd.DataFrame([{"Book": new_name, "Code": "", "Description": ""}])
                self.books_df = pd.concat([self.books_df, new_entry], ignore_index=True)
                self.save_books()
                self.refresh_book_list()
                popup.destroy()
                messagebox.showinfo("Book Created", f"New book '{new_name}' created.")

        # Buttons
        button_frame = tk.Frame(content_frame, bg='#2d3748')
        button_frame.pack(pady=20)
        
        create_btn = tk.Button(
            button_frame,
            text="Create Book",
            command=on_submit,
            font=('Segoe UI', 11),
            bg='#10b981',
            fg='#ffffff',
            relief='flat',
            cursor='hand2',
            padx=20,
            pady=8
        )
        create_btn.pack(side='left', padx=10)
        
        cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            command=popup.destroy,
            font=('Segoe UI', 11),
            bg='#ef4444',
            fg='#ffffff',
            relief='flat',
            cursor='hand2',
            padx=20,
            pady=8
        )
        cancel_btn.pack(side='left', padx=10)
        
        entry.bind("<Return>", lambda e: on_submit())
    
    def get_unique_books(self):
        """Get list of unique book names"""
        return sorted([b for b in self.books_df["Book"].unique() if isinstance(b, str) and b])
    
    def refresh_book_list(self):
        """Refresh the book list"""
        self.book_listbox.delete(0, tk.END)
        book_names = self.get_unique_books()
        for book in book_names:
            self.book_listbox.insert(tk.END, book)
        self.books_count_label.config(text=f"({len(book_names)} books)")
    
    def on_book_select(self, event=None):
        """Handle book selection"""
        try:
            index = self.book_listbox.curselection()[0]
            self.selected_book = self.book_listbox.get(index)
            self.codes_title_label.config(text=f"🔤 Codes for: {self.selected_book}")
            self.page_index = 0
            self.update_code_grid()
            self.update_nav_buttons()
        except IndexError:
            pass
    
    def update_nav_buttons(self):
        """Update navigation button states"""
        if not self.selected_book:
            self.prev_btn.config(state="disabled", bg='#475569')
            self.next_btn.config(state="disabled", bg='#475569')
            return

        total_codes = len(self.books_df[self.books_df["Book"] == self.selected_book])
        total_pages = max(1, (total_codes + self.codes_per_page - 1) // self.codes_per_page)
        
        self.prev_btn.config(
            state="normal" if self.page_index > 0 else "disabled",
            bg='#3b82f6' if self.page_index > 0 else '#475569'
        )
        self.next_btn.config(
            state="normal" if self.page_index < total_pages - 1 else "disabled",
            bg='#3b82f6' if self.page_index < total_pages - 1 else '#475569'
        )
    
    def prev_page(self):
        """Go to previous page"""
        if self.page_index > 0:
            self.page_index -= 1
            self.update_code_grid()
            self.update_nav_buttons()
    
    def next_page(self):
        """Go to next page"""
        if not self.selected_book:
            return
        total_codes = len(self.books_df[self.books_df["Book"] == self.selected_book])
        total_pages = max(1, (total_codes + self.codes_per_page - 1) // self.codes_per_page)
        if self.page_index < total_pages - 1:
            self.page_index += 1
            self.update_code_grid()
            self.update_nav_buttons()
    
    def delete_book(self):
        """Delete selected book"""
        if not self.selected_book:
            messagebox.showwarning("No Selection", "Please select a book to delete.")
            return
        
        confirm = messagebox.askyesno(
            "Delete Book", 
            f"Are you sure you want to delete '{self.selected_book}'?\n\nThis will also delete all associated codes."
        )
        if confirm:
            self.books_df = self.books_df[self.books_df["Book"] != self.selected_book]
            self.save_books()
            self.selected_book = None
            self.codes_title_label.config(text="🔤 Select a book to view codes")
            self.refresh_book_list()
            self.update_code_grid()
            self.update_nav_buttons()
            messagebox.showinfo("Deleted", "Book deleted successfully.")
    
    def edit_book(self):
        """Edit selected book with modern dialog"""
        if not self.selected_book:
            messagebox.showwarning("No Selection", "Please select a book to edit.")
            return
        
        popup = tk.Toplevel(self)
        popup.title("Edit Book")
        popup.geometry("500x250")
        popup.configure(bg='#1e293b')
        popup.transient(self)
        popup.grab_set()
        
        # Center the popup
        popup.update_idletasks()
        x = (popup.winfo_screenwidth() // 2) - (popup.winfo_width() // 2)
        y = (popup.winfo_screenheight() // 2) - (popup.winfo_height() // 2)
        popup.geometry(f"+{x}+{y}")
        
        # Content with glass morphism
        content_frame = tk.Frame(popup, bg='#2d3748', relief='ridge', bd=1)
        content_frame.place(relx=0.5, rely=0.5, anchor='center', relwidth=0.9, relheight=0.85)
        
        # Title
        title_label = tk.Label(
            content_frame,
            text="Edit Book Name",
            font=('Segoe UI', 18, 'bold'),
            fg='#ffffff',
            bg='#2d3748'
        )
        title_label.pack(pady=(30, 10))
        
        # Current name label
        current_label = tk.Label(
            content_frame,
            text=f"Current: {self.selected_book}",
            font=('Segoe UI', 11),
            fg='#64748b',
            bg='#2d3748'
        )
        current_label.pack()
        
        # Input frame
        input_frame = tk.Frame(content_frame, bg='#2d3748')
        input_frame.pack(pady=20)
        
        tk.Label(
            input_frame,
            text="New Name:",
            font=('Segoe UI', 12),
            fg='#94a3b8',
            bg='#2d3748'
        ).pack()
        
        # Modern entry with current name
        entry = tk.Entry(
            input_frame,
            width=30,
            font=('Segoe UI', 12),
            bg='#1e293b',
            fg='#ffffff',
            relief='flat',
            insertbackground='#ffffff'
        )
        entry.pack(pady=10, ipady=8)
        entry.insert(0, self.selected_book)
        entry.select_range(0, tk.END)
        entry.focus()

        def on_submit():
            new_name = entry.get().strip()
            if new_name and new_name != self.selected_book:
                # Check if new name already exists
                if new_name in self.books_df["Book"].values:
                    messagebox.showwarning("Duplicate", "A book with that name already exists.")
                    return
                
                # Update all rows with the old book name
                self.books_df.loc[self.books_df["Book"] == self.selected_book, "Book"] = new_name
                self.save_books()
                
                # Update selection and refresh
                old_name = self.selected_book
                self.selected_book = new_name
                self.refresh_book_list()
                
                # Reselect the renamed book
                book_list = self.book_listbox.get(0, tk.END)
                if new_name in book_list:
                    index = book_list.index(new_name)
                    self.book_listbox.selection_clear(0, tk.END)
                    self.book_listbox.selection_set(index)
                    self.book_listbox.see(index)
                
                # Update display
                self.codes_title_label.config(text=f"🔤 Codes for: {new_name}")
                self.update_code_grid()
                
                popup.destroy()
                messagebox.showinfo("Book Renamed", f"Book renamed from '{old_name}' to '{new_name}'.")
            elif new_name == self.selected_book:
                popup.destroy()

        # Buttons
        button_frame = tk.Frame(content_frame, bg='#2d3748')
        button_frame.pack(pady=20)
        
        save_btn = tk.Button(
            button_frame,
            text="Save Changes",
            command=on_submit,
            font=('Segoe UI', 11),
            bg='#10b981',
            fg='#ffffff',
            relief='flat',
            cursor='hand2',
            padx=20,
            pady=8
        )
        save_btn.pack(side='left', padx=10)
        
        cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            command=popup.destroy,
            font=('Segoe UI', 11),
            bg='#ef4444',
            fg='#ffffff',
            relief='flat',
            cursor='hand2',
            padx=20,
            pady=8
        )
        cancel_btn.pack(side='left', padx=10)
        
        # Bind Enter key
        entry.bind("<Return>", lambda e: on_submit())
        
        # Add hover effects
        save_btn.bind('<Enter>', lambda e: save_btn.config(bg='#059669'))
        save_btn.bind('<Leave>', lambda e: save_btn.config(bg='#10b981'))
        cancel_btn.bind('<Enter>', lambda e: cancel_btn.config(bg='#dc2626'))
        cancel_btn.bind('<Leave>', lambda e: cancel_btn.config(bg='#ef4444'))
    
    def print_book(self):
        """Print selected book"""
        if not self.selected_book:
            messagebox.showwarning("No Selection", "Please select a book to print.")
            return
        messagebox.showinfo("Print Book", f"Printing '{self.selected_book}' - Feature coming soon!")
    
    def load_books(self):
        """Load books from CSV"""
        if os.path.exists("ald_books.csv"):
            df = pd.read_csv("ald_books.csv")
            df["Book"] = df["Book"].fillna("").astype(str)
            return df
        return pd.DataFrame(columns=["Book", "Code", "Description"])
    
    def save_books(self):
        """Save books to CSV"""
        self.books_df.to_csv("ald_books.csv", index=False)
    
    def start_animations(self):
        """Start background animations"""
        def animate():
            self.animation_frame += 1
            self.draw_background()
            self.draw_accent_line()
            self.after(50, animate)  # ~20 FPS
        
        animate()