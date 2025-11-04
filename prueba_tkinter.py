import tkinter as tk

ventana = tk.Tk()
ventana.title("Prueba Tkinter")
ventana.geometry("300x200")

etiqueta = tk.Label(ventana, text="¡Tkinter está funcionando!", font=("Arial", 12))
etiqueta.pack(pady=50)

ventana.mainloop()