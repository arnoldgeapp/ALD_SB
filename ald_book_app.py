import tkinter as tk
from tkinter import ttk
import math

from book_gallery import BookGalleryScreen
from code_management import CodeManagementScreen
from enhanced_code_browser import EnhancedCodeBrowserScreen

class ModernMainMenu(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg='#0f1419')
        self.controller = controller
        self.animation_frame = 0
        self.hover_animations = {}
        self.create_background()
        self.create_content()
        self.start_animations()

    def create_background(self):
        self.bg_canvas = tk.Canvas(self, highlightthickness=0)
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        self.bg_canvas.bind('<Configure>', self.on_canvas_resize)
        self.draw_background()
    
    def draw_background(self):
        self.bg_canvas.delete("all")
        width = self.bg_canvas.winfo_width()
        height = self.bg_canvas.winfo_height()
        if width <= 1 or height <= 1:
            return
        gradient_steps = 50
        for i in range(gradient_steps):
            progress = i / gradient_steps
            time_offset = self.animation_frame * 0.01
            r1, g1, b1 = 15, 20, 25
            r2, g2, b2 = 30, 40, 60
            wave = math.sin(progress * math.pi + time_offset) * 0.1
            r = int(r1 + (r2 - r1) * (progress + wave))
            g = int(g1 + (g2 - g1) * (progress + wave))
            b = int(b1 + (b2 - b1) * (progress + wave))
            color = f"#{r:02x}{g:02x}{b:02x}"
            y = i * height // gradient_steps
            next_y = (i + 1) * height // gradient_steps
            self.bg_canvas.create_rectangle(0, y, width, next_y, fill=color, outline=color)
        self.draw_floating_shapes(width, height)
    
    def draw_floating_shapes(self, width, height):
        shapes = [
            {'type': 'circle', 'x': 0.15, 'y': 0.2, 'size': 60, 'color': '#6366f1', 'speed': 0.4},
            {'type': 'circle', 'x': 0.85, 'y': 0.7, 'size': 80, 'color': '#8b5cf6', 'speed': 0.6},
            {'type': 'rect', 'x': 0.9, 'y': 0.15, 'size': 45, 'color': '#ec4899', 'speed': 0.5},
            {'type': 'rect', 'x': 0.1, 'y': 0.85, 'size': 55, 'color': '#06b6d4', 'speed': 0.7},
            {'type': 'circle', 'x': 0.5, 'y': 0.1, 'size': 35, 'color': '#10b981', 'speed': 0.3},
        ]
        for shape in shapes:
            base_x = shape['x'] * width
            base_y = shape['y'] * height
            float_x = base_x + math.sin(self.animation_frame * 0.02 * shape['speed']) * 25
            float_y = base_y + math.cos(self.animation_frame * 0.015 * shape['speed']) * 20
            size = shape['size']
            glow_size = size + 10
            glow_color = shape['color']
            if shape['type'] == 'circle':
                self.bg_canvas.create_oval(float_x - glow_size//2, float_y - glow_size//2,
                                           float_x + glow_size//2, float_y + glow_size//2,
                                           fill=glow_color, outline="")
                self.bg_canvas.create_oval(float_x - size//2, float_y - size//2,
                                           float_x + size//2, float_y + size//2,
                                           fill=shape['color'], outline="")
            else:
                self.bg_canvas.create_rectangle(float_x - glow_size//2, float_y - glow_size//2,
                                                float_x + glow_size//2, float_y + glow_size//2,
                                                fill=glow_color, outline="")
                self.bg_canvas.create_rectangle(float_x - size//2, float_y - size//2,
                                                float_x + size//2, float_y + size//2,
                                                fill=shape['color'], outline="")
    
    def on_canvas_resize(self, event):
        self.draw_background()
    
    def create_content(self):
        self.content_frame = tk.Frame(self, bg='#1e293b', relief='ridge', bd=1)
        self.content_frame.place(relx=0.5, rely=0.5, anchor='center', relwidth=0.7, relheight=0.8)
        border_frame = tk.Frame(self.content_frame, bg='#334155', height=2)
        border_frame.pack(fill='x')
        self.create_header()
        self.create_navigation_cards()
        self.create_footer()
    
    def create_header(self):
        header_frame = tk.Frame(self.content_frame, bg='#1e293b')
        header_frame.pack(pady=(50, 30))
        title_label = tk.Label(header_frame, text="ALD Book Manager", font=('Segoe UI', 36, 'bold'), fg='#ffffff', bg='#1e293b')
        title_label.pack()
        subtitle_label = tk.Label(header_frame, text="Manage your books and codes with style", font=('Segoe UI', 14), fg='#94a3b8', bg='#1e293b')
        subtitle_label.pack(pady=(10, 0))
        accent_canvas = tk.Canvas(header_frame, width=200, height=4, bg='#1e293b', highlightthickness=0)
        accent_canvas.pack(pady=20)
        self.accent_canvas = accent_canvas
        self.draw_accent_line()
    
    def draw_accent_line(self):
        self.accent_canvas.delete("all")
        width = 200
        colors = ['#6366f1', '#8b5cf6', '#ec4899', '#06b6d4', '#10b981', '#f59e0b']
        for i in range(width):
            progress = (i / width + self.animation_frame * 0.01) % 1
            color_index = int(progress * len(colors))
            next_color_index = (color_index + 1) % len(colors)
            local_progress = (progress * len(colors)) % 1
            current_color = colors[color_index]
            _ = colors[next_color_index]
            intensity = (math.sin(progress * math.pi * 2 + self.animation_frame * 0.05) + 1) / 2
            if intensity > 0.3:
                self.accent_canvas.create_line(i, 2, i+1, 2, fill=current_color, width=3)
    
    def create_navigation_cards(self):
        cards_frame = tk.Frame(self.content_frame, bg='#1e293b')
        cards_frame.pack(expand=True, pady=30)
        card_configs = [
            {
                'title': '📚 Book Gallery',
                'subtitle': 'Browse and manage your book collections',
                'color': '#3b82f6',
                'hover_color': '#2563eb',
                'command': lambda: self.controller.show_frame("BookGalleryScreen")
            },
            {
                'title': '🔤 Code Management',
                'subtitle': 'Basic code editing and management',
                'color': '#64748b',
                'hover_color': '#475569',
                'command': lambda: self.controller.show_frame("CodeManagementScreen")
            },
            {
                'title': '✨ Enhanced Code Browser',
                'subtitle': '🚀 Browse 15 categories • Manage 8 favorites • Add notes',
                'color': '#10b981',
                'hover_color': '#059669',
                'command': lambda: self.controller.show_frame("EnhancedCodeBrowserScreen")
            }
        ]
        for i, config in enumerate(card_configs):
            self.create_navigation_card(cards_frame, config, i)
    
    def create_navigation_card(self, parent, config, index):
        card_frame = tk.Frame(parent, bg=config['color'], relief='flat', cursor='hand2')
        card_frame.pack(pady=20, padx=40, fill='x')
        content_frame = tk.Frame(card_frame, bg=config['color'])
        content_frame.pack(fill='both', padx=30, pady=30)
        title_label = tk.Label(content_frame, text=config['title'], font=('Segoe UI', 20, 'bold'), fg='#ffffff', bg=config['color'])
        title_label.pack()
        subtitle_label = tk.Label(content_frame, text=config['subtitle'], font=('Segoe UI', 12), fg='#e2e8f0', bg=config['color'])
        subtitle_label.pack(pady=(5, 0))
        def on_enter(event):
            card_frame.config(bg=config['hover_color'])
            content_frame.config(bg=config['hover_color'])
            title_label.config(bg=config['hover_color'])
            subtitle_label.config(bg=config['hover_color'])
            self.hover_animations[index] = True
        def on_leave(event):
            card_frame.config(bg=config['color'])
            content_frame.config(bg=config['color'])
            title_label.config(bg=config['color'])
            subtitle_label.config(bg=config['color'])
            self.hover_animations[index] = False
        def on_click(event):
            config['command']()
        for widget in [card_frame, content_frame, title_label, subtitle_label]:
            widget.bind('<Enter>', on_enter)
            widget.bind('<Leave>', on_leave)
            widget.bind('<Button-1>', on_click)
    
    def create_footer(self):
        footer_frame = tk.Frame(self.content_frame, bg='#1e293b')
        footer_frame.pack(side='bottom', pady=30)
        version_label = tk.Label(footer_frame, text="ALD Book Manager v2.0 • Modern Edition", font=('Segoe UI', 10), fg='#64748b', bg='#1e293b')
        version_label.pack()
    
    def start_animations(self):
        def animate():
            self.animation_frame += 1
            self.draw_background()
            self.draw_accent_line()
            self.after(50, animate)
        animate()

class ALDApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ALD Book Manager - Enhanced Edition")
        self.minsize(1200, 800)
        self.geometry("1600x1000")
        self.configure(bg='#0f1419')
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.container = tk.Frame(self, bg='#0f1419')
        self.container.grid(row=0, column=0, sticky="nsew")
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        self.frames = {}
        frame_classes = [
            ("ModernMainMenu", ModernMainMenu),
            ("BookGalleryScreen", BookGalleryScreen),
            ("CodeManagementScreen", CodeManagementScreen),
            ("EnhancedCodeBrowserScreen", EnhancedCodeBrowserScreen)
        ]
        for frame_name, frame_class in frame_classes:
            frame = frame_class(parent=self.container, controller=self)
            self.frames[frame_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame("ModernMainMenu")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

if __name__ == "__main__":
    app = ALDApp()
    app.mainloop()
