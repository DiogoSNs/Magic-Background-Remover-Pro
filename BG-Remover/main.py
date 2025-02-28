from rembg import remove
from PIL import Image, ImageTk, ImageOps
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinterdnd2 import TkinterDnD, DND_FILES
import threading
import platform
import os
import subprocess

class ProfessionalRemoverApp(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("BG Remover Pro")
        self.geometry("1000x700")
        self.minsize(800, 600)
        self.configure(bg="#2A2D37")
        self.style = ttk.Style()
        
        # Configuração de temas
        self._setup_styles()
        self._create_widgets()
        self._setup_drag_drop()
        
        # Variáveis de estado
        self.input_path = ""
        self.output_path = ""

    def _setup_styles(self):
        self.style.theme_use('clam')
        
        color_palette = {
            'primary': "#4A90E2",
            'secondary': "#6FCF97",
            'background': "#2A2D37",
            'surface': "#373B47",
            'text': "#FFFFFF",
            'accent': "#F2C94C",
            'error': "#EB5757"
        }
        
        self.style.configure('.', background=color_palette['background'])
        self.style.configure('TFrame', background=color_palette['background'])
        self.style.configure('TLabel', 
                           background=color_palette['background'],
                           foreground=color_palette['text'],
                           font=('Segoe UI', 10))
        
        self.style.configure('Primary.TButton', 
                           background=color_palette['primary'],
                           foreground=color_palette['text'],
                           borderwidth=0,
                           focuscolor=color_palette['secondary'],
                           font=('Segoe UI', 10, 'bold'),
                           padding=10)
        
        self.style.map('Primary.TButton',
                     background=[('active', color_palette['secondary'])])
        
        self.style.configure('Progress.Horizontal.TProgressbar',
                           thickness=25,
                           troughcolor=color_palette['surface'],
                           background=color_palette['accent'],
                           bordercolor=color_palette['surface'])
        
        self.style.configure('Preview.TFrame',
                           background=color_palette['surface'],
                           relief='solid',
                           borderwidth=2)
        
        self.style.configure('Status.TFrame',
                           background=color_palette['surface'])
        
    def _create_widgets(self):
        # Header
        header_frame = ttk.Frame(self)
        header_frame.pack(pady=20, padx=20, fill='x')
        
        title_label = ttk.Label(header_frame, 
                              text="🧙 BG REMOVER PRO", 
                              font=('Segoe UI', 18, 'bold'),
                              foreground="#4A90E2")
        title_label.pack(side='left')
        
        # Main Container
        main_container = ttk.Frame(self)
        main_container.pack(expand=True, fill='both', padx=20, pady=10)
        
        # Painel de Controle
        control_frame = ttk.Frame(main_container)
        control_frame.pack(side='left', fill='y', padx=10)
        
        # Seção de Entrada
        input_group = ttk.Frame(control_frame)
        input_group.pack(pady=10, fill='x')
        
        ttk.Label(input_group, 
                text="IMAGEM DE ENTRADA", 
                font=('Segoe UI', 11, 'bold'),
                foreground="#A0A0A0").pack(anchor='w')
        
        self.input_btn = ttk.Button(input_group, 
                                  text="Selecionar Arquivo", 
                                  style='Primary.TButton',
                                  command=self.select_image)
        self.input_btn.pack(pady=5, fill='x')
        
        self.input_label = ttk.Label(input_group, 
                                   text="Arraste uma imagem aqui", 
                                   wraplength=200,
                                   foreground="#A0A0A0")
        self.input_label.pack(pady=5)
        
        # Seção de Saída
        output_group = ttk.Frame(control_frame)
        output_group.pack(pady=10, fill='x')
        
        ttk.Label(output_group, 
                text="DESTINO DA SAÍDA", 
                font=('Segoe UI', 11, 'bold'),
                foreground="#A0A0A0").pack(anchor='w')
        
        self.output_btn = ttk.Button(output_group, 
                                   text="Definir Destino", 
                                   style='Primary.TButton',
                                   command=self.select_output)
        self.output_btn.pack(pady=5, fill='x')
        
        self.output_label = ttk.Label(output_group, 
                                    text="Nenhum destino selecionado", 
                                    wraplength=200,
                                    foreground="#A0A0A0")
        self.output_label.pack(pady=5)
        
        # Visualização
        preview_frame = ttk.Frame(main_container, style='Preview.TFrame')
        preview_frame.pack(side='right', expand=True, fill='both', padx=10)
        
        # Pré-visualizações
        self.before_canvas = tk.Canvas(preview_frame, 
                                      bg="#373B47", 
                                      highlightthickness=0)
        self.before_canvas.pack(side='left', expand=True, fill='both', padx=10, pady=10)
        
        vsplit = ttk.Frame(preview_frame, width=2, style='TFrame')
        vsplit.pack(side='left', fill='y', padx=5)
        
        self.after_canvas = tk.Canvas(preview_frame, 
                                     bg="#373B47", 
                                     highlightthickness=0)
        self.after_canvas.pack(side='left', expand=True, fill='both', padx=10, pady=10)
        
        # Barra de Status
        self.status_bar = ttk.Frame(self, style='Status.TFrame')
        self.status_bar.pack(fill='x', padx=20, pady=(0, 5))
        self.status_label = ttk.Label(self.status_bar, 
                                    text="Pronto", 
                                    foreground="#A0A0A0")
        self.status_label.pack(side='left', padx=10)
        
        # Barra de Progresso
        self.progress = ttk.Progressbar(self, style='Progress.Horizontal.TProgressbar')
        self.progress.pack(fill='x', padx=20, pady=(0, 10))
        
        # Botão Principal
        self.process_btn = ttk.Button(self, 
                                    text="REMOVER FUNDO", 
                                    style='Primary.TButton',
                                    state='disabled',
                                    command=self.start_processing)
        self.process_btn.pack(pady=(0, 20), padx=20, fill='x')
        
    def _setup_drag_drop(self):
        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self.handle_drop)
        self.input_label.bind("<Enter>", lambda e: self.input_label.config(foreground="#4A90E2"))
        self.input_label.bind("<Leave>", lambda e: self.input_label.config(foreground="#A0A0A0"))
        
    def handle_drop(self, event):
        try:
            raw_path = event.data
            file_path = raw_path.strip().rstrip("}").lstrip("{")
            
            if platform.system() == 'Windows':
                file_path = file_path.replace('\\', '/')
            
            valid_extensions = ('.png', '.jpg', '.jpeg')
            if not any(file_path.lower().endswith(ext) for ext in valid_extensions):
                raise ValueError("Formatos suportados: PNG, JPG, JPEG")
            
            self.input_path = file_path
            self.input_label.config(text=file_path.split('/')[-1], foreground="#FFFFFF")
            self.update_preview()
            self.check_ready()
            
        except Exception as e:
            self.show_error(f"Erro no Drag & Drop:\n{str(e)}")
            
    def update_preview(self):
        try:
            img = Image.open(self.input_path)
            img.thumbnail((400, 400))
            bordered_img = ImageOps.expand(img, border=2, fill="#4A90E2")
            self._update_canvas(self.before_canvas, bordered_img)
            self.after_canvas.delete("all")
        except Exception as e:
            self.show_error(f"Erro ao carregar pré-visualização:\n{str(e)}")
            
    def _update_canvas(self, canvas, image):
        canvas.delete("all")
        img_tk = ImageTk.PhotoImage(image)
        canvas.image = img_tk
        canvas.config(width=img_tk.width(), height=img_tk.height())
        canvas.create_image(
            (canvas.winfo_width() - img_tk.width()) // 2,
            (canvas.winfo_height() - img_tk.height()) // 2,
            anchor='nw', 
            image=img_tk
        )
        
    def select_image(self):
        filetypes = (
            ('Imagens', '*.png *.jpg *.jpeg'),
            ('Todos os arquivos', '*.*')
        )
        file_path = filedialog.askopenfilename(title="Selecionar Imagem", filetypes=filetypes)
        if file_path:
            self.input_path = file_path
            self.input_label.config(text=file_path.split('/')[-1], foreground="#FFFFFF")
            self.update_preview()
            self.check_ready()
            
    def select_output(self):
        filetypes = (
            ('PNG', '*.png'),
            ('JPG', '*.jpg'),
            ('Todos os arquivos', '*.*')
        )
        file_path = filedialog.asksaveasfilename(
            title="Salvar Como",
            filetypes=filetypes,
            defaultextension=".png"
        )
        if file_path:
            self.output_path = file_path
            self.output_label.config(text=file_path.split('/')[-1], foreground="#FFFFFF")
            self.check_ready()
            
    def check_ready(self):
        if self.input_path and self.output_path:
            self.process_btn.config(state='normal')
            return True
        return False
            
    def start_processing(self):
        self.status_label.config(text="Processando... Por favor aguarde")
        self.progress['value'] = 0
        threading.Thread(target=self.process_image, daemon=True).start()
        
    def process_image(self):
        try:
            self.process_btn.config(state='disabled')
            
            # Processamento em etapas com atualização de progresso
            self._update_progress(10, "Abrindo imagem...")
            original_img = Image.open(self.input_path)
            
            self._update_progress(30, "Removendo fundo...")
            no_bg_img = remove(original_img)
            
            self._update_progress(70, "Salvando resultado...")
            no_bg_img.save(self.output_path)
            
            # Abre a imagem automaticamente após salvar
            self.open_image(self.output_path)
            
            self._update_progress(100, "Processo concluído!")
            self.show_result()
            
        except Exception as e:
            self.show_error(f"Erro durante o processamento:\n{str(e)}")
        finally:
            self.process_btn.config(state='normal' if self.check_ready() else 'disabled')
            
    def _update_progress(self, value, message):
        self.progress['value'] = value
        self.status_label.config(text=message)
        self.update_idletasks()
            
    def show_result(self):
        try:
            img = Image.open(self.output_path)
            img.thumbnail((400, 400))
            bordered_img = ImageOps.expand(img, border=2, fill="#6FCF97")
            self._update_canvas(self.after_canvas, bordered_img)
            messagebox.showinfo("Sucesso", "Fundo removido com sucesso!")
        except Exception as e:
            self.show_error(f"Erro ao exibir resultado:\n{str(e)}")
            
    def open_image(self, path):
        try:
            if platform.system() == "Windows":
                os.startfile(path)
            elif platform.system() == "Darwin":  # Mac
                subprocess.Popen(["open", path])
            else:  # Linux
                subprocess.Popen(["xdg-open", path])
        except Exception as e:
            self.show_error(f"Não foi possível abrir a imagem automaticamente: {str(e)}")
            
    def show_error(self, message):
        messagebox.showerror("Erro", message)
        self.status_label.config(text="Erro - Verifique os detalhes")

if __name__ == "__main__":
    app = ProfessionalRemoverApp()
    app.mainloop()