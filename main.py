# main.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import os
from database import (
    guardar_contrato, obtener_contratos, obtener_contrato_por_id, buscar_contrato_por_cedula,
    editar_contrato, cambiar_estado, agregar_abono, obtener_abonos, backup_db
)
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False

LOGO_FILE = "logo_cristorey.jpeg"

# ---------- Estilos ----------
BG = "#FFFFFF"
GOLD = "#C8A951"
BUTTON_FONT = ("Arial", 12, "bold")
TITLE_FONT = ("Helvetica", 18, "bold")
SUB_FONT = ("Helvetica", 11)

# ---------- App ----------
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Cristo Rey - Servicios Funerarios")
        self.root.state("zoomed")  # pantalla completa (Windows); si no, use geometry
        self.root.configure(bg=BG)

        # container for frames
        self.container = tk.Frame(self.root, bg=BG)
        self.container.pack(fill="both", expand=True)

        # create frames
        self.frames = {}
        for F in (MenuFrame, NuevoContratoFrame, EditarContratoFrame, RegistrarAbonoFrame, VerAbonosFrame, ContratosFrame):
            frame = F(parent=self.container, controller=self)
            self.frames[F.__name__] = frame
            frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.show_frame("MenuFrame")

    def show_frame(self, name):
        frame = self.frames[name]
        frame.tkraise()
        if hasattr(frame, "on_show"):
            frame.on_show()


# ---------- MENU PRINCIPAL ----------
class MenuFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG)
        self.controller = controller

        # Header (logo + title)
        header = tk.Frame(self, bg=BG)
        header.pack(pady=20)

        # logo
        logo_label = tk.Label(header, bg=BG)
        logo_label.pack()
        if os.path.exists(LOGO_FILE):
            try:
                if PIL_AVAILABLE:
                    img = Image.open(LOGO_FILE)
                    img.thumbnail((220, 220))
                    self.logo_img = ImageTk.PhotoImage(img)
                    logo_label.config(image=self.logo_img)
                else:
                    # Try PhotoImage (may not support JPEG)
                    self.logo_img = tk.PhotoImage(file=LOGO_FILE)
                    logo_label.config(image=self.logo_img)
            except Exception:
                logo_label.config(text="CRISTO REY", font=TITLE_FONT, fg=GOLD, bg=BG)
        else:
            logo_label.config(text="CRISTO REY", font=TITLE_FONT, fg=GOLD, bg=BG)

        tk.Label(self, text="Cristo Rey Servicios Funerarios", font=TITLE_FONT, bg=BG, fg="black").pack()
        tk.Label(self, text="Sistema de Gestión de Contratos y Abonos", font=SUB_FONT, bg=BG, fg=GOLD).pack(pady=(0,10))

        separator = tk.Frame(self, bg=GOLD, height=3)
        separator.pack(fill="x", padx=200, pady=10)

        # Buttons area
        botones_frame = tk.Frame(self, bg=BG)
        botones_frame.pack(pady=20)

        btn_cfg = {"width":30, "height":2, "font":BUTTON_FONT, "bd":0}

        btns = [
            ("➕ Nuevo Contrato", GOLD, lambda: controller.show_frame("NuevoContratoFrame")),
            ("✏️ Editar Contrato", "#4F81BD", lambda: controller.show_frame("EditarContratoFrame")),
            ("💰 Registrar Abono", "#E8A317", lambda: controller.show_frame("RegistrarAbonoFrame")),
            ("📊 Ver Abonos Totales", "#F28C28", lambda: controller.show_frame("VerAbonosFrame")),
            ("📗 Contratos Activos", "#C8A951", lambda: self.abrir_contratos("Activo")),
            ("⏸ Contratos Suspendidos", "#9A7AB0", lambda: self.abrir_contratos("Suspendido")),
            ("❌ Contratos Cancelados", "#D9534F", lambda: self.abrir_contratos("Cancelado")),
            ("💾 Backup Base de Datos", "#BDBDBD", self.hacer_backup),
            ("🚪 Salir del Sistema", "#616161", self.salir_app)
        ]

        for texto, color, cmd in btns:
            b = tk.Button(botones_frame, text=texto, bg=color, fg="black", command=cmd, **btn_cfg)
            b.pack(pady=8)

    def abrir_contratos(self, estado):
        frame = self.controller.frames["ContratosFrame"]
        frame.set_estado(estado)
        self.controller.show_frame("ContratosFrame")

    def hacer_backup(self):
        ruta = backup_db()
        if ruta:
            messagebox.showinfo("Backup creado", f"Respaldo guardado en:\n{ruta}")
        else:
            messagebox.showerror("Error", "No se pudo crear el respaldo.")

    def salir_app(self):
        if messagebox.askyesno("Confirmar", "¿Desea salir del sistema?"):
            self.controller.root.quit()


# ---------- NUEVO CONTRATO ----------
class NuevoContratoFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG)
        self.controller = controller

        # header + back
        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", pady=10)
        tk.Button(top, text="🔙 Volver", bg="#BDBDBD", command=lambda: controller.show_frame("MenuFrame")).pack(side="left", padx=20)

        tk.Label(self, text="Registrar Nuevo Contrato", font=TITLE_FONT, bg=BG, fg="black").pack(pady=5)

        form = tk.Frame(self, bg=BG)
        form.pack(pady=10)

        # ID auto/manual
        id_frame = tk.Frame(form, bg=BG)
        id_frame.grid(row=0, column=0, columnspan=2, pady=5)
        self.var_auto = tk.BooleanVar(value=True)
        chk = tk.Checkbutton(id_frame, text="Generar ID automáticamente", variable=self.var_auto, bg=BG)
        chk.pack(side="left", padx=5)
        tk.Label(id_frame, text="ID Manual:", bg=BG).pack(side="left", padx=5)
        self.entry_id = tk.Entry(id_frame, width=10, state="disabled")
        self.entry_id.pack(side="left", padx=5)

        def toggle_id():
            if self.var_auto.get():
                self.entry_id.config(state="disabled")
            else:
                self.entry_id.config(state="normal")
        chk.config(command=toggle_id)

        # Campos
        labels = ["Nombre", "Cédula", "Dirección", "Teléfono", "Plan", "Mensualidad"]
        self.entries = {}
        for i, lab in enumerate(labels, start=1):
            tk.Label(form, text=lab + ":", bg=BG).grid(row=i, column=0, sticky="e", padx=5, pady=3)
            e = tk.Entry(form, width=50)
            e.grid(row=i, column=1, sticky="w", padx=5, pady=3)
            self.entries[lab.lower()] = e

        # Fecha inicio automática
        self.fecha_inicio = datetime.now().strftime("%Y-%m-%d")
        tk.Label(form, text=f"Fecha de inicio: {self.fecha_inicio}", bg=BG).grid(row=7, column=0, columnspan=2, pady=8)

        # Afiliados
        tk.Label(self, text="Afiliados (máx 10):", bg=BG).pack(pady=(10,0))
        afi_frame = tk.Frame(self, bg=BG)
        afi_frame.pack()
        self.list_afiliados = []
        self.afiliados_box = tk.Listbox(afi_frame, width=70, height=6)
        self.afiliados_box.pack(side="left", padx=5, pady=5)
        afi_buttons = tk.Frame(afi_frame, bg=BG)
        afi_buttons.pack(side="left", padx=5)
        tk.Button(afi_buttons, text="➕ Agregar", bg=GOLD, command=self.agregar_afiliado).pack(pady=5, fill="x")
        tk.Button(afi_buttons, text="✏️ Editar", bg="#BDBDBD", command=self.editar_afiliado).pack(pady=5, fill="x")
        tk.Button(afi_buttons, text="🗑 Eliminar", bg="#D9534F", command=self.eliminar_afiliado).pack(pady=5, fill="x")

        # Guardar
        tk.Button(self, text="💾 Guardar Contrato", bg=GOLD, fg="black", font=BUTTON_FONT, command=self.guardar_contrato).pack(pady=12)

    def agregar_afiliado(self):
        if len(self.list_afiliados) >= 10:
            messagebox.showwarning("Límite", "Máximo 10 afiliados.")
            return
        ventana = tk.Toplevel(self)
        ventana.title("Agregar Afiliado")
        ventana.geometry("350x280")
        tk.Label(ventana, text="Nombre:").pack()
        e_nombre = tk.Entry(ventana); e_nombre.pack()
        tk.Label(ventana, text="Apellido:").pack()
        e_apellido = tk.Entry(ventana); e_apellido.pack()
        tk.Label(ventana, text="Parentesco:").pack()
        e_parentesco = tk.Entry(ventana); e_parentesco.pack()
        tk.Label(ventana, text="Teléfono:").pack()
        e_telefono = tk.Entry(ventana); e_telefono.pack()

        def guardar():
            nombre = e_nombre.get().strip()
            apellido = e_apellido.get().strip()
            parentesco = e_parentesco.get().strip()
            telefono = e_telefono.get().strip()
            if not nombre or not apellido:
                messagebox.showerror("Error", "Nombre y apellido obligatorios.")
                return
            afi = {"nombre": nombre, "apellido": apellido, "parentesco": parentesco, "telefono": telefono}
            self.list_afiliados.append(afi)
            self.afiliados_box.insert(tk.END, f"{nombre} {apellido} ({parentesco}) - {telefono}")
            ventana.destroy()
        tk.Button(ventana, text="Guardar Afiliado", bg=GOLD, command=guardar).pack(pady=10)

    def editar_afiliado(self):
        idx = self.afiliados_box.curselection()
        if not idx:
            messagebox.showwarning("Atención", "Seleccione un afiliado para editar.")
            return
        i = idx[0]
        afi = self.list_afiliados[i]
        ventana = tk.Toplevel(self)
        ventana.title("Editar Afiliado")
        ventana.geometry("350x280")
        tk.Label(ventana, text="Nombre:").pack()
        e_nombre = tk.Entry(ventana); e_nombre.insert(0, afi["nombre"]); e_nombre.pack()
        tk.Label(ventana, text="Apellido:").pack()
        e_apellido = tk.Entry(ventana); e_apellido.insert(0, afi["apellido"]); e_apellido.pack()
        tk.Label(ventana, text="Parentesco:").pack()
        e_parentesco = tk.Entry(ventana); e_parentesco.insert(0, afi.get("parentesco","")); e_parentesco.pack()
        tk.Label(ventana, text="Teléfono:").pack()
        e_telefono = tk.Entry(ventana); e_telefono.insert(0, afi.get("telefono","")); e_telefono.pack()

        def guardar():
            nombre = e_nombre.get().strip(); apellido = e_apellido.get().strip()
            parentesco = e_parentesco.get().strip(); telefono = e_telefono.get().strip()
            if not nombre or not apellido:
                messagebox.showerror("Error", "Nombre y apellido obligatorios.")
                return
            self.list_afiliados[i] = {"nombre": nombre, "apellido": apellido, "parentesco": parentesco, "telefono": telefono}
            self.afiliados_box.delete(i)
            self.afiliados_box.insert(i, f"{nombre} {apellido} ({parentesco}) - {telefono}")
            ventana.destroy()
        tk.Button(ventana, text="Guardar Cambios", bg=GOLD, command=guardar).pack(pady=10)

    def eliminar_afiliado(self):
        idx = self.afiliados_box.curselection()
        if not idx:
            messagebox.showwarning("Atención", "Seleccione un afiliado para eliminar.")
            return
        i = idx[0]
        if messagebox.askyesno("Confirmar", "¿Eliminar afiliado seleccionado?"):
            self.afiliados_box.delete(i)
            del self.list_afiliados[i]

    def guardar_contrato(self):
        try:
            id_manual = self.entry_id.get().strip()
            id_manual = int(id_manual) if (id_manual and not self.var_auto.get()) else None
        except ValueError:
            messagebox.showerror("Error", "ID manual debe ser numérico.")
            return

        nombre = self.entries["nombre"].get().strip()
        cedula = self.entries["cédula"].get().strip()
        direccion = self.entries["dirección"].get().strip()
        telefono = self.entries["teléfono"].get().strip()
        plan = self.entries["plan"].get().strip()
        mensualidad = self.entries["mensualidad"].get().strip()

        if not nombre or not cedula or not plan or not mensualidad:
            messagebox.showerror("Error", "Complete los campos obligatorios.")
            return
        try:
            mensualidad = float(mensualidad)
        except:
            messagebox.showerror("Error", "Mensualidad inválida.")
            return

        fecha_inicio = self.fecha_inicio
        try:
            nuevo_id = guardar_contrato(nombre, cedula, direccion, telefono, plan, mensualidad, fecha_inicio, self.list_afiliados, id_manual)
            messagebox.showinfo("Éxito", f"Contrato guardado. ID: {nuevo_id}")
            # limpiar formulario
            for e in self.entries.values():
                e.delete(0, tk.END)
            self.list_afiliados.clear()
            self.afiliados_box.delete(0, tk.END)
            self.entry_id.delete(0, tk.END)
            self.var_auto.set(True)
            self.controller.show_frame("MenuFrame")
        except Exception as e:
            messagebox.showerror("Error", str(e))


# ---------- EDITAR CONTRATO ----------
class EditarContratoFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG)
        self.controller = controller
        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", pady=8)
        tk.Button(top, text="🔙 Volver", bg="#BDBDBD", command=lambda: controller.show_frame("MenuFrame")).pack(side="left", padx=20)
        tk.Label(self, text="Editar Contrato", font=TITLE_FONT, bg=BG).pack(pady=4)

        search = tk.Frame(self, bg=BG)
        search.pack(pady=6)
        tk.Label(search, text="Buscar por ID o Cédula:", bg=BG).pack(side="left", padx=5)
        self.search_entry = tk.Entry(search, width=30); self.search_entry.pack(side="left", padx=5)
        tk.Button(search, text="Buscar", bg=GOLD, command=self.buscar).pack(side="left", padx=5)

        self.form = tk.Frame(self, bg=BG)
        # fields will be created after search
        self.form.pack(pady=10)

    def buscar(self):
        key = self.search_entry.get().strip()
        if not key:
            messagebox.showwarning("Atención", "Ingrese ID o cédula.")
            return
        contrato = None
        if key.isdigit():
            contrato = obtener_contrato_por_id(int(key))
        if not contrato:
            resultados = buscar_contrato_por_cedula(key)
            contrato = resultados[0] if resultados else None

        for widget in self.form.winfo_children():
            widget.destroy()

        if not contrato:
            messagebox.showinfo("Sin resultados", "No se encontró el contrato.")
            return

        self.current_id = contrato["id"]
        # populate form
        labels = ["Nombre", "Cédula", "Dirección", "Teléfono", "Plan", "Mensualidad"]
        self.edit_entries = {}
        for i, lab in enumerate(labels):
            tk.Label(self.form, text=lab+":", bg=BG).grid(row=i, column=0, sticky="e", padx=5, pady=3)
            e = tk.Entry(self.form, width=50)
            e.grid(row=i, column=1, padx=5, pady=3)
            val = contrato.get(lab.lower()) if lab.lower() in contrato else contrato.get(lab.lower(), "")
            # mensualidad special
            if lab == "Mensualidad":
                e.insert(0, str(contrato.get("mensualidad", "")))
            else:
                e.insert(0, contrato.get(lab.lower(), ""))
            self.edit_entries[lab.lower()] = e

        tk.Label(self.form, text=f"Estado actual: {contrato.get('estado')}", bg=BG).grid(row=6, column=0, columnspan=2, pady=5)

        # afiliados list
        tk.Label(self.form, text="Afiliados:", bg=BG).grid(row=7, column=0, sticky="ne", padx=5)
        self.afi_box = tk.Listbox(self.form, width=60, height=6)
        self.afi_box.grid(row=7, column=1, sticky="w")
        self.afi_data = contrato.get("afiliados", [])
        for a in self.afi_data:
            self.afi_box.insert(tk.END, f"{a['nombre']} {a['apellido']} ({a.get('parentesco','')}) - {a.get('telefono','')}")

        afi_buttons = tk.Frame(self.form, bg=BG)
        afi_buttons.grid(row=7, column=2, sticky="n", padx=5)
        tk.Button(afi_buttons, text="➕ Agregar", bg=GOLD, command=self.afi_agregar).pack(pady=3, fill="x")
        tk.Button(afi_buttons, text="✏️ Editar", bg="#BDBDBD", command=self.afi_editar).pack(pady=3, fill="x")
        tk.Button(afi_buttons, text="🗑 Eliminar", bg="#D9534F", command=self.afi_eliminar).pack(pady=3, fill="x")

        # action buttons
        actions = tk.Frame(self.form, bg=BG)
        actions.grid(row=8, column=0, columnspan=3, pady=12)
        tk.Button(actions, text="💾 Guardar Cambios", bg=GOLD, command=self.guardar_cambios).pack(side="left", padx=8)
        tk.Button(actions, text="⏸ Suspender", bg="#9A7AB0", command=lambda: self.cambiar_estado("Suspendido")).pack(side="left", padx=8)
        tk.Button(actions, text="🔄 Reactivar", bg="#4F81BD", command=lambda: self.cambiar_estado("Activo")).pack(side="left", padx=8)
        tk.Button(actions, text="❌ Cancelar Contrato", bg="#D9534F", command=lambda: self.cambiar_estado("Cancelado")).pack(side="left", padx=8)

    def afi_agregar(self):
        ventana = tk.Toplevel(self)
        ventana.title("Agregar Afiliado")
        ventana.geometry("350x280")
        tk.Label(ventana, text="Nombre:").pack(); e_nombre = tk.Entry(ventana); e_nombre.pack()
        tk.Label(ventana, text="Apellido:").pack(); e_apellido = tk.Entry(ventana); e_apellido.pack()
        tk.Label(ventana, text="Parentesco:").pack(); e_parent = tk.Entry(ventana); e_parent.pack()
        tk.Label(ventana, text="Teléfono:").pack(); e_tel = tk.Entry(ventana); e_tel.pack()
        def guardar():
            nombre = e_nombre.get().strip(); apellido = e_apellido.get().strip()
            parentesco = e_parent.get().strip(); telefono = e_tel.get().strip()
            if not nombre or not apellido:
                messagebox.showerror("Error", "Nombre y apellido obligatorios."); return
            afi = {"nombre": nombre, "apellido": apellido, "parentesco": parentesco, "telefono": telefono}
            self.afi_data.append(afi)
            self.afi_box.insert(tk.END, f"{nombre} {apellido} ({parentesco}) - {telefono}")
            ventana.destroy()
        tk.Button(ventana, text="Guardar", bg=GOLD, command=guardar).pack(pady=8)

    def afi_editar(self):
        sel = self.afi_box.curselection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione un afiliado.")
            return
        i = sel[0]
        afi = self.afi_data[i]
        ventana = tk.Toplevel(self)
        ventana.title("Editar Afiliado")
        ventana.geometry("350x280")
        tk.Label(ventana, text="Nombre:").pack(); e_nombre = tk.Entry(ventana); e_nombre.insert(0,afi["nombre"]); e_nombre.pack()
        tk.Label(ventana, text="Apellido:").pack(); e_apellido = tk.Entry(ventana); e_apellido.insert(0,afi["apellido"]); e_apellido.pack()
        tk.Label(ventana, text="Parentesco:").pack(); e_parent = tk.Entry(ventana); e_parent.insert(0,afi.get("parentesco","")); e_parent.pack()
        tk.Label(ventana, text="Teléfono:").pack(); e_tel = tk.Entry(ventana); e_tel.insert(0,afi.get("telefono","")); e_tel.pack()
        def guardar():
            nombre = e_nombre.get().strip(); apellido = e_apellido.get().strip()
            parentesco = e_parent.get().strip(); telefono = e_tel.get().strip()
            if not nombre or not apellido:
                messagebox.showerror("Error", "Nombre y apellido obligatorios."); return
            self.afi_data[i] = {"nombre": nombre, "apellido": apellido, "parentesco": parentesco, "telefono": telefono}
            self.afi_box.delete(i); self.afi_box.insert(i, f"{nombre} {apellido} ({parentesco}) - {telefono}")
            ventana.destroy()
        tk.Button(ventana, text="Guardar", bg=GOLD, command=guardar).pack(pady=8)

    def afi_eliminar(self):
        sel = self.afi_box.curselection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione un afiliado.")
            return
        i = sel[0]
        if messagebox.askyesno("Confirmar", "Eliminar afiliado?"):
            del self.afi_data[i]; self.afi_box.delete(i)

    def guardar_cambios(self):
        try:
            nuevos = {
                "nombre": self.edit_entries["nombre"].get().strip(),
                "cedula": self.edit_entries["cédula"].get().strip(),
                "direccion": self.edit_entries["dirección"].get().strip(),
                "telefono": self.edit_entries["teléfono"].get().strip(),
                "plan": self.edit_entries["plan"].get().strip(),
                "mensualidad": float(self.edit_entries["mensualidad"].get().strip()),
                "afiliados": self.afi_data
            }
            editar_contrato(self.current_id, nuevos)
            messagebox.showinfo("Éxito", "Contrato actualizado.")
            self.controller.show_frame("MenuFrame")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def cambiar_estado(self, estado):
        if messagebox.askyesno("Confirmar", f"¿Cambiar estado a {estado}?"):
            cambiar_estado(self.current_id, estado)
            messagebox.showinfo("Hecho", f"Contrato {estado}.")
            self.controller.show_frame("MenuFrame")


# ---------- REGISTRAR ABONO ----------
class RegistrarAbonoFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG)
        self.controller = controller
        top = tk.Frame(self, bg=BG); top.pack(fill="x", pady=8)
        tk.Button(top, text="🔙 Volver", bg="#BDBDBD", command=lambda: controller.show_frame("MenuFrame")).pack(side="left", padx=20)
        tk.Label(self, text="Registrar Abono", font=TITLE_FONT, bg=BG).pack(pady=5)

        body = tk.Frame(self, bg=BG); body.pack(pady=10)
        tk.Label(body, text="Buscar por ID o Cédula:", bg=BG).grid(row=0, column=0, sticky="e", padx=5)
        self.search = tk.Entry(body, width=30); self.search.grid(row=0, column=1, padx=5)
        tk.Button(body, text="Buscar", bg=GOLD, command=self.buscar_contrato).grid(row=0, column=2, padx=5)

        self.info_label = tk.Label(body, text="", bg=BG)
        self.info_label.grid(row=1, column=0, columnspan=3, pady=6)

        tk.Label(body, text="Monto:", bg=BG).grid(row=2, column=0, sticky="e", padx=5)
        self.entry_monto = tk.Entry(body); self.entry_monto.grid(row=2, column=1, padx=5)
        tk.Label(body, text="Observación:", bg=BG).grid(row=3, column=0, sticky="e", padx=5)
        self.entry_obs = tk.Entry(body, width=40); self.entry_obs.grid(row=3, column=1, columnspan=2, padx=5)

        tk.Button(self, text="💾 Guardar Abono", bg="#E8A317", command=self.guardar_abono).pack(pady=12)

    def buscar_contrato(self):
        key = self.search.get().strip()
        if not key:
            messagebox.showwarning("Atención", "Ingrese ID o cédula.")
            return
        contrato = None
        if key.isdigit():
            contrato = obtener_contrato_por_id(int(key))
        if not contrato:
            res = buscar_contrato_por_cedula(key)
            contrato = res[0] if res else None
        if contrato:
            self.current_id = contrato["id"]
            self.info_label.config(text=f"Contrato {contrato['id']} - {contrato['nombre']} - {contrato['plan']}")
        else:
            messagebox.showinfo("No encontrado", "Contrato no hallado.")

    def guardar_abono(self):
        try:
            contrato_id = getattr(self, "current_id", None)
            if contrato_id is None:
                messagebox.showwarning("Atención", "Busque un contrato primero.")
                return
            monto = float(self.entry_monto.get())
            obs = self.entry_obs.get().strip()
            agregar_abono(contrato_id, monto, obs)
            messagebox.showinfo("Éxito", "Abono registrado.")
            self.entry_monto.delete(0, tk.END); self.entry_obs.delete(0, tk.END)
            # auto backup already done in DB layer
        except ValueError:
            messagebox.showerror("Error", "Monto inválido.")
        except Exception as e:
            messagebox.showerror("Error", str(e))


# ---------- VER ABONOS ----------
class VerAbonosFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG)
        self.controller = controller
        top = tk.Frame(self, bg=BG); top.pack(fill="x", pady=8)
        tk.Button(top, text="🔙 Volver", bg="#BDBDBD", command=lambda: controller.show_frame("MenuFrame")).pack(side="left", padx=20)
        tk.Label(self, text="Ver Abonos Totales", font=TITLE_FONT, bg=BG).pack(pady=5)

        filter_frame = tk.Frame(self, bg=BG); filter_frame.pack(pady=8)
        tk.Label(filter_frame, text="Buscar por ID o Cédula:", bg=BG).pack(side="left", padx=5)
        self.search_ab = tk.Entry(filter_frame, width=30); self.search_ab.pack(side="left", padx=5)
        tk.Button(filter_frame, text="Buscar", bg=GOLD, command=self.buscar).pack(side="left", padx=5)
        tk.Button(filter_frame, text="Mostrar Todos", bg="#BDBDBD", command=self.mostrar_todos).pack(side="left", padx=5)

        cols = ("ID Abono", "ID Contrato", "Nombre", "Cédula", "Fecha", "Monto", "Observación")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=130)
        self.tree.pack(fill="both", expand=True, padx=10, pady=8)

        tk.Button(self, text="Exportar CSV", bg="#4F81BD", command=self.export_csv).pack(pady=6)

    def on_show(self):
        self.mostrar_todos()

    def mostrar_todos(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        abonos = obtener_abonos()
        for a in abonos:
            contrato = obtener_contrato_por_id(a["contrato_id"])
            nombre = contrato["nombre"] if contrato else ""
            cedula = contrato["cedula"] if contrato else ""
            self.tree.insert("", tk.END, values=(a["id"], a["contrato_id"], nombre, cedula, a["fecha"], a["monto"], a["observacion"]))

    def buscar(self):
        key = self.search_ab.get().strip()
        for i in self.tree.get_children():
            self.tree.delete(i)
        if not key:
            self.mostrar_todos(); return
        if key.isdigit():
            abonos = obtener_abonos(contrato_id=int(key))
        else:
            abonos = obtener_abonos(cedula=key)
        for a in abonos:
            contrato = obtener_contrato_por_id(a["contrato_id"])
            nombre = contrato["nombre"] if contrato else ""
            cedula = contrato["cedula"] if contrato else ""
            self.tree.insert("", tk.END, values=(a["id"], a["contrato_id"], nombre, cedula, a["fecha"], a["monto"], a["observacion"]))

    def export_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files","*.csv")])
        if not path:
            return
        import csv
        rows = []
        for a in self.tree.get_children():
            rows.append(self.tree.item(a)["values"])
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["ID Abono","ID Contrato","Nombre","Cédula","Fecha","Monto","Observación"])
            writer.writerows(rows)
        messagebox.showinfo("Exportado", f"CSV guardado en:\n{path}")


# ---------- CONTRATOS (lista por estado) ----------
class ContratosFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG)
        self.controller = controller
        top = tk.Frame(self, bg=BG); top.pack(fill="x", pady=8)
        tk.Button(top, text="🔙 Volver", bg="#BDBDBD", command=lambda: controller.show_frame("MenuFrame")).pack(side="left", padx=20)
        self.title_label = tk.Label(self, text="", font=TITLE_FONT, bg=BG); self.title_label.pack(pady=5)

        self.tree = ttk.Treeview(self, columns=("ID","Nombre","Cédula","Plan","Mensualidad","Estado","Fecha"), show="headings")
        for c in ("ID","Nombre","Cédula","Plan","Mensualidad","Estado","Fecha"):
            self.tree.heading(c, text=c)
            self.tree.column(c, width=130)
        self.tree.pack(fill="both", expand=True, padx=10, pady=8)
        self.tree.bind("<Double-1>", self.ver_detalle)

        btns = tk.Frame(self, bg=BG); btns.pack(pady=6)
        tk.Button(btns, text="✏️ Editar Contrato", bg="#4F81BD", command=self.editar_seleccionado).pack(side="left", padx=6)
        tk.Button(btns, text="💰 Registrar Abono", bg="#E8A317", command=self.registrar_para_seleccion).pack(side="left", padx=6)
        tk.Button(btns, text="⏸ Suspender", bg="#9A7AB0", command=lambda: self.cambiar_estado_seleccion("Suspendido")).pack(side="left", padx=6)
        tk.Button(btns, text="❌ Cancelar", bg="#D9534F", command=lambda: self.cambiar_estado_seleccion("Cancelado")).pack(side="left", padx=6)

    def set_estado(self, estado):
        self.estado = estado
        self.title_label.config(text=f"Contratos - {estado}")
        self.on_show()

    def on_show(self):
        # load datos
        for i in self.tree.get_children(): self.tree.delete(i)
        contratos = obtener_contratos(self.estado)
        for c in contratos:
            self.tree.insert("", tk.END, values=(c["id"], c["nombre"], c["cedula"], c["plan"], c["mensualidad"], c["estado"], c["fecha_inicio"]))

    def ver_detalle(self, event):
        sel = self.tree.selection()
        if not sel: return
        item = self.tree.item(sel[0])["values"]
        contrato_id = item[0]
        # open Edit frame with that id
        frame = self.controller.frames["EditarContratoFrame"]
        frame.search_entry.delete(0, tk.END)
        frame.search_entry.insert(0, str(contrato_id))
        frame.buscar()
        self.controller.show_frame("EditarContratoFrame")

    def editar_seleccionado(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione un contrato.")
            return
        contrato_id = self.tree.item(sel[0])["values"][0]
        frame = self.controller.frames["EditarContratoFrame"]
        frame.search_entry.delete(0, tk.END)
        frame.search_entry.insert(0, str(contrato_id))
        frame.buscar()
        self.controller.show_frame("EditarContratoFrame")

    def registrar_para_seleccion(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione un contrato.")
            return
        contrato_id = self.tree.item(sel[0])["values"][0]
        frame = self.controller.frames["RegistrarAbonoFrame"]
        frame.search.delete(0, tk.END); frame.search.insert(0, str(contrato_id))
        frame.buscar_contrato()
        self.controller.show_frame("RegistrarAbonoFrame")

    def cambiar_estado_seleccion(self, estado):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione un contrato.")
            return
        contrato_id = self.tree.item(sel[0])["values"][0]
        if messagebox.askyesno("Confirmar", f"¿Cambiar estado a {estado}?"):
            cambiar_estado(contrato_id, estado)
            messagebox.showinfo("Hecho", "Estado actualizado.")
            self.on_show()


# ---------- Lanzar app ----------
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
