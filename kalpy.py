from tkinter import *
import tkinter.font as tkFont

# Responsive dimensions based on screen size
def get_responsive_dimensions():
    root = Tk()
    root.withdraw()
    screen_width = root.winfo_screenwidth()
    root.destroy()
    
    # Reference size aspect for UI
    base_width = 320
    base_height = 490
    
    # Scale based on screen size (minimum 1.0, maximum 2.0)
    scale_factor = min(max(screen_width / 1920, 0.8), 2.0)
    
    # Responsive dimensions
    return {
        'window_width': int(base_width * scale_factor),
        'window_height': int(base_height * scale_factor),
        'margin': int(7 * scale_factor),
        'button_size': int(78 * scale_factor),
        'font_size': max(int(14 * scale_factor), 10),
        'display_font_size': max(int(26 * scale_factor), 16),
        'history_font_size': max(int(13 * scale_factor), 10)
    }

dims = get_responsive_dimensions()

max_len = 14
colors = {
    'dark': '#202020',
    'light': '#fbf9e7',
    'semi-light': '#a6a599',
    'accent-1': '#e8a976',
    'accent-2': '#323232',
    'accent-3': '#3b3b3b',
    'dimmed': "#e87676"
}

class Kalpy:
    def __init__(self, root):
        self.root = root
        self.root.title("Kalpy")
        self.root.config(bg=colors['dark'])
        
        # Use responsive dimensions
        window_width = dims['window_width']
        window_height = dims['window_height']
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.resizable(False, False)
        try:
            icon_image = PhotoImage(file='src/logo.png')
            root.iconphoto(True, icon_image)
        except:
            pass

        # State variables
        self.counter = 0
        self.pre_result = 0
        self.idle = True
        self.stacked = False
        self.pnt_check = False
        self.add_check = False
        self.sub_check = False
        self.mul_check = False
        self.div_check = False
        self.calculated = False

        # History text area
        history_font = ('sans-serif', dims['history_font_size'])
        self.history = Text(root, bd=0, width=34, height=1, font=history_font, bg=colors['dark'], fg=colors['semi-light'], wrap='none', padx=0, pady=2)
        self.history.tag_configure('tag-right', justify='right')
        self.history.grid(row=0, column=0, columnspan=4, sticky="ew", padx=dims['margin'], pady=(dims['margin'], 0))
        self.history.config(state=DISABLED)
        
        # Main text area
        display_font = ('sans-serif', dims['display_font_size'], 'bold')
        self.entry = Text(root, bg=colors['dark'], fg=colors['light'], bd=0, width=16, height=1, font=display_font, wrap='none', padx=1, pady=2)
        self.entry.tag_configure('tag-right', justify='right')
        self.entry.insert('end', '0', 'tag-right')
        self.entry.grid(row=1, column=0, columnspan=4, sticky="ew", padx=dims['margin'], pady=(dims['margin'], 0))
        self.entry.config(state=DISABLED)

        self.create_buttons()

    # Helper funcs
    def get_value(self):
        try:
            val = self.entry.get('1.0', 'end-1c').replace(',', '')
            return int(val) if val.isdigit() else float(val)
        except:
            return None
        
    def get_sym(self, op_type):
        if op_type == "add":
            return "+"
        elif op_type == "sub":
            return "-"
        elif op_type == "mul":
            return "×"
        elif op_type == "div":
            return "÷"
        return ""

    def show_error(self):
        self.entry.config(state=NORMAL)
        self.entry.delete('1.0', END)
        self.entry.insert('end', "¡ERROR!", 'tag-right')
        self.entry.config(state=DISABLED)

        self.counter = 0
        self.pre_result = 0
        self.stacked = False
        self.pnt_check = False
        self.add_check = False
        self.sub_check = False
        self.mul_check = False
        self.div_check = False
        self.calculated = True
        
    def apply_filter(self, value):
        if isinstance(value, float):
            decimal_pos = str(value).find('.')
            if decimal_pos != -1:
                decimal_places = max_len - decimal_pos - 1
                value = round(value, max(decimal_places, 0))

        if isinstance(value, float) and value.is_integer():
            value = int(value)
            
        if value == 0:
            self.idle = True
            
        return value
    
    def apply_format(self, value):
        str_value = str(value)
        if isinstance(value, float):
            decimal_pos = str_value.find('.')
            if decimal_pos != -1:
                decimal_places = len(str_value) - decimal_pos - 1
                str_value = f"{value:,.{decimal_places}f}"
        
        try:
            value = int(str_value) if str(abs(int(str_value))).isdigit() else float(str_value)
            str_value = f"{value:,}"
        except:
            pass
        
        return str_value
    
    # Main funcs
    def insert_char(self, char):
        if self.calculated:
            self.clear()

        self.entry.config(state=NORMAL)

        if self.idle:
            self.idle = False
            self.entry.delete('1.0', END)
        
        commas = self.entry.get('1.0', 'end-1c').count(',')
        extra = 1 if (self.pnt_check and commas <= 1) else 0
        if self.counter < max_len + extra:
            value = char
            self.counter += 1

            if not self.pnt_check:
                value = self.entry.get('1.0', 'end-1c').replace(',', '') + char
                try:
                    value = int(value) if value.isdigit() else float(value) ###
                except:
                    self.show_error()
                    return
                value = self.apply_format(value)
                self.entry.delete('1.0', END)

            self.entry.insert('end', value, 'tag-right')

        self.entry.config(state=DISABLED)

    def insert_point(self):
        if self.calculated:
            self.clear()
        
        if not self.pnt_check:
            self.idle = False
            self.pnt_check = True
            self.entry.config(state=NORMAL)

            if self.get_value() is None:
                self.entry.insert('end', '0', 'tag-right')
                self.counter += 1

            commas = self.entry.get('1.0', 'end-1c').count(',')
            if commas < 4:
                self.entry.insert('end', '.', 'tag-right')

            self.entry.config(state=DISABLED)

    def delete_char(self):
        if self.idle:
            return

        if self.calculated:
            self.history.config(state=NORMAL)
            self.history.delete('1.0', END)
            self.history.config(state=DISABLED)
            return
    
        if self.counter > 0:
            self.entry.config(state=NORMAL)

            value = self.entry.get('1.0', 'end-1c')[:-1]
            self.entry.delete('1.0', END)

            if not value.endswith('.'):
                self.counter -= 1

            if not '.' in value:
                self.pnt_check = False
                value = value.replace(',', '')
                try:
                    value = int(value) if value.isdigit() else float(value)
                except:
                    pass
                value = self.apply_format(value)

            self.entry.insert('end', value, 'tag-right')
            self.entry.config(state=DISABLED)
            
            if self.counter == 0 and not self.stacked:
                self.clear()
    
    def clear(self):
        self.entry.config(state=NORMAL)
        self.entry.delete('1.0', END)
        self.entry.insert('end', '0', 'tag-right')
        self.entry.config(state=DISABLED)
        self.history.config(state=NORMAL)
        self.history.delete('1.0', END)
        self.history.config(state=DISABLED)

        self.counter = 0
        self.pre_result = 0
        self.idle = True
        self.stacked = False
        self.pnt_check = False
        self.add_check = False
        self.sub_check = False
        self.mul_check = False
        self.div_check = False
        self.calculated = False

    def store_op(self, op_type):
        value = self.get_value()
        
        if self.stacked:
            self.add_check = False
            self.sub_check = False
            self.mul_check = False
            self.div_check = False
            setattr(self, f"{op_type}_check", True)

            if value is None:
                stored = self.history.get('1.0', 'end-2c')
                stored = f"{stored[:-2]} {self.get_sym(op_type)} "

                self.history.config(state=NORMAL)
                self.history.delete('1.0', END)
                self.history.insert('end', stored, 'tag-right')
                self.history.config(state=DISABLED)
                return
            
            self.auto_op(self.get_sym(op_type))
            return
        
        self.counter = 0
        self.pre_result = value
        self.pnt_check = False
        self.add_check = False
        self.sub_check = False
        self.mul_check = False
        self.div_check = False
        setattr(self, f"{op_type}_check", True)
            
        self.entry.config(state=NORMAL)
        self.entry.delete('1.0', END)
        self.entry.config(state=DISABLED)
            
        self.history.config(state=NORMAL)
        if self.calculated:
            self.calculated = False
            self.history.delete('1.0', END)
        self.history.insert('end', f"{str(value)} {self.get_sym(op_type)} ", 'tag-right')
        self.history.config(state=DISABLED)

        self.stacked = True

    def percentage(self):
        value = self.get_value()
        if value is not None:
            result = 0
            str_result = ""
            try:
                result = self.apply_filter(value / 100)
                tmp_str = self.apply_format(result)
                str_result = tmp_str if len(str(result)) <= max_len else '¡TOO LONG NUM!'
                self.entry.config(state=NORMAL)
                self.entry.delete('1.0', END)
                self.entry.insert('end', str_result, 'tag-right')
                self.entry.config(state=DISABLED)

                str_history = str(result) if len(str(result)) <= 34 else '¡TOO LONG NUM!'
                self.history.config(state=NORMAL)
                self.history.delete('1.0', END)
                if str_result != '¡TOO LONG NUM!':
                    self.history.insert('end', str_history, 'tag-right')
                self.history.config(state=DISABLED)
            except:
                self.show_error()
                return
                
            self.add_check = False
            self.sub_check = False
            self.mul_check = False
            self.div_check = False
            self.calculated = True
            self.pnt_check = True if str_result.find('.') != -1 else False
            self.counter = len(str_result)
    
    def sign(self):
        value = self.get_value()
        if value is not None:
            result = 0
            str_result = ""
            try:
                result = self.apply_filter(-value)
                tmp_str = self.apply_format(result)
                str_result = tmp_str if len(str(result)) <= max_len else '¡TOO LONG NUM!'
                self.entry.config(state=NORMAL)
                self.entry.delete('1.0', END)
                self.entry.insert('end', str_result, 'tag-right')
                self.entry.config(state=DISABLED)

                str_history = f"negate({str(-result)})" if len(f"negate({str(-result)})") <= 34 else '¡TOO LONG EXP!'
                self.history.config(state=NORMAL)
                self.history.delete('1.0', END)
                if str_result != '¡TOO LONG NUM!':
                    self.history.insert('end', str_history, 'tag-right')
                self.history.config(state=DISABLED)
            except:
                self.show_error()
                return
                
            self.add_check = False
            self.sub_check = False
            self.mul_check = False
            self.div_check = False
            self.calculated = True
            self.pnt_check = True if str_result.find('.') != -1 else False
            self.counter = len(str_result)
    
    def auto_op(self, op_current):
        value = self.get_value()

        if value is None:
            self.show_error()
            return
        
        result = 0
        str_result = ""
        op_history = self.history.get('1.0', END)
        try:
            if '+' in op_history:
                result = self.pre_result + value
            elif '-' in op_history:
                result = self.pre_result - value
            elif '×' in op_history:
                result = self.pre_result * value
            elif '÷' in op_history:
                result = (self.pre_result / value) if value != 0 else None
                if result is None:
                    self.show_error()
                    return
            else:
                result = value

            result = self.apply_filter(result)
            tmp_str = self.apply_format(result)
            str_result = tmp_str if len(str(result)) <= max_len else '¡TOO LONG NUM!'
            self.entry.config(state=NORMAL)
            self.entry.delete('1.0', END)
            self.entry.config(state=DISABLED)
            
            str_history = f"{str_result.replace(',', '')} {op_current} " if len(f"{str_result.replace(',', '')} {op_current} ") <= 34 else '¡TOO LONG EXP!'
            self.history.config(state=NORMAL)
            self.history.delete('1.0', END)
            if str_result != '¡TOO LONG NUM!':
                self.history.insert('end', str_history, 'tag-right')
            self.history.config(state=DISABLED)
        except:
            self.show_error()
            return

        self.pnt_check = False
        self.calculated = False
        self.counter = 0
        self.pre_result = result
    
    def calculate(self):
        value = self.get_value()

        if value is None:
            self.show_error()
            return
        
        result = 0
        str_result = ""
        try:
            if self.add_check:
                result = self.pre_result + value
            elif self.sub_check:
                result = self.pre_result - value
            elif self.mul_check:
                result = self.pre_result * value
            elif self.div_check:
                result = (self.pre_result / value) if value != 0 else None
                if result is None:
                    self.show_error()
                    return
            else:
                result = value

            result = self.apply_filter(result)
            tmp_str = self.apply_format(result)
            str_result = tmp_str if len(str(result)) <= max_len else '¡TOO LONG NUM!'
            self.entry.config(state=NORMAL)
            self.entry.delete('1.0', END)
            self.entry.insert('end', str_result, 'tag-right')
            self.entry.config(state=DISABLED)
            
            stored = self.history.get('1.0', 'end-2c')
            str_history = f"{str(value)} =" if len(f"{stored} {str(value)} =") <= 34 else '¡TOO LONG EXP!'
            self.history.config(state=NORMAL)
            if str_history == f"{str_result} =" or str_result == '¡TOO LONG NUM!':
                self.history.delete('1.0', END)
            if str_result != '¡TOO LONG NUM!':
                self.history.insert('end', str_history, 'tag-right')
            self.history.config(state=DISABLED)
        except:
            self.show_error()
            return

        self.stacked = False
        self.add_check = False
        self.sub_check = False
        self.mul_check = False
        self.div_check = False
        self.calculated = True
        self.pnt_check = True if str_result.find('.') != -1 else False
        self.pre_result = 0
        self.counter = len(str_result)

    # UI funcs
    def on_enter(self, e):
        hover_color = ""
        origin_color = e.widget.base_color
        if origin_color == colors['accent-2']:
            hover_color = colors['accent-3']
        elif origin_color == colors['accent-3']:
            hover_color = colors['accent-2']
        else:
            hover_color = colors['dimmed']
        e.widget['background'] = hover_color

    def on_leave(self, e):
        e.widget['background'] = e.widget.base_color

    def create_buttons(self):
        # Create a frame for all buttons with external padding
        button_frame = Frame(self.root, bg=colors['dark'])
        button_frame.grid(row=2, column=0, columnspan=4, rowspan=5, sticky="nsew", 
                         padx=dims['margin'], pady=dims['margin'])
        
        # Configure grid weights for the button frame
        for i in range(4):
            button_frame.grid_columnconfigure(i, weight=1)
        for i in range(5):
            button_frame.grid_rowconfigure(i, weight=1)
        
        # Configure main window grid weights
        for i in range(4):
            self.root.grid_columnconfigure(i, weight=1)
        for i in range(7):
            self.root.grid_rowconfigure(i, weight=1)

        # Button configuration: [text, row, col, command, colspan]
        btn_info = [
            ("C", 0, 0, self.clear, 1), ("<", 0, 1, self.delete_char, 1), ("%", 0, 2, self.percentage, 1), ("÷", 0, 3, lambda: self.store_op("div"), 1),
            ("7", 1, 0, lambda: self.insert_char('7'), 1), ("8", 1, 1, lambda: self.insert_char('8'), 1), ("9", 1, 2, lambda: self.insert_char('9'), 1), ("×", 1, 3, lambda: self.store_op("mul"), 1),
            ("4", 2, 0, lambda: self.insert_char('4'), 1), ("5", 2, 1, lambda: self.insert_char('5'), 1), ("6", 2, 2, lambda: self.insert_char('6'), 1), ("-", 2, 3, lambda: self.store_op("sub"), 1),
            ("1", 3, 0, lambda: self.insert_char('1'), 1), ("2", 3, 1, lambda: self.insert_char('2'), 1), ("3", 3, 2, lambda: self.insert_char('3'), 1), ("+", 3, 3, lambda: self.store_op("add"), 1),
            ("±", 4, 0, self.sign, 1), ("0", 4, 1, lambda: self.insert_char('0'), 1), (".", 4, 2, self.insert_point, 1), ("=", 4, 3, self.calculate, 1)
        ]

        # Buttons config
        button_font = ('sans-serif', dims['font_size'])
        for text, row, col, cmd, colspan in btn_info:
            init_color = self.get_color(text)
            
            btn = Button(
                button_frame, 
                text=text, 
                command=cmd, 
                bd=0, 
                font=button_font,
                bg=init_color, 
                fg=colors['dark'] if text == "=" else colors['light'], 
                activebackground=colors['dark'], 
                activeforeground=colors['semi-light'],
                width=8,
                height=2
            )
            btn.base_color = init_color
            
            # Use grid layout with padding
            btn.grid(
                row=row, 
                column=col, 
                columnspan=colspan,
                sticky="nsew",
                padx=0, 
                pady=0,
                ipadx=5, # Internal padding
                ipady=5  # Internal padding
            )
            
            btn.bind("<Enter>", self.on_enter)
            btn.bind("<Leave>", self.on_leave)

    def get_color(self, char):
        if char in " -+×÷%=<C":
            return colors['accent-2'] if char != "=" else colors['accent-1']
        else:
            return colors['accent-3']
    
if __name__ == "__main__":
    root = Tk()
    app = Kalpy(root)
    root.mainloop()