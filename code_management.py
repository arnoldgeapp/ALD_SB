import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import os
import math

# Import enhanced data functions
import sys
sys.path.append('utils')
from enhanced_file_io import (
    load_enhanced_codes, save_enhanced_codes,
    get_categories, get_subcategories, 
    get_category_colors, toggle_code_favorite
)

class CodeManagementScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg='#0f1419')
        self.controller = controller
        
        # Animation variables
        self.animation_frame = 0
        
        # Load enhanced codes data
        self.codes_df = load_enhanced_codes()
        self.selected_code_index = None
        self.category_colors = get_category_colors()
        
        self.create_background()
        self.create_content()
        self.start_animations()

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
        
        # Add floating geometric shapes
        self.draw_floating_shapes(width, height)
    
    def draw_floating_shapes(self, width, height):
        """Draw animated floating geometric shapes"""
        shapes = [
            {'type': 'circle', 'x': 0.1, 'y': 0.25, 'size': 55, 'color': '#10b981', 'speed': 0.5},
            {'type': 'circle', 'x': 0.9, 'y': 0.65, 'size': 75, 'color': '#059669', 'speed': 0.7},
            {'type': 'rect', 'x': 0.85, 'y': 0.1, 'size': 40, 'color': '#047857', 'speed': 0.4},
            {'type': 'rect', 'x': 0.05, 'y': 0.9, 'size': 50, 'color': '#065f46', 'speed': 0.6},
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
                                relwidth=0.90, relheight=0.95)  # Bigger for new fields
        
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
        
        # Footer
        self.create_footer()
    
    def create_header(self):
        """Create animated header section"""
        header_frame = tk.Frame(self.content_frame, bg='#1e293b')
        header_frame.pack(pady=(30, 20))
        
        # Main title
        title_label = tk.Label(header_frame,
                              text="Enhanced Code Management",
                              font=('Segoe UI', 32, 'bold'),
                              fg='#ffffff',
                              bg='#1e293b')
        title_label.pack()
        
        # Subtitle with stats
        categories = get_categories()
        favorites_count = len(self.codes_df[self.codes_df['DefaultFavorite'] == True])
        subtitle_text = f"Manage {len(self.codes_df)} codes • {len(categories)} categories • {favorites_count} favorites"
        
        subtitle_label = tk.Label(header_frame,
                                 text=subtitle_text,
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
                    color = '#10b981'
                elif intensity > 0.5:
                    color = '#059669'
                else:
                    color = '#047857'
                
                self.accent_canvas.create_line(i, 1, i+1, 1, fill=color, width=2)
    
    def create_main_content(self):
        """Create main content area with codes list and enhanced input fields"""
        main_container = tk.Frame(self.content_frame, bg='#1e293b')
        main_container.pack(expand=True, fill='both', padx=40, pady=20)
        
        # Create two-column layout
        left_panel = tk.Frame(main_container, bg='#1e293b')
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 20))
        
        right_panel = tk.Frame(main_container, bg='#1e293b')
        right_panel.pack(side='left', fill='both', padx=(20, 0))
        
        # Left panel - Codes list
        self.create_codes_list_panel(left_panel)
        
        # Right panel - Enhanced input fields and actions
        self.create_enhanced_action_panel(right_panel)
    
    def create_codes_list_panel(self, parent):
        """Create the codes list panel with enhanced filtering"""
        # Panel card
        list_card = tk.Frame(parent, bg='#2d3748', relief='ridge', bd=1)
        list_card.pack(fill='both', expand=True)
        
        # Panel header
        header_frame = tk.Frame(list_card, bg='#2d3748')
        header_frame.pack(fill='x', padx=20, pady=(20, 10))
        
        codes_label = tk.Label(header_frame,
                              text="🔤 Code List",
                              font=('Segoe UI', 16, 'bold'),
                              fg='#ffffff',
                              bg='#2d3748')
        codes_label.pack(side='left')
        
        # Codes count
        self.codes_count_label = tk.Label(header_frame,
                                         text=f"({len(self.codes_df)} codes)",
                                         font=('Segoe UI', 11),
                                         fg='#64748b',
                                         bg='#2d3748')
        self.codes_count_label.pack(side='left', padx=(10, 0))
        
        # Enhanced filters frame
        filters_frame = tk.Frame(list_card, bg='#2d3748')
        filters_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        # Search frame
        search_frame = tk.Frame(filters_frame, bg='#2d3748')
        search_frame.pack(fill='x', pady=(0, 5))
        
        search_label = tk.Label(search_frame,
                               text="🔍",
                               font=('Segoe UI', 12),
                               fg='#94a3b8',
                               bg='#2d3748')
        search_label.pack(side='left')
        
        self.search_entry = tk.Entry(search_frame,
                                    font=('Segoe UI', 11),
                                    bg='#1e293b',
                                    fg='#ffffff',
                                    relief='flat',
                                    insertbackground='#ffffff')
        self.search_entry.pack(side='left', fill='x', expand=True, padx=(10, 0), ipady=5)
        self.search_entry.bind('<KeyRelease>', self.filter_codes)
        
        # Category filter frame
        category_frame = tk.Frame(filters_frame, bg='#2d3748')
        category_frame.pack(fill='x', pady=(5, 0))
        
        tk.Label(category_frame,
                text="📂 Category:",
                font=('Segoe UI', 10),
                fg='#94a3b8',
                bg='#2d3748').pack(side='left')
        
        self.filter_category_var = tk.StringVar(value="All")
        self.filter_category_combo = ttk.Combobox(category_frame,
                                                 textvariable=self.filter_category_var,
                                                 width=20,
                                                 state="readonly")
        self.filter_category_combo.pack(side='left', padx=(10, 0))
        self.filter_category_combo.bind('<<ComboboxSelected>>', self.filter_codes)
        
        # Favorites filter
        self.favorites_only_var = tk.BooleanVar()
        favorites_check = tk.Checkbutton(
            category_frame,
            text="⭐ Favorites Only",
            variable=self.favorites_only_var,
            command=self.filter_codes,
            font=('Segoe UI', 10),
            fg='#94a3b8',
            bg='#2d3748',
            selectcolor='#1e293b',
            activebackground='#2d3748',
            activeforeground='#ffffff'
        )
        favorites_check.pack(side='right')
        
        # Listbox container
        listbox_container = tk.Frame(list_card, bg='#1e293b', relief='groove', bd=1)
        listbox_container.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(listbox_container)
        v_scrollbar.pack(side='right', fill='y')
        
        h_scrollbar = ttk.Scrollbar(listbox_container, orient='horizontal')
        h_scrollbar.pack(side='bottom', fill='x')
        
        # Enhanced codes listbox
        self.codes_listbox = tk.Listbox(
            listbox_container,
            font=('Segoe UI', 10),
            bg='#1e293b',
            fg='#ffffff',
            selectbackground='#10b981',
            selectforeground='#ffffff',
            relief='flat',
            highlightthickness=0,
            activestyle='none',
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set
        )
        self.codes_listbox.pack(side='left', fill='both', expand=True)
        v_scrollbar.config(command=self.codes_listbox.yview)
        h_scrollbar.config(command=self.codes_listbox.xview)
        self.codes_listbox.bind('<<ListboxSelect>>', self.on_code_select)
        
        # Load initial data
        self.refresh_filter_options()
        self.refresh_codes_list()
    
    def create_enhanced_action_panel(self, parent):
        """Create the enhanced action panel with all new fields"""
        # Panel card
        action_card = tk.Frame(parent, bg='#2d3748', relief='ridge', bd=1)
        action_card.pack(fill='both')
        
        # Panel content with scrolling for many fields
        canvas_frame = tk.Frame(action_card, bg='#2d3748')
        canvas_frame.pack(fill='both', expand=True, padx=30, pady=20)
        
        # Title
        title_label = tk.Label(canvas_frame,
                              text="Enhanced Code Editor",
                              font=('Segoe UI', 18, 'bold'),
                              fg='#ffffff',
                              bg='#2d3748')
        title_label.pack(pady=(0, 20))
        
        # Create scrollable content
        self.create_input_fields(canvas_frame)
        
        # Action buttons at bottom
        self.create_action_buttons(canvas_frame)
    
    def create_input_fields(self, parent):
        """Create all input fields for enhanced code management"""
        # Code input
        code_frame = tk.Frame(parent, bg='#2d3748')
        code_frame.pack(fill='x', pady=8)
        
        tk.Label(code_frame,
                text="Code:",
                font=('Segoe UI', 12, 'bold'),
                fg='#94a3b8',
                bg='#2d3748',
                width=12,
                anchor='w').pack(side='left')
        
        self.code_entry = tk.Entry(code_frame,
                                  font=('Segoe UI', 12),
                                  bg='#1e293b',
                                  fg='#ffffff',
                                  relief='flat',
                                  insertbackground='#ffffff')
        self.code_entry.pack(side='left', fill='x', expand=True, ipady=6)
        
        # Description input
        desc_frame = tk.Frame(parent, bg='#2d3748')
        desc_frame.pack(fill='x', pady=8)
        
        tk.Label(desc_frame,
                text="Description:",
                font=('Segoe UI', 12, 'bold'),
                fg='#94a3b8',
                bg='#2d3748',
                width=12,
                anchor='w').pack(side='left')
        
        self.desc_entry = tk.Entry(desc_frame,
                                  font=('Segoe UI', 12),
                                  bg='#1e293b',
                                  fg='#ffffff',
                                  relief='flat',
                                  insertbackground='#ffffff')
        self.desc_entry.pack(side='left', fill='x', expand=True, ipady=6)
        
        # Category selection
        category_frame = tk.Frame(parent, bg='#2d3748')
        category_frame.pack(fill='x', pady=8)
        
        tk.Label(category_frame,
                text="Category:",
                font=('Segoe UI', 12, 'bold'),
                fg='#94a3b8',
                bg='#2d3748',
                width=12,
                anchor='w').pack(side='left')
        
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(category_frame,
                                          textvariable=self.category_var,
                                          font=('Segoe UI', 12),
                                          width=25)
        self.category_combo.pack(side='left', fill='x', expand=True)
        self.category_combo.bind('<<ComboboxSelected>>', self.on_category_change)
        
        # SubCategory selection
        subcategory_frame = tk.Frame(parent, bg='#2d3748')
        subcategory_frame.pack(fill='x', pady=8)
        
        tk.Label(subcategory_frame,
                text="SubCategory:",
                font=('Segoe UI', 12, 'bold'),
                fg='#94a3b8',
                bg='#2d3748',
                width=12,
                anchor='w').pack(side='left')
        
        self.subcategory_var = tk.StringVar()
        self.subcategory_combo = ttk.Combobox(subcategory_frame,
                                             textvariable=self.subcategory_var,
                                             font=('Segoe UI', 12),
                                             width=25)
        self.subcategory_combo.pack(side='left', fill='x', expand=True)
        
        # Favorite checkbox with visual indicator
        favorite_frame = tk.Frame(parent, bg='#2d3748')
        favorite_frame.pack(fill='x', pady=8)
        
        tk.Label(favorite_frame,
                text="Favorite:",
                font=('Segoe UI', 12, 'bold'),
                fg='#94a3b8',
                bg='#2d3748',
                width=12,
                anchor='w').pack(side='left')
        
        self.favorite_var = tk.BooleanVar()
        self.favorite_check = tk.Checkbutton(
            favorite_frame,
            text="⭐ Mark as Favorite",
            variable=self.favorite_var,
            font=('Segoe UI', 12),
            fg='#fbbf24',
            bg='#2d3748',
            selectcolor='#1e293b',
            activebackground='#2d3748',
            activeforeground='#fbbf24'
        )
        self.favorite_check.pack(side='left')
        
        # Notes text area
        notes_frame = tk.Frame(parent, bg='#2d3748')
        notes_frame.pack(fill='both', expand=True, pady=8)
        
        tk.Label(notes_frame,
                text="Notes:",
                font=('Segoe UI', 12, 'bold'),
                fg='#94a3b8',
                bg='#2d3748').pack(anchor='w')
        
        # Notes text widget with scrollbar
        notes_container = tk.Frame(notes_frame, bg='#1e293b', relief='groove', bd=1)
        notes_container.pack(fill='both', expand=True, pady=(5, 0))
        
        notes_scrollbar = ttk.Scrollbar(notes_container)
        notes_scrollbar.pack(side='right', fill='y')
        
        self.notes_text = tk.Text(notes_container,
                                 font=('Segoe UI', 10),
                                 bg='#1e293b',
                                 fg='#ffffff',
                                 relief='flat',
                                 height=6,
                                 wrap='word',
                                 insertbackground='#ffffff',
                                 yscrollcommand=notes_scrollbar.set)
        self.notes_text.pack(side='left', fill='both', expand=True)
        notes_scrollbar.config(command=self.notes_text.yview)
        
        # Load dropdown options
        self.load_category_options()
    
    def create_action_buttons(self, parent):
        """Create enhanced action buttons"""
        buttons_frame = tk.Frame(parent, bg='#2d3748')
        buttons_frame.pack(pady=(20, 0))
        
        button_configs = [
            {'text': '➕ Add Code', 'command': self.add_code, 'color': '#10b981'},
            {'text': '💾 Update Code', 'command': self.update_code, 'color': '#3b82f6'},
            {'text': '🗑️ Delete Code', 'command': self.delete_code, 'color': '#ef4444'},
            {'text': '🔄 Clear Fields', 'command': self.clear_fields, 'color': '#8b5cf6'},
        ]
        
        for config in button_configs:
            btn = tk.Button(
                buttons_frame,
                text=config['text'],
                command=config['command'],
                font=('Segoe UI', 11),
                bg=config['color'],
                fg='#ffffff',
                relief='flat',
                cursor='hand2',
                padx=20,
                pady=10,
                width=18
            )
            btn.pack(pady=3)
            
            # Hover effects
            def on_enter(event, button=btn, color=config['color']):
                r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
                darker = f"#{max(0, r-20):02x}{max(0, g-20):02x}{max(0, b-20):02x}"
                button.config(bg=darker)
            
            def on_leave(event, button=btn, color=config['color']):
                button.config(bg=color)
            
            btn.bind('<Enter>', on_enter)
            btn.bind('<Leave>', on_leave)
    
    def load_category_options(self):
        """Load category and subcategory options"""
        categories = get_categories()
        category_names = [cat['name'] for cat in categories]
        
        self.category_combo['values'] = category_names
        
        # Set default if empty
        if not self.category_var.get() and category_names:
            self.category_var.set(category_names[0])
            self.on_category_change()
    
    def on_category_change(self, event=None):
        """Update subcategories when category changes"""
        selected_category = self.category_var.get()
        if selected_category:
            subcategories = get_subcategories(selected_category)
            self.subcategory_combo['values'] = subcategories
            if subcategories:
                self.subcategory_var.set(subcategories[0])
    
    def refresh_filter_options(self):
        """Refresh filter dropdown options"""
        categories = get_categories()
        category_names = ["All"] + [cat['name'] for cat in categories]
        self.filter_category_combo['values'] = category_names
    
    def refresh_codes_list(self):
        """Refresh the codes listbox with enhanced display"""
        self.codes_listbox.delete(0, tk.END)
        
        # Get current filters
        search_term = self.search_entry.get().lower()
        filter_category = self.filter_category_var.get()
        favorites_only = self.favorites_only_var.get()
        
        # Filter codes
        filtered_df = self.codes_df.copy()
        
        if search_term:
            mask = (
                filtered_df['Code'].astype(str).str.lower().str.contains(search_term, na=False) |
                filtered_df['Description'].astype(str).str.lower().str.contains(search_term, na=False) |
                filtered_df['Notes'].astype(str).str.lower().str.contains(search_term, na=False)
            )
            filtered_df = filtered_df[mask]
        
        if filter_category != "All":
            filtered_df = filtered_df[filtered_df['Category'] == filter_category]
        
        if favorites_only:
            filtered_df = filtered_df[filtered_df['DefaultFavorite'] == True]
        
        # Add codes to listbox with enhanced display
        for idx, row in filtered_df.iterrows():
            code = str(row['Code'])
            desc = str(row['Description'])
            category = str(row.get('Category', 'Unknown'))
            is_favorite = row.get('DefaultFavorite', False)
            
            # Create enhanced display text
            favorite_star = "⭐ " if is_favorite else ""
            category_badge = f"[{category[:8]}]"
            display_text = f"{favorite_star}{code} - {desc} {category_badge}"
            
            self.codes_listbox.insert(tk.END, display_text)
        
        self.codes_count_label.config(text=f"({len(filtered_df)} codes)")
    
    def filter_codes(self, event=None):
        """Filter codes based on current criteria"""
        self.refresh_codes_list()
    
    def on_code_select(self, event):
        """Handle code selection from listbox"""
        try:
            selection = self.codes_listbox.curselection()
            if selection:
                index = selection[0]
                selected_text = self.codes_listbox.get(index)
                
                # Extract code from display text (remove favorite star and category)
                display_parts = selected_text.replace("⭐ ", "").split(" - ")
                code_part = display_parts[0]
                
                # Find the actual index in the dataframe
                mask = self.codes_df['Code'].astype(str) == code_part
                if mask.any():
                    self.selected_code_index = self.codes_df[mask].index[0]
                    row = self.codes_df.loc[self.selected_code_index]
                    
                    # Populate all fields
                    self.code_entry.delete(0, tk.END)
                    self.code_entry.insert(0, str(row['Code']))
                    
                    self.desc_entry.delete(0, tk.END)
                    self.desc_entry.insert(0, str(row['Description']))
                    
                    self.category_var.set(str(row.get('Category', '')))
                    self.on_category_change()  # Update subcategories
                    
                    self.subcategory_var.set(str(row.get('SubCategory', '')))
                    
                    self.favorite_var.set(row.get('DefaultFavorite', False))
                    
                    self.notes_text.delete('1.0', tk.END)
                    notes = str(row.get('Notes', ''))
                    if notes and notes != 'nan':
                        self.notes_text.insert('1.0', notes)
        except Exception as e:
            print(f"Selection error: {e}")
    
    def add_code(self):
        """Add a new code with all enhanced fields"""
        code = self.code_entry.get().strip()
        desc = self.desc_entry.get().strip()
        category = self.category_var.get()
        subcategory = self.subcategory_var.get()
        is_favorite = self.favorite_var.get()
        notes = self.notes_text.get('1.0', tk.END).strip()
        
        if not code:
            messagebox.showwarning("Missing Code", "Please enter a code.")
            return
        
        # Check for duplicate
        if code in self.codes_df['Code'].values:
            messagebox.showwarning("Duplicate Code", "This code already exists.")
            return
        
        # Add new code with all fields
        new_row = {
            'Code': code,
            'Description': desc,
            'Category': category,
            'SubCategory': subcategory,
            'DefaultFavorite': is_favorite,
            'Notes': notes
        }
        
        new_df = pd.DataFrame([new_row])
        self.codes_df = pd.concat([self.codes_df, new_df], ignore_index=True)
        
        # Sort by code
        self.codes_df = self.codes_df.sort_values('Code').reset_index(drop=True)
        
        # Save enhanced codes
        save_enhanced_codes(self.codes_df)
        
        self.refresh_codes_list()
        self.clear_fields()
        
        messagebox.showinfo("Success", f"Code '{code}' added successfully with enhanced details.")
    
    def update_code(self):
        """Update selected code with all enhanced fields"""
        if self.selected_code_index is None:
            messagebox.showwarning("No Selection", "Please select a code to update.")
            return
        
        code = self.code_entry.get().strip()
        desc = self.desc_entry.get().strip()
        category = self.category_var.get()
        subcategory = self.subcategory_var.get()
        is_favorite = self.favorite_var.get()
        notes = self.notes_text.get('1.0', tk.END).strip()
        
        if not code:
            messagebox.showwarning("Missing Code", "Please enter a code.")
            return
        
        # Check if changing code to a duplicate
        old_code = str(self.codes_df.loc[self.selected_code_index, 'Code'])
        if code != old_code and code in self.codes_df['Code'].values:
            messagebox.showwarning("Duplicate Code", "This code already exists.")
            return
        
        # Update all fields
        self.codes_df.loc[self.selected_code_index, 'Code'] = code
        self.codes_df.loc[self.selected_code_index, 'Description'] = desc
        self.codes_df.loc[self.selected_code_index, 'Category'] = category
        self.codes_df.loc[self.selected_code_index, 'SubCategory'] = subcategory
        self.codes_df.loc[self.selected_code_index, 'DefaultFavorite'] = is_favorite
        self.codes_df.loc[self.selected_code_index, 'Notes'] = notes
        
        # Resort
        self.codes_df = self.codes_df.sort_values('Code').reset_index(drop=True)
        
        # Save enhanced codes
        save_enhanced_codes(self.codes_df)
        
        self.refresh_codes_list()
        
        messagebox.showinfo("Success", "Code updated successfully with enhanced details.")
    
    def delete_code(self):
        """Delete selected code"""
        if self.selected_code_index is None:
            messagebox.showwarning("No Selection", "Please select a code to delete.")
            return
        
        code = str(self.codes_df.loc[self.selected_code_index, 'Code'])
        
        confirm = messagebox.askyesno("Delete Code", 
                                     f"Are you sure you want to delete code '{code}'?")
        
        if confirm:
            self.codes_df = self.codes_df.drop(self.selected_code_index).reset_index(drop=True)
            save_enhanced_codes(self.codes_df)
            self.refresh_codes_list()
            self.clear_fields()
            self.selected_code_index = None
            
            messagebox.showinfo("Success", "Code deleted successfully.")
    
    def clear_fields(self):
        """Clear all input fields"""
        self.code_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.category_var.set('')
        self.subcategory_var.set('')
        self.favorite_var.set(False)
        self.notes_text.delete('1.0', tk.END)
        self.selected_code_index = None
        self.codes_listbox.selection_clear(0, tk.END)
    
    def create_footer(self):
        """Create footer with stats and back button"""
        footer_frame = tk.Frame(self.content_frame, bg='#1e293b')
        footer_frame.pack(side='bottom', fill='x', pady=(10, 20))
        
        # Stats
        categories = get_categories()
        favorites_count = len(self.codes_df[self.codes_df['DefaultFavorite'] == True])
        
        stats_label = tk.Label(footer_frame,
                              text=f"💡 Managing {len(self.codes_df)} codes across {len(categories)} categories • {favorites_count} favorites",
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
            self.after(50, animate)  # ~20 FPS
        
        animate()