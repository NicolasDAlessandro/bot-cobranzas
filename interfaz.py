import customtkinter as ctk
import pandas as pd
from tkinter import filedialog, messagebox, ttk
from whatsapp_utils import enviar_mensajes
from pdf_processor import extraer_datos_pdf
import re

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Bot de Mensajes")
        self.geometry("900x720")

        self.datos = None
        self.filas_seleccionadas = {}
        self.modo_prueba = ctk.BooleanVar(value=False)
        self.buscador_var = ctk.StringVar()
        self.buscador_var.trace_add("write", lambda *args: self.filtrar_por_nombre())

        self.crear_widgets()

    def crear_widgets(self):
        ctk.CTkLabel(self, text="Envío de mensajes por WhatsApp", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=10)
        ctk.CTkButton(self, text="Cargar PDF", command=self.cargar_pdf).pack(pady=5)

        ctk.CTkLabel(self, text="Mensaje a enviar (usa {Nombre}, {DEBE}, etc.):").pack(pady=(20, 5))
        self.texto_mensaje = ctk.CTkTextbox(self, height=120)
        self.texto_mensaje.insert("0.0", "Buenas tardes {Nombre}, me comunico del sector de cobranzas de Gasloni, para informarte que el {ULT_VTO} venció la cuota de tu crédito. Podes abonarla de forma presencial o mediante transferencia. Recordá que a partir de la fecha del vencimiento se generan intereses diarios. Saludos.")
        self.texto_mensaje.pack(padx=20, pady=5, fill="both")

        ctk.CTkCheckBox(self, text="Modo prueba (no enviar mensajes)", variable=self.modo_prueba).pack(pady=10)
        ctk.CTkButton(self, text="Enviar mensajes", command=self.enviar_mensajes).pack(pady=10)
        ctk.CTkButton(self, text="☑️ Marcar/Desmarcar Todos", command=self.toggle_todos).pack(pady=5)

        self.label_estado = ctk.CTkLabel(self, text="⏳ Esperando acciones...")
        self.label_estado.pack(pady=10)

        self.entry_busqueda = ctk.CTkEntry(self, textvariable=self.buscador_var, placeholder_text="Filtrar por nombre")
        self.entry_busqueda.pack(padx=30, pady=(1, 3), ipadx=5, ipady=2)

        self.frame_tabla = ctk.CTkFrame(self)
        self.frame_tabla.pack(padx=20, pady=10, fill="both", expand=True)

        self.tree = ttk.Treeview(self.frame_tabla, show="headings")
        self.tree.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(self.frame_tabla, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        self.texto_log = ctk.CTkTextbox(self, height=150)
        self.texto_log.pack(padx=20, pady=10, fill="both", expand=False)

    def cargar_pdf(self):
        path = filedialog.askopenfilename(filetypes=[("Archivos PDF", "*.pdf")])
        if not path:
            return

        self.label_estado.configure(text="⏳ Procesando archivo PDF...")
        self.update_idletasks()

        try:
            datos_raw = extraer_datos_pdf(path)
            messagebox.showinfo("Debug", f"Se extrajeron {len(datos_raw)} filas crudas del PDF.")

            datos_limpios = []
            for _, fila in datos_raw.iterrows():
                nombre = fila.get("Nombre", "")
                if not nombre or "*" in nombre:
                    continue

                match = re.search(r"[A-Za-zÁ-ú].*", nombre)
                if match:
                    nombre = match.group(0).strip()

                try:
                    debe = float(str(fila["DEBE"]).replace(",", "").replace(".", ""))
                    haber = float(str(fila["HABER"]).replace(",", "").replace(".", ""))
                    saldo = float(str(fila["SALDO"]).replace(",", "").replace(".", ""))
                except ValueError:
                    continue

                if haber >= debe or haber >= saldo:
                    continue

                fila["Nombre"] = nombre
                fila["Seleccionado"] = True
                datos_limpios.append(fila)

            self.datos = pd.DataFrame(datos_limpios)
            self.mostrar_datos_en_tabla()
            self.label_estado.configure(text=f"Datos cargados: {len(self.datos)} filas")
            messagebox.showinfo("PDF cargado", f"Se cargaron {len(self.datos)} filas válidas.")

        except Exception as e:
            messagebox.showerror("Error al procesar PDF", str(e))
            self.label_estado.configure(text="❌ Error al procesar el PDF")

    def mostrar_datos_en_tabla(self, df=None):
        self.tree.delete(*self.tree.get_children())
        if df is None:
            df = self.datos

        columnas = ["Seleccionado"] + [col for col in df.columns if col != "Seleccionado"]
        self.tree["columns"] = columnas

        for col in columnas:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=100)

        self.tree.column("Seleccionado", width=60)

        for idx, fila in df.iterrows():
            seleccionado = "✔" if fila.get("Seleccionado", False) else ""
            valores = [seleccionado] + [fila.get(col, "") for col in columnas if col != "Seleccionado"]
            item_id = self.tree.insert("", "end", values=valores)
            self.filas_seleccionadas[item_id] = idx

        self.tree.bind("<ButtonRelease-1>", self.on_click_checkbox)

    def filtrar_por_nombre(self):
        if self.datos is None:
            return

        texto = self.buscador_var.get().lower()
        if not texto:
            self.mostrar_datos_en_tabla()
        else:
            filtrado = self.datos[self.datos["Nombre"].str.lower().str.contains(texto, na=False)]
            self.mostrar_datos_en_tabla(filtrado)

    def on_click_checkbox(self, event):
        item_id = self.tree.identify_row(event.y)
        columna = self.tree.identify_column(event.x)
        if not item_id or columna != "#1":
            return

        idx = self.filas_seleccionadas.get(item_id)
        if idx is not None and idx in self.datos.index:
            actual = self.datos.at[idx, "Seleccionado"]
            nuevo = not actual
            self.datos.at[idx, "Seleccionado"] = nuevo
            self.tree.set(item_id, "Seleccionado", "✔" if nuevo else "")

    def toggle_todos(self):
        if self.datos is None:
            return

        marcar_todo = not self.datos["Seleccionado"].all()
        self.datos["Seleccionado"] = marcar_todo
        self.filtrar_por_nombre()  

    def enviar_mensajes(self):
        if self.datos is None or self.datos.empty:
            messagebox.showerror("Error", "Debes cargar un archivo primero.")
            return

        seleccionados = self.datos[self.datos["Seleccionado"] == True]
        if seleccionados.empty:
            messagebox.showwarning("Nada seleccionado", "No hay filas seleccionadas.")
            return

        mensaje = self.texto_mensaje.get("0.0", "end").strip()
        if not mensaje:
            messagebox.showerror("Error", "Debes ingresar un mensaje.")
            return

        if messagebox.askyesno("Confirmación", f"Se enviarán {len(seleccionados)} mensajes. ¿Continuar?"):
            self.label_estado.configure(text="📤 Enviando mensajes...")
            self.texto_log.delete("0.0", "end")

            def log(msg):
                self.texto_log.insert("end", msg + "\n")
                self.texto_log.see("end")
                self.update_idletasks()

            enviados, fallidos = enviar_mensajes(
                seleccionados, mensaje,
                callback_log=log,
                modo_prueba=self.modo_prueba.get()
            )

            self.label_estado.configure(text=f"✅ Finalizado | Enviados: {enviados} | Fallidos: {fallidos}")
            messagebox.showinfo("Resultado", f"✅ Enviados: {enviados}\n❌ Fallidos: {fallidos}")

if __name__ == "__main__":
    app = App()
    app.mainloop()
