import tkinter as tk
from tkinter import ttk
import math
import time

class ModernMainMenu(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg='#0f1419')
        self.controller = controller
        
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
            # Animated gradient colors
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
            {'type': 'circle', 'x': 0.2, 'y': 0.3, 'size': 60, 'color': '#1e40af', 'speed': 0.5},
            {'type': 'circle', 'x': 0.8, 'y': 0.6, 'size': 80, 'color': '#1d4ed8', 'speed': 0.7},
            {'type': 'circle', 'x': 0.1, 'y': 0.8, 'size': 40, 'color': '#2563eb', 'speed': 0.3},
            {'type': 'rect', 'x': 0.9, 'y': 0.2, 'size': 50, 'color': '#1e40af', 'speed': 0.6},
            {'type': 'rect', 'x': 0.05, 'y': 0.1, 'size': 35, 'color': '#3730a3', 'speed': 0.4},
        ]
        
        for shape in shapes:
            # Calculate animated position
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
            else:  # rectangle
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
                                relwidth=0.7, relheight=0.8)
        
        # Add subtle border
        border_frame = tk.Frame(self.content_frame, bg='#334155', height=2)
        border_frame.pack(fill='x')
        
        # Header section
        self.create_header()
        
        # Navigation cards
        self.create_navigation_cards()
        
        # Footer section
        self.create_footer()
    
    def create_header(self):
        """Create animated header section"""
        header_frame = tk.Frame(self.content_frame, bg='#1e293b')
        header_frame.pack(pady=(50, 30))
        
        # Animated logo/icon
        logo_frame = tk.Frame(header_frame, bg='#1e293b')
        logo_frame.pack(pady=(0, 20))
        
        # Create logo with gradient text effect
        self.logo_canvas = tk.Canvas(logo_frame, width=80, height=80, 
                                    bg='#1e293b', highlightthickness=0)
        self.logo_canvas.pack()
        
        # Draw animated logo
        self.draw_logo()
        
        # Main title with glow effect
        title_frame = tk.Frame(header_frame, bg='#1e293b')
        title_frame.pack()
        
        self.title_label = tk.Label(title_frame,
                                   text="ALD Book Manager",
                                   font=('Segoe UI', 36, 'bold'),
                                   fg='#ffffff',
                                   bg='#1e293b')
        self.title_label.pack()
        
        # Subtitle with fade-in animation
        self.subtitle_label = tk.Label(title_frame,
                                      text="Advanced Library & Documentation System",
                                      font=('Segoe UI', 14),
                                      fg='#94a3b8',
                                      bg='#1e293b')
        self.subtitle_label.pack(pady=(5, 0))
        
        # Animated accent line
        accent_canvas = tk.Canvas(title_frame, width=200, height=4,
                                 bg='#1e293b', highlightthickness=0)
        accent_canvas.pack(pady=15)
        self.accent_canvas = accent_canvas
        self.draw_accent_line()
    
    def draw_logo(self):
        """Draw animated logo"""
        self.logo_canvas.delete("all")
        
        # Animated book icon
        center_x, center_y = 40, 40
        time_offset = self.animation_frame * 0.05
        
        # Book spine
        spine_height = 50 + math.sin(time_offset) * 2
        self.logo_canvas.create_rectangle(center_x - 15, center_y - spine_height//2,
                                         center_x - 5, center_y + spine_height//2,
                                         fill='#3b82f6', outline='#60a5fa', width=1)
        
        # Book pages
        for i in range(3):
            offset = i * 2 + math.sin(time_offset + i) * 1
            self.logo_canvas.create_rectangle(center_x - 5 + offset, center_y - spine_height//2 + 5,
                                             center_x + 15 + offset, center_y + spine_height//2 - 5,
                                             fill='#f8fafc', outline='#e2e8f0')
        
        # Glowing effect
        glow_radius = 25 + math.sin(time_offset * 2) * 3
        for i in range(3):
            # Use visible blue color instead of alpha
            glow_colors = ['#1e40af', '#3730a3', '#1e3a8a']
            color = glow_colors[min(i, 2)]
            self.logo_canvas.create_oval(center_x - glow_radius - i*3, center_y - glow_radius - i*3,
                                        center_x + glow_radius + i*3, center_y + glow_radius + i*3,
                                        outline=color, width=1, fill="")
    
    def draw_accent_line(self):
        """Draw animated accent line"""
        self.accent_canvas.delete("all")
        
        width = 200
        progress = (math.sin(self.animation_frame * 0.03) + 1) / 2
        
        # Gradient line
        for i in range(width):
            x_progress = i / width
            intensity = progress * (1 - abs(x_progress - 0.5) * 2)
            
            # Use blue gradient instead of alpha
            if intensity > 0.1:
                if intensity > 0.8:
                    color = '#3b82f6'
                elif intensity > 0.5:
                    color = '#2563eb'
                elif intensity > 0.3:
                    color = '#1d4ed8'
                else:
                    color = '#1e40af'
                
                self.accent_canvas.create_line(i, 2, i+1, 2, fill=color, width=2)
    
    def create_navigation_cards(self):
        """Create modern navigation cards with hover effects"""
        cards_frame = tk.Frame(self.content_frame, bg='#1e293b')
        cards_frame.pack(expand=True, pady=30)
        
        # Card configurations
        cards_config = [
            {
                'title': 'Book Gallery',
                'subtitle': 'Browse & Manage Your Books',
                'icon': '📚',
                'description': 'View, create, and organize your book collections with an intuitive interface',
                'action': lambda: self.controller.show_frame("BookGalleryScreen"),
                'color': '#3b82f6',
                'hover_color': '#2563eb'
            },
            {
                'title': 'Code Management',
                'subtitle': 'Advanced Code Operations',
                'icon': '🔤',
                'description': 'Add, edit, search, and manage codes across all your books efficiently',
                'action': lambda: self.controller.show_frame("CodeManagementScreen"),
                'color': '#10b981',
                'hover_color': '#059669'
            }
        ]
        
        for i, config in enumerate(cards_config):
            card = self.create_nav_card(cards_frame, config, i)
            card.pack(pady=15, padx=40, fill='x')
    
    def create_nav_card(self, parent, config, index):
        """Create individual navigation card with advanced styling"""
        # Main card container
        card_frame = tk.Frame(parent, bg='#2d3748', relief='ridge', bd=1, cursor='hand2')
        
        # Add hover effects
        card_id = f"card_{index}"
        self.hover_animations[card_id] = {'scale': 1.0, 'glow': 0.0}
        
        # Bind events
        def on_enter(event):
            self.animate_card_hover(card_id, True)
        
        def on_leave(event):
            self.animate_card_hover(card_id, False)
        
        def on_click(event):
            self.animate_card_click(card_id, config['action'])
        
        card_frame.bind('<Enter>', on_enter)
        card_frame.bind('<Leave>', on_leave)
        card_frame.bind('<Button-1>', on_click)
        
        # Card content
        content_frame = tk.Frame(card_frame, bg='#2d3748')
        content_frame.pack(expand=True, fill='both', padx=30, pady=25)
        
        # Left side - Icon and title
        left_frame = tk.Frame(content_frame, bg='#2d3748')
        left_frame.pack(side='left', fill='y')
        
        # Icon with glow effect
        icon_frame = tk.Frame(left_frame, bg='#2d3748')
        icon_frame.pack(anchor='w')
        
        icon_label = tk.Label(icon_frame,
                             text=config['icon'],
                             font=('Segoe UI Emoji', 32),
                             bg='#2d3748',
                             cursor='hand2')
        icon_label.pack(side='left')
        icon_label.bind('<Button-1>', on_click)
        
        # Title and subtitle
        text_frame = tk.Frame(left_frame, bg='#2d3748')
        text_frame.pack(anchor='w', pady=(10, 0))
        
        title_label = tk.Label(text_frame,
                              text=config['title'],
                              font=('Segoe UI', 20, 'bold'),
                              fg='#ffffff',
                              bg='#2d3748',
                              cursor='hand2')
        title_label.pack(anchor='w')
        title_label.bind('<Button-1>', on_click)
        
        subtitle_label = tk.Label(text_frame,
                                 text=config['subtitle'],
                                 font=('Segoe UI', 12),
                                 fg=config['color'],
                                 bg='#2d3748',
                                 cursor='hand2')
        subtitle_label.pack(anchor='w', pady=(2, 0))
        subtitle_label.bind('<Button-1>', on_click)
        
        # Right side - Description and arrow
        right_frame = tk.Frame(content_frame, bg='#2d3748')
        right_frame.pack(side='right', fill='both', expand=True, padx=(30, 0))
        
        desc_label = tk.Label(right_frame,
                             text=config['description'],
                             font=('Segoe UI', 11),
                             fg='#94a3b8',
                             bg='#2d3748',
                             wraplength=300,
                             justify='left',
                             cursor='hand2')
        desc_label.pack(anchor='w', pady=(10, 0))
        desc_label.bind('<Button-1>', on_click)
        
        # Arrow indicator
        arrow_label = tk.Label(right_frame,
                              text='→',
                              font=('Segoe UI', 18),
                              fg=config['color'],
                              bg='#2d3748',
                              cursor='hand2')
        arrow_label.pack(anchor='e', side='bottom')
        arrow_label.bind('<Button-1>', on_click)
        
        # Bind all child widgets for hover/click
        for widget in [icon_label, title_label, subtitle_label, desc_label, arrow_label]:
            widget.bind('<Enter>', on_enter)
            widget.bind('<Leave>', on_leave)
        
        return card_frame
    
    def create_footer(self):
        """Create footer with additional info"""
        footer_frame = tk.Frame(self.content_frame, bg='#1e293b')
        footer_frame.pack(side='bottom', pady=30)
        
        # Stats or info
        stats_frame = tk.Frame(footer_frame, bg='#1e293b')
        stats_frame.pack()
        
        # Version info
        version_label = tk.Label(stats_frame,
                                text="Version 2.0 • ALD Management Suite",
                                font=('Segoe UI', 10),
                                fg='#64748b',
                                bg='#1e293b')
        version_label.pack()
        
        # Feature highlights
        features_frame = tk.Frame(footer_frame, bg='#1e293b')
        features_frame.pack(pady=(15, 0))
        
        features_text = "✨ Modern Interface • 🚀 Fast Performance • 📊 Advanced Analytics"
        features_label = tk.Label(features_frame,
                                 text=features_text,
                                 font=('Segoe UI', 9),
                                 fg='#475569',
                                 bg='#1e293b')
        features_label.pack()
    
    def animate_card_hover(self, card_id, entering):
        """Animate card hover effects"""
        if card_id in self.hover_animations:
            target_scale = 1.02 if entering else 1.0
            target_glow = 1.0 if entering else 0.0
            
            # Simple immediate effect (in a real app, you'd use smooth transitions)
            self.hover_animations[card_id]['scale'] = target_scale
            self.hover_animations[card_id]['glow'] = target_glow
    
    def animate_card_click(self, card_id, action):
        """Animate card click and execute action"""
        # Visual feedback
        self.after(100, action)  # Small delay for visual feedback
    
    def start_animations(self):
        """Start background animations"""
        def animate():
            self.animation_frame += 1
            self.draw_background()
            self.draw_logo()
            self.draw_accent_line()
            self.after(50, animate)  # ~20 FPS
        
        animate()


class ALDApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ALD Book Manager")
        
        # Modern window setup
        self.setup_window()
        self.setup_styles()
        
        # Main container
        self.container = tk.Frame(self, bg='#0f1419')
        self.container.pack(fill="both", expand=True)

        # Import other screens (keeping existing imports)
        from book_gallery import BookGalleryScreen
        from code_management import CodeManagementScreen

        self.frames = {}
        for F in (ModernMainMenu, BookGalleryScreen, CodeManagementScreen):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.place(relx=0, rely=0, relwidth=1.0, relheight=1.0)

        self.show_frame("ModernMainMenu")

    def setup_window(self):
        """Configure window with modern styling"""
        # Get screen dimensions
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Set window size (85% of screen, minimum 1400x900)
        window_width = max(1400, int(screen_width * 0.85))
        window_height = max(900, int(screen_height * 0.85))
        
        # Center window
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.minsize(1200, 800)
        
        # Modern window styling
        self.configure(bg='#0f1419')

    def setup_styles(self):
        """Configure modern styling"""
        style = ttk.Style()
        style.theme_use('clam')  # Modern base theme
        
        # Configure modern styles
        style.configure('Modern.TButton',
                       padding=(20, 12),
                       font=('Segoe UI', 11),
                       relief='flat')

    def show_frame(self, page_name):
        """Show the specified frame"""
        frame = self.frames[page_name]
        frame.tkraise()


if __name__ == "__main__":
    app = ALDApp()
    app.mainloop()
