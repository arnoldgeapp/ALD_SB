import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import os
import math

# Import your enhanced data functions
import sys
sys.path.append('utils')
from enhanced_file_io import (
    load_enhanced_codes, save_enhanced_codes,
    get_categories, get_subcategories, 
    get_codes_by_category, toggle_code_favorite,
    get_favorite_codes, update_code_notes,
    search_codes, get_category_colors
)

class EnhancedCodeBrowserScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg='#0f1419')
        self.controller = controller
        
        # Animation variables
        self.animation_frame = 0
        
        # Data state
        self.codes_df = load_enhanced_codes()
        self.selected_category = "All"
        self.selected_subcategory = "All"
        self.search_term = ""
        self.show_favorites_only = False
        self.selected_code = None
        
        # Get category colors
        self.category_colors = get_category_colors()
        
        self.create_background()
        self.create_content()
        self.start_animations()
        self.load_initial_data()

    def create_background(self):
        """Create animated gradient background"""
        self.bg_canvas = tk.Canvas(self, highlightthickness=0)
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        self.bg_canvas.bind('<Configure>', self.on_canvas_resize)
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
            
            wave = math.sin(progress * math.pi + time_offset) * 0.1
            
            r = int(r1 + (r2 - r1) * (progress + wave))
            g = int(g1 + (g2 - g1) * (progress + wave))
            b = int(b1 + (b2 - b1) * (progress + wave))
            
            color = f"#{r:02x}{g:02x}{b:02x}"
            
            y = i * height // gradient_steps
            next_y = (i + 1) * height // gradient_steps
            
            self.bg_canvas.create_rectangle(0, y, width, next_y, 
                                          fill=color, outline=color)
        
        # Add floating shapes for visual appeal
        shapes = [
            {'type': 'circle', 'x': 0.1, 'y': 0.25, 'size': 55, 'color': '#10b981', 'speed': 0.5},
            {'type': 'circle', 'x': 0.9, 'y': 0.65, 'size': 75, 'color': '#059669', 'speed': 0.7},
            {'type': 'rect', 'x': 0.85, 'y': 0.1, 'size': 40, 'color': '#047857', 'speed': 0.4},
            {'type': 'rect', 'x': 0.05, 'y': 0.9, 'size': 50, 'color': '#065f46', 'speed': 0.6},
        ]
        
        for shape in shapes:
            base_x = shape['x'] * width
            base_y = shape['y'] * height
            
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
        self.draw_background()
    
    def create_content(self):
        """Create main content with enhanced categorization"""
        # Main content container
        self.content_frame = tk.Frame(self, bg='#1e293b', relief='ridge', bd=1)
        self.content_frame.place(relx=0.5, rely=0.5, anchor='center', 
                                relwidth=0.95, relheight=0.95)
        
        # Border
        border_frame = tk.Frame(self.content_frame, bg='#334155', height=2)
        border_frame.pack(fill='x')
        
        # Close button
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
        
        # Header
        self.create_header()
        
        # Main content area
        self.create_main_content()
        
        # Footer
        self.create_footer()
    
    def create_header(self):
        """Create enhanced header with category stats"""
        header_frame = tk.Frame(self.content_frame, bg='#1e293b')
        header_frame.pack(pady=(20, 15))
        
        # Title
        title_label = tk.Label(header_frame,
                              text="Enhanced Code Browser",
                              font=('Segoe UI', 28, 'bold'),
                              fg='#ffffff',
                              bg='#1e293b')
        title_label.pack()
        
        # Subtitle with stats
        categories = get_categories()
        favorites = get_favorite_codes()
        stats_text = f"Browse {len(self.codes_df)} codes • {len(categories)} categories • {len(favorites)} favorites"
        
        self.subtitle_label = tk.Label(header_frame,
                                      text=stats_text,
                                      font=('Segoe UI', 12),
                                      fg='#94a3b8',
                                      bg='#1e293b')
        self.subtitle_label.pack(pady=(5, 0))
        
        # Animated accent line
        accent_canvas = tk.Canvas(header_frame, width=200, height=3,
                                 bg='#1e293b', highlightthickness=0)
        accent_canvas.pack(pady=10)
        self.accent_canvas = accent_canvas
        self.draw_accent_line()
    
    def draw_accent_line(self):
        """Draw animated accent line"""
        self.accent_canvas.delete("all")
        
        width = 200
        progress = (math.sin(self.animation_frame * 0.03) + 1) / 2
        
        for i in range(width):
            x_progress = i / width
            intensity = progress * (1 - abs(x_progress - 0.5) * 2)
            
            if intensity > 0.1:
                if intensity > 0.8:
                    color = '#10b981'
                elif intensity > 0.5:
                    color = '#059669'
                else:
                    color = '#047857'
                
                self.accent_canvas.create_line(i, 1, i+1, 1, fill=color, width=2)
    
    def create_main_content(self):
        """Create three-panel layout: Categories | Codes | Details"""
        main_container = tk.Frame(self.content_frame, bg='#1e293b')
        main_container.pack(expand=True, fill='both', padx=20, pady=15)
        
        # Configure grid
        main_container.grid_columnconfigure(0, weight=0, minsize=280)  # Categories panel
        main_container.grid_columnconfigure(1, weight=1, minsize=400)  # Codes panel
        main_container.grid_columnconfigure(2, weight=0, minsize=300)  # Details panel
        main_container.grid_rowconfigure(0, weight=1)
        
        # Create panels
        self.create_categories_panel(main_container)
        self.create_codes_panel(main_container)
        self.create_details_panel(main_container)
    
    def create_categories_panel(self, parent):
        """Create hierarchical categories panel"""
        categories_card = tk.Frame(parent, bg='#2d3748', relief='ridge', bd=1)
        categories_card.grid(row=0, column=0, sticky='nsew', padx=(0, 10))
        
        # Header
        header_frame = tk.Frame(categories_card, bg='#2d3748')
        header_frame.pack(fill='x', padx=15, pady=(15, 10))
        
        categories_label = tk.Label(header_frame,
                                   text="🏷️ Categories",
                                   font=('Segoe UI', 14, 'bold'),
                                   fg='#ffffff',
                                   bg='#2d3748')
        categories_label.pack(side='left')
        
        # Favorites toggle
        self.favorites_var = tk.BooleanVar()
        favorites_check = tk.Checkbutton(
            header_frame,
            text="⭐ Favorites",
            variable=self.favorites_var,
            command=self.toggle_favorites_filter,
            font=('Segoe UI', 9),
            fg='#94a3b8',
            bg='#2d3748',
            selectcolor='#1e293b',
            activebackground='#2d3748',
            activeforeground='#ffffff'
        )
        favorites_check.pack(side='right')
        
        # Search frame
        search_frame = tk.Frame(categories_card, bg='#2d3748')
        search_frame.pack(fill='x', padx=15, pady=(0, 10))
        
        tk.Label(search_frame,
                text="🔍",
                font=('Segoe UI', 12),
                fg='#94a3b8',
                bg='#2d3748').pack(side='left')
        
        self.search_entry = tk.Entry(search_frame,
                                    font=('Segoe UI', 10),
                                    bg='#1e293b',
                                    fg='#ffffff',
                                    relief='flat',
                                    insertbackground='#ffffff')
        self.search_entry.pack(side='left', fill='x', expand=True, padx=(10, 0), ipady=4)
        self.search_entry.bind('<KeyRelease>', self.on_search_change)
        
        # Categories tree
        tree_frame = tk.Frame(categories_card, bg='#1e293b', relief='groove', bd=1)
        tree_frame.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        # Scrollbar for tree
        tree_scrollbar = ttk.Scrollbar(tree_frame)
        tree_scrollbar.pack(side='right', fill='y')
        
        # Categories listbox
        self.categories_listbox = tk.Listbox(
            tree_frame,
            font=('Segoe UI', 10),
            bg='#1e293b',
            fg='#ffffff',
            selectbackground='#3b82f6',
            selectforeground='#ffffff',
            relief='flat',
            highlightthickness=0,
            activestyle='none',
            yscrollcommand=tree_scrollbar.set
        )
        self.categories_listbox.pack(side='left', fill='both', expand=True)
        tree_scrollbar.config(command=self.categories_listbox.yview)
        self.categories_listbox.bind('<<ListboxSelect>>', self.on_category_select)
    
    def create_codes_panel(self, parent):
        """Create codes grid panel"""
        codes_card = tk.Frame(parent, bg='#2d3748', relief='ridge', bd=1)
        codes_card.grid(row=0, column=1, sticky='nsew', padx=5)
        
        # Header
        header_frame = tk.Frame(codes_card, bg='#2d3748')
        header_frame.pack(fill='x', padx=15, pady=(15, 10))
        
        self.codes_title_label = tk.Label(header_frame,
                                         text="🔤 All Codes",
                                         font=('Segoe UI', 14, 'bold'),
                                         fg='#ffffff',
                                         bg='#2d3748')
        self.codes_title_label.pack(side='left')
        
        self.codes_count_label = tk.Label(header_frame,
                                         text="(0 codes)",
                                         font=('Segoe UI', 10),
                                         fg='#64748b',
                                         bg='#2d3748')
        self.codes_count_label.pack(side='left', padx=(10, 0))
        
        # Codes grid container
        codes_container = tk.Frame(codes_card, bg='#2d3748')
        codes_container.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        # Canvas for scrolling codes grid
        self.codes_canvas = tk.Canvas(codes_container, bg='#2d3748', highlightthickness=0)
        codes_scrollbar = ttk.Scrollbar(codes_container, orient='vertical', command=self.codes_canvas.yview)
        self.codes_canvas.configure(yscrollcommand=codes_scrollbar.set)
        
        codes_scrollbar.pack(side='right', fill='y')
        self.codes_canvas.pack(side='left', fill='both', expand=True)
        
        self.codes_grid_frame = tk.Frame(self.codes_canvas, bg='#2d3748')
        self.codes_canvas_window = self.codes_canvas.create_window(0, 0, anchor='nw', window=self.codes_grid_frame)
        
        self.codes_canvas.bind('<Configure>', self.on_codes_canvas_configure)
        self.codes_grid_frame.bind('<Configure>', self.on_codes_grid_configure)
    
    def create_details_panel(self, parent):
        """Create code details and notes panel"""
        details_card = tk.Frame(parent, bg='#2d3748', relief='ridge', bd=1)
        details_card.grid(row=0, column=2, sticky='nsew', padx=(10, 0))
        
        # Header
        header_frame = tk.Frame(details_card, bg='#2d3748')
        header_frame.pack(fill='x', padx=15, pady=(15, 10))
        
        details_label = tk.Label(header_frame,
                                text="📋 Code Details",
                                font=('Segoe UI', 14, 'bold'),
                                fg='#ffffff',
                                bg='#2d3748')
        details_label.pack()
        
        # Content frame
        self.details_content_frame = tk.Frame(details_card, bg='#2d3748')
        self.details_content_frame.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        # Initially show "Select a code" message
        self.show_no_selection_message()
    
    def show_no_selection_message(self):
        """Show message when no code is selected"""
        for widget in self.details_content_frame.winfo_children():
            widget.destroy()
        
        message_label = tk.Label(self.details_content_frame,
                                text="👆 Select a code to view details\n\n🏷️  Browse categories\n⭐ Toggle favorites\n🔍 Search codes",
                                font=('Segoe UI', 11),
                                fg='#64748b',
                                bg='#2d3748',
                                justify='center')
        message_label.pack(pady=50)
    
    def show_code_details(self, code_row):
        """Show details for selected code"""
        for widget in self.details_content_frame.winfo_children():
            widget.destroy()
        
        # Code number (large)
        code_label = tk.Label(self.details_content_frame,
                             text=str(code_row['Code']),
                             font=('Segoe UI', 18, 'bold'),
                             fg='#3b82f6',
                             bg='#2d3748')
        code_label.pack(pady=(0, 10))
        
        # Favorite button
        favorite_frame = tk.Frame(self.details_content_frame, bg='#2d3748')
        favorite_frame.pack(fill='x', pady=(0, 15))
        
        is_favorite = code_row.get('DefaultFavorite', False)
        favorite_text = "⭐ Remove from Favorites" if is_favorite else "☆ Add to Favorites"
        favorite_color = '#fbbf24' if is_favorite else '#64748b'
        
        self.favorite_btn = tk.Button(
            favorite_frame,
            text=favorite_text,
            command=lambda: self.toggle_favorite(code_row['Code']),
            font=('Segoe UI', 9),
            bg=favorite_color,
            fg='#ffffff',
            relief='flat',
            cursor='hand2',
            pady=5
        )
        self.favorite_btn.pack(fill='x')
        
        # Category info
        category_frame = tk.Frame(self.details_content_frame, bg='#1e293b', relief='ridge', bd=1)
        category_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(category_frame,
                text="Category:",
                font=('Segoe UI', 9, 'bold'),
                fg='#94a3b8',
                bg='#1e293b').pack(anchor='w', padx=10, pady=(8, 2))
        
        category_color = self.category_colors.get(code_row.get('Category', ''), '#3b82f6')
        tk.Label(category_frame,
                text=str(code_row.get('Category', 'Unknown')),
                font=('Segoe UI', 10),
                fg=category_color,
                bg='#1e293b').pack(anchor='w', padx=10)
        
        tk.Label(category_frame,
                text="Subcategory:",
                font=('Segoe UI', 9, 'bold'),
                fg='#94a3b8',
                bg='#1e293b').pack(anchor='w', padx=10, pady=(5, 2))
        
        tk.Label(category_frame,
                text=str(code_row.get('SubCategory', 'General')),
                font=('Segoe UI', 10),
                fg='#ffffff',
                bg='#1e293b').pack(anchor='w', padx=10, pady=(0, 8))
        
        # Description
        desc_frame = tk.Frame(self.details_content_frame, bg='#1e293b', relief='ridge', bd=1)
        desc_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(desc_frame,
                text="Description:",
                font=('Segoe UI', 9, 'bold'),
                fg='#94a3b8',
                bg='#1e293b').pack(anchor='w', padx=10, pady=(8, 2))
        
        desc_text = str(code_row.get('Description', 'No description'))
        desc_label = tk.Label(desc_frame,
                             text=desc_text,
                             font=('Segoe UI', 10),
                             fg='#ffffff',
                             bg='#1e293b',
                             wraplength=250,
                             justify='left')
        desc_label.pack(anchor='w', padx=10, pady=(0, 8))
        
        # Notes section
        notes_frame = tk.Frame(self.details_content_frame, bg='#1e293b', relief='ridge', bd=1)
        notes_frame.pack(fill='both', expand=True)
        
        tk.Label(notes_frame,
                text="Notes:",
                font=('Segoe UI', 9, 'bold'),
                fg='#94a3b8',
                bg='#1e293b').pack(anchor='w', padx=10, pady=(8, 2))
        
        # Notes text widget
        self.notes_text = tk.Text(notes_frame,
                                 font=('Segoe UI', 9),
                                 bg='#374151',
                                 fg='#ffffff',
                                 relief='flat',
                                 height=6,
                                 wrap='word',
                                 insertbackground='#ffffff')
        self.notes_text.pack(fill='both', expand=True, padx=10, pady=(0, 5))
        
        # Pre-fill notes
        current_notes = str(code_row.get('Notes', ''))
        if current_notes and current_notes != 'nan':
            self.notes_text.insert('1.0', current_notes)
        
        # Save notes button
        save_notes_btn = tk.Button(
            notes_frame,
            text="💾 Save Notes",
            command=lambda: self.save_notes(code_row['Code']),
            font=('Segoe UI', 9),
            bg='#10b981',
            fg='#ffffff',
            relief='flat',
            cursor='hand2',
            pady=4
        )
        save_notes_btn.pack(fill='x', padx=10, pady=(0, 8))
    
    def load_initial_data(self):
        """Load initial categories and codes"""
        self.refresh_categories_list()
        self.refresh_codes_display()
    
    def refresh_categories_list(self):
        """Refresh the categories list"""
        self.categories_listbox.delete(0, tk.END)
        
        # Add "All Categories" option
        self.categories_listbox.insert(tk.END, "📁 All Categories")
        
        # Add main categories with counts
        categories = get_categories()
        for category in categories:
            count = category['count']
            display_text = f"📂 {category['name']} ({count})"
            self.categories_listbox.insert(tk.END, display_text)
            
            # Add subcategories (indented)
            subcategories = get_subcategories(category['name'])
            for subcat in subcategories:
                subcat_codes = get_codes_by_category(category['name'], subcat)
                subcat_count = len(subcat_codes)
                subcat_display = f"   └── {subcat} ({subcat_count})"
                self.categories_listbox.insert(tk.END, subcat_display)
    
    def on_category_select(self, event):
        """Handle category selection"""
        selection = self.categories_listbox.curselection()
        if not selection:
            return
        
        selected_text = self.categories_listbox.get(selection[0])
        
        if selected_text.startswith("📁 All Categories"):
            self.selected_category = "All"
            self.selected_subcategory = "All"
        elif selected_text.startswith("📂"):
            # Main category selected
            category_name = selected_text.split(" (")[0].replace("📂 ", "")
            self.selected_category = category_name
            self.selected_subcategory = "All"
        elif selected_text.startswith("   └──"):
            # Subcategory selected - need to find parent category
            subcat_name = selected_text.split(" (")[0].replace("   └── ", "")
            self.selected_subcategory = subcat_name
            # Find parent category (look up in the list)
            current_index = selection[0]
            while current_index >= 0:
                list_item = self.categories_listbox.get(current_index)
                if list_item.startswith("📂"):
                    self.selected_category = list_item.split(" (")[0].replace("📂 ", "")
                    break
                current_index -= 1
        
        self.refresh_codes_display()
    
    def on_search_change(self, event):
        """Handle search term change"""
        self.search_term = self.search_entry.get()
        self.refresh_codes_display()
    
    def toggle_favorites_filter(self):
        """Toggle favorites-only filter"""
        self.show_favorites_only = self.favorites_var.get()
        self.refresh_codes_display()
    
    def refresh_codes_display(self):
        """Refresh the codes grid display"""
        # Clear existing codes
        for widget in self.codes_grid_frame.winfo_children():
            widget.destroy()
        
        # Get filtered codes
        if self.search_term:
            codes_df = search_codes(
                self.search_term, 
                self.selected_category if self.selected_category != "All" else None,
                self.selected_subcategory if self.selected_subcategory != "All" else None,
                self.show_favorites_only
            )
        else:
            codes_df = get_codes_by_category(
                self.selected_category if self.selected_category != "All" else None,
                self.selected_subcategory if self.selected_subcategory != "All" else None,
                self.show_favorites_only
            )
        
        # Update title and count
        title_parts = []
        if self.show_favorites_only:
            title_parts.append("⭐ Favorites")
        if self.selected_category != "All":
            title_parts.append(f"📂 {self.selected_category}")
            if self.selected_subcategory != "All":
                title_parts.append(f"→ {self.selected_subcategory}")
        
        if not title_parts:
            title = "🔤 All Codes"
        else:
            title = " ".join(title_parts)
        
        self.codes_title_label.config(text=title)
        self.codes_count_label.config(text=f"({len(codes_df)} codes)")
        
        # Create code cards in grid
        if len(codes_df) == 0:
            no_codes_label = tk.Label(self.codes_grid_frame,
                                     text="No codes found matching criteria",
                                     font=('Segoe UI', 11),
                                     fg='#64748b',
                                     bg='#2d3748')
            no_codes_label.pack(pady=30)
        else:
            self.create_codes_grid(codes_df)
        
        # Update scroll region
        self.codes_grid_frame.update_idletasks()
        self.codes_canvas.configure(scrollregion=self.codes_canvas.bbox("all"))
    
    def create_codes_grid(self, codes_df):
        """Create grid of code cards"""
        codes_per_row = 3
        
        for i, (_, code_row) in enumerate(codes_df.iterrows()):
            row_idx = i // codes_per_row
            col_idx = i % codes_per_row
            
            # Configure grid weights
            self.codes_grid_frame.grid_rowconfigure(row_idx, weight=0)
            self.codes_grid_frame.grid_columnconfigure(col_idx, weight=1)
            
            # Create code card
            self.create_code_card(self.codes_grid_frame, code_row, row_idx, col_idx)
    
    def create_code_card(self, parent, code_row, row, col):
        """Create individual code card"""
        # Card frame
        card_bg = '#374151'
        if code_row.get('DefaultFavorite', False):
            card_bg = '#1e40af'  # Blue tint for favorites
        
        card_frame = tk.Frame(parent, bg=card_bg, relief='ridge', bd=1, cursor='hand2')
        card_frame.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
        
        # Card content
        content_frame = tk.Frame(card_frame, bg=card_bg)
        content_frame.pack(fill='both', expand=True, padx=8, pady=8)
        
        # Code number (with favorite star)
        code_text = str(code_row['Code'])
        if code_row.get('DefaultFavorite', False):
            code_text = f"⭐ {code_text}"
        
        code_label = tk.Label(content_frame,
                             text=code_text,
                             font=('Segoe UI', 11, 'bold'),
                             fg='#ffffff',
                             bg=card_bg)
        code_label.pack()
        
        # Category badge
        category = str(code_row.get('Category', 'Unknown'))
        category_color = self.category_colors.get(category, '#64748b')
        
        category_label = tk.Label(content_frame,
                                 text=category[:12] + "..." if len(category) > 12 else category,
                                 font=('Segoe UI', 8),
                                 fg=category_color,
                                 bg=card_bg)
        category_label.pack()
        
        # Description (truncated)
        desc = str(code_row.get('Description', ''))
        if len(desc) > 40:
            desc = desc[:40] + "..."
        
        desc_label = tk.Label(content_frame,
                             text=desc,
                             font=('Segoe UI', 8),
                             fg='#d1d5db',
                             bg=card_bg,
                             wraplength=120,
                             justify='center')
        desc_label.pack(pady=(3, 0))
        
        # Bind click events
        def on_card_click(event, code_data=code_row):
            self.selected_code = code_data
            self.show_code_details(code_data)
        
        def on_card_enter(event):
            hover_bg = '#4b5563'
            card_frame.config(bg=hover_bg)
            content_frame.config(bg=hover_bg)
            code_label.config(bg=hover_bg)
            category_label.config(bg=hover_bg)
            desc_label.config(bg=hover_bg)
        
        def on_card_leave(event):
            card_frame.config(bg=card_bg)
            content_frame.config(bg=card_bg)
            code_label.config(bg=card_bg)
            category_label.config(bg=card_bg)
            desc_label.config(bg=card_bg)
        
        # Bind events to all card components
        for widget in [card_frame, content_frame, code_label, category_label, desc_label]:
            widget.bind('<Button-1>', on_card_click)
            widget.bind('<Enter>', on_card_enter)
            widget.bind('<Leave>', on_card_leave)
    
    def on_codes_canvas_configure(self, event):
        """Handle codes canvas resize"""
        canvas_width = event.width
        self.codes_canvas.itemconfig(self.codes_canvas_window, width=canvas_width)
    
    def on_codes_grid_configure(self, event):
        """Update scroll region when codes grid changes"""
        self.codes_canvas.configure(scrollregion=self.codes_canvas.bbox("all"))
    
    def toggle_favorite(self, code):
        """Toggle favorite status for a code"""
        new_status = toggle_code_favorite(code)
        
        # Refresh the current code details if it's still selected
        if self.selected_code and self.selected_code['Code'] == code:
            # Update the selected code data
            self.codes_df = load_enhanced_codes()  # Reload to get updated data
            updated_code = self.codes_df[self.codes_df['Code'] == code].iloc[0]
            self.selected_code = updated_code
            self.show_code_details(updated_code)
        
        # Refresh the codes display to show updated favorite status
        self.refresh_codes_display()
    
    def save_notes(self, code):
        """Save notes for a code"""
        notes_content = self.notes_text.get('1.0', tk.END).strip()
        
        if update_code_notes(code, notes_content):
            messagebox.showinfo("Success", f"Notes saved for code {code}")
            # Reload data to reflect changes
            self.codes_df = load_enhanced_codes()
        else:
            messagebox.showerror("Error", f"Failed to save notes for code {code}")
    
    def create_footer(self):
        """Create footer with back button"""
        footer_frame = tk.Frame(self.content_frame, bg='#1e293b')
        footer_frame.pack(side='bottom', fill='x', pady=(10, 20))
        
        # Stats
        stats_label = tk.Label(footer_frame,
                              text="💡 Click a code card to view details • Use categories to filter • Star your favorites",
                              font=('Segoe UI', 10),
                              fg='#64748b',
                              bg='#1e293b')
        stats_label.pack()
        
        # Back button
        back_btn = tk.Button(
            footer_frame,
            text='🏠 Back to Main Menu',
            command=lambda: self.controller.show_frame("ModernMainMenu"),
            font=('Segoe UI', 14, 'bold'),
            bg='#475569',
            fg='#ffffff',
            relief='flat',
            cursor='hand2',
            padx=40,
            pady=10
        )
        back_btn.pack(pady=(15, 0))
        
        # Hover effects
        back_btn.bind('<Enter>', lambda e: back_btn.config(bg='#334155'))
        back_btn.bind('<Leave>', lambda e: back_btn.config(bg='#475569'))
    
    def start_animations(self):
        """Start background animations"""
        def animate():
            self.animation_frame += 1
            self.draw_background()
            self.draw_accent_line()
            self.after(50, animate)
        
        animate()