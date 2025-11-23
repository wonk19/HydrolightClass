"""
P02_GUI_bottom.py
Bottom Reflectance Spectrum GUI Viewer
"""

import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import os
import glob

class BottomReflectanceViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Bottom Reflectance Spectrum Viewer")
        self.root.geometry("1200x700")
        
        self.data_dir = r"C:\HE60\cursor\data\bottom_reflectances"
        self.colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown', 
                       'pink', 'gray', 'olive', 'cyan', 'magenta', 'navy']
        self.color_index = 0
        self.plotted_lines = []
        
        self.setup_gui()
        self.load_file_list()
    
    def setup_gui(self):
        # Left frame
        left_frame = tk.Frame(self.root, width=300, padx=10, pady=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
        
        # Right frame
        right_frame = tk.Frame(self.root, padx=10, pady=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(left_frame, text="Bottom Reflectance Files", 
                               font=('Arial', 12, 'bold'))
        title_label.pack(pady=(0, 10))
        
        # Listbox with scrollbar
        listbox_frame = tk.Frame(left_frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.file_listbox = tk.Listbox(listbox_frame, yscrollcommand=scrollbar.set,
                                       selectmode=tk.SINGLE, height=20)
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.file_listbox.yview)
        
        # Double-click binding
        self.file_listbox.bind('<Double-Button-1>', lambda e: self.plot_selected())
        
        # Hold checkbox
        self.hold_var = tk.BooleanVar(value=False)
        hold_check = tk.Checkbutton(left_frame, text="Hold (keep previous plots)", 
                                     variable=self.hold_var, font=('Arial', 10))
        hold_check.pack(pady=(0, 10))
        
        # Buttons
        button_frame = tk.Frame(left_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        plot_btn = tk.Button(button_frame, text="Plot", command=self.plot_selected,
                            bg='#4CAF50', fg='white', font=('Arial', 10, 'bold'),
                            padx=20, pady=5)
        plot_btn.pack(fill=tk.X, pady=(0, 5))
        
        clear_btn = tk.Button(button_frame, text="Clear All", command=self.clear_plot,
                             bg='#f44336', fg='white', font=('Arial', 10, 'bold'),
                             padx=20, pady=5)
        clear_btn.pack(fill=tk.X)
        
        # Info label
        self.info_label = tk.Label(left_frame, text="Ready", 
                                   font=('Arial', 9), fg='gray')
        self.info_label.pack(side=tk.BOTTOM, pady=(10, 0))
        
        # Matplotlib figure
        self.fig = Figure(figsize=(8, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlabel('Wavelength (nm)', fontsize=11)
        self.ax.set_ylabel('Reflectance (nondimensional)', fontsize=11)
        self.ax.set_title('Bottom Reflectance Spectrum', fontsize=13, fontweight='bold')
        self.ax.grid(True, alpha=0.3)
        
        # Canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=right_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def load_file_list(self):
        try:
            txt_files = glob.glob(os.path.join(self.data_dir, "*.txt"))
            for file_path in sorted(txt_files):
                filename = os.path.basename(file_path)
                if filename.lower() != 'filelist.txt':
                    self.file_listbox.insert(tk.END, filename)
            self.info_label.config(text=f"Found {self.file_listbox.size()} files")
        except Exception as e:
            self.info_label.config(text=f"Error: {e}")
    
    def parse_reflectance_file(self, filepath):
        wavelengths = []
        reflectances = []
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                in_data = False
                for line in f:
                    line = line.strip()
                    if '\\end_header' in line:
                        in_data = True
                        continue
                    if '\\end_data' in line:
                        break
                    if in_data and line:
                        try:
                            parts = line.split()
                            if len(parts) >= 2 and not line.startswith('\\'):
                                wavelengths.append(float(parts[0]))
                                reflectances.append(float(parts[1]))
                        except:
                            pass
        except Exception as e:
            print(f"Error parsing: {e}")
        return wavelengths, reflectances
    
    def plot_selected(self):
        selection = self.file_listbox.curselection()
        if not selection:
            self.info_label.config(text="Please select a file first")
            return
        
        filename = self.file_listbox.get(selection[0])
        filepath = os.path.join(self.data_dir, filename)
        
        if not self.hold_var.get():
            self.clear_plot()
        
        wavelengths, reflectances = self.parse_reflectance_file(filepath)
        
        if len(wavelengths) == 0:
            self.info_label.config(text=f"No data in {filename}")
            return
        
        color = self.colors[self.color_index % len(self.colors)]
        self.color_index += 1
        
        label = filename.replace('.txt', '')
        line, = self.ax.plot(wavelengths, reflectances, '-', linewidth=2, 
                            color=color, label=label)
        
        self.plotted_lines.append((line, label))
        self.ax.legend(fontsize=9, loc='best')
        self.canvas.draw()
        
        num_plots = len(self.plotted_lines)
        self.info_label.config(text=f"Plotted: {filename} ({num_plots} total)")
    
    def clear_plot(self):
        self.ax.clear()
        self.ax.set_xlabel('Wavelength (nm)', fontsize=11)
        self.ax.set_ylabel('Reflectance (nondimensional)', fontsize=11)
        self.ax.set_title('Bottom Reflectance Spectrum', fontsize=13, fontweight='bold')
        self.ax.grid(True, alpha=0.3)
        self.plotted_lines = []
        self.color_index = 0
        self.canvas.draw()
        self.info_label.config(text="Plot cleared")

def main():
    root = tk.Tk()
    app = BottomReflectanceViewer(root)
    root.mainloop()

if __name__ == "__main__":
    main()
