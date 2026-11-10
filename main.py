import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database import conectar, crear_tablas


# ==========================================
# CONFIGURACIÓN GENERAL
# ==========================================

crear_tablas()

VENTANA = tk.Tk()
VENTANA.title("PARKING SMART - Sistema de Parqueo")
VENTANA.geometry("1250x780")
VENTANA.minsize(1100, 700)
VENTANA.configure(bg="#F1F5F9")

COLOR_PRINCIPAL = "#172554"
COLOR_AZUL = "#2563EB"
COLOR_ROJO = "#DC2626"
COLOR_VERDE = "#0F766E"
COLOR_MORADO = "#7C3AED"
COLOR_FONDO = "#F1F5F9"

CAPACIDAD = 30
TARIFA_HORA = 0.50


# ==========================================
# ENCABEZADO
# ==========================================

encabezado = tk.Frame(
    VENTANA,
    bg=COLOR_PRINCIPAL,
    height=85
)
encabezado.pack(fill="x")
encabezado.pack_propagate(False)

tk.Label(
    encabezado,
    text="🚗 PARKING SMART",
    font=("Arial", 25, "bold"),
    bg=COLOR_PRINCIPAL,
    fg="white"
).pack(side="left", padx=30)

tk.Label(
    encabezado,
    text="Sistema de Gestión de Parqueos",
    font=("Arial", 13),
    bg=COLOR_PRINCIPAL,
    fg="white"
).pack(side="right", padx=30)


# ==========================================
# CONTENEDOR PRINCIPAL
# ==========================================

contenido = tk.Frame(
    VENTANA,
    bg=COLOR_FONDO
)

contenido.pack(
    fill="both",
    expand=True,
    padx=25,
    pady=15
)


tk.Label(
    contenido,
    text="Panel de administración",
    font=("Arial", 22, "bold"),
    bg=COLOR_FONDO,
    fg=COLOR_PRINCIPAL
).pack(anchor="w", pady=8)


# ==========================================
# TARJETAS INFORMATIVAS
# ==========================================

tarjetas = tk.Frame(
    contenido,
    bg=COLOR_FONDO
)

tarjetas.pack(fill="x", pady=8)


def crear_tarjeta(titulo, valor):

    tarjeta = tk.Frame(
        tarjetas,
        bg="white",
        height=90,
        highlightbackground="#CBD5E1",
        highlightthickness=1
    )

    tarjeta.pack(
        side="left",
        padx=8,
        fill="x",
        expand=True
    )

    tarjeta.pack_propagate(False)

    tk.Label(
        tarjeta,
        text=titulo,
        font=("Arial", 11),
        bg="white",
        fg="#64748B"
    ).pack(pady=(12, 3))

    etiqueta = tk.Label(
        tarjeta,
        text=valor,
        font=("Arial", 22, "bold"),
        bg="white",
        fg=COLOR_AZUL
    )

    etiqueta.pack()

    return etiqueta


total_vehiculos = crear_tarjeta(
    "VEHÍCULOS REGISTRADOS", "0"
)

vehiculos_dentro = crear_tarjeta(
    "VEHÍCULOS EN PARQUEO", "0"
)

espacios_libres = crear_tarjeta(
    "ESPACIOS DISPONIBLES", "30"
)


# ==========================================
# FORMULARIO DE ENTRADA
# ==========================================

formulario = tk.LabelFrame(
    contenido,
    text=" Registrar entrada de vehículo ",
    font=("Arial", 12, "bold"),
    bg="white",
    fg=COLOR_PRINCIPAL,
    padx=10,
    pady=10
)

formulario.pack(fill="x", pady=10)


tk.Label(
    formulario,
    text="Número de placa:",
    bg="white",
    font=("Arial", 11)
).grid(row=0, column=0, padx=5, pady=10)


entrada_placa = tk.Entry(
    formulario,
    font=("Arial", 12),
    width=17
)

entrada_placa.grid(row=0, column=1, padx=5)


tk.Label(
    formulario,
    text="Tipo de vehículo:",
    bg="white",
    font=("Arial", 11)
).grid(row=0, column=2, padx=5)


tipo_vehiculo = ttk.Combobox(
    formulario,
    values=[
        "Automóvil",
        "Motocicleta",
        "Camioneta",
        "Camión"
    ],
    state="readonly",
    font=("Arial", 11),
    width=15
)

tipo_vehiculo.grid(row=0, column=3, padx=5)
tipo_vehiculo.set("Automóvil")


# ==========================================
# FUNCIONES PRINCIPALES
# ==========================================

def actualizar_tabla():

    for elemento in tabla.get_children():
        tabla.delete(elemento)

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT id, placa, tipo, hora_entrada, estado
        FROM vehiculos
        WHERE estado = 'Dentro'
        ORDER BY id DESC
    """)

    vehiculos = cursor.fetchall()

    for vehiculo in vehiculos:

        tabla.insert(
            "",
            "end",
            values=vehiculo
        )

    cursor.execute(
        "SELECT COUNT(*) FROM vehiculos"
    )

    total = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM vehiculos
        WHERE estado = 'Dentro'
    """)

    dentro = cursor.fetchone()[0]

    conexion.close()

    total_vehiculos.config(text=str(total))

    vehiculos_dentro.config(text=str(dentro))

    espacios_libres.config(
        text=str(max(0, CAPACIDAD - dentro))
    )


# ==========================================
# REGISTRAR ENTRADA
# ==========================================

def registrar_vehiculo():

    placa = entrada_placa.get().strip().upper()

    tipo = tipo_vehiculo.get()

    if not placa:

        messagebox.showwarning(
            "Advertencia",
            "Ingrese el número de placa."
        )

        return

    if len(placa) > 15:

        messagebox.showwarning(
            "Advertencia",
            "La placa no puede superar 15 caracteres."
        )

        return

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT id
        FROM vehiculos
        WHERE placa = ?
        AND estado = 'Dentro'
    """, (placa,))

    if cursor.fetchone():

        conexion.close()

        messagebox.showwarning(
            "Vehículo existente",
            "Este vehículo ya está dentro del parqueo."
        )

        return

    cursor.execute("""
        SELECT COUNT(*)
        FROM vehiculos
        WHERE estado = 'Dentro'
    """)

    cantidad = cursor.fetchone()[0]

    if cantidad >= CAPACIDAD:

        conexion.close()

        messagebox.showwarning(
            "Parqueo lleno",
            "No hay espacios disponibles."
        )

        return

    hora = datetime.now().strftime(
        "%d/%m/%Y %H:%M:%S"
    )

    cursor.execute("""
        INSERT INTO vehiculos
        (placa, tipo, hora_entrada, estado)
        VALUES (?, ?, ?, 'Dentro')
    """, (placa, tipo, hora))

    conexion.commit()
    conexion.close()

    entrada_placa.delete(0, tk.END)

    actualizar_tabla()

    messagebox.showinfo(
        "Registro exitoso",
        f"Vehículo {placa} registrado correctamente."
    )


# ==========================================
# REGISTRAR SALIDA
# ==========================================

def registrar_salida():

    seleccionado = tabla.selection()

    if not seleccionado:

        messagebox.showwarning(
            "Advertencia",
            "Seleccione un vehículo de la tabla."
        )

        return

    datos = tabla.item(seleccionado[0])

    id_vehiculo = datos["values"][0]

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT placa, hora_entrada
        FROM vehiculos
        WHERE id = ?
        AND estado = 'Dentro'
    """, (id_vehiculo,))

    vehiculo = cursor.fetchone()

    if vehiculo is None:

        conexion.close()
        actualizar_tabla()
        return

    placa, hora_entrada = vehiculo

    formato = "%d/%m/%Y %H:%M:%S"

    entrada = datetime.strptime(
        hora_entrada,
        formato
    )

    salida = datetime.now()

    segundos = int(
        (salida - entrada).total_seconds()
    )

    horas = max(
        1,
        (segundos + 3599) // 3600
    )

    costo = horas * TARIFA_HORA

    hora_salida = salida.strftime(formato)

    cursor.execute("""
        UPDATE vehiculos
        SET hora_salida = ?,
            costo = ?,
            estado = 'Fuera'
        WHERE id = ?
    """, (
        hora_salida,
        costo,
        id_vehiculo
    ))

    conexion.commit()
    conexion.close()

    actualizar_tabla()

    messagebox.showinfo(
        "Salida registrada",
        f"Vehículo: {placa}\n\n"
        f"Tiempo: {horas} hora(s)\n"
        f"Tarifa: ${TARIFA_HORA:.2f}\n\n"
        f"TOTAL A PAGAR: ${costo:.2f}"
    )


# ==========================================
# BOTONES DE ENTRADA Y SALIDA
# ==========================================

tk.Button(
    formulario,
    text="+ REGISTRAR ENTRADA",
    font=("Arial", 10, "bold"),
    bg=COLOR_AZUL,
    fg="white",
    relief="flat",
    cursor="hand2",
    command=registrar_vehiculo
).grid(row=0, column=4, padx=8, pady=10)


tk.Button(
    formulario,
    text="REGISTRAR SALIDA",
    font=("Arial", 10, "bold"),
    bg=COLOR_ROJO,
    fg="white",
    relief="flat",
    cursor="hand2",
    command=registrar_salida
).grid(row=0, column=5, padx=8, pady=10)


# ==========================================
# MÓDULO DE HISTORIAL
# ==========================================

def abrir_historial():

    ventana = tk.Toplevel(VENTANA)

    ventana.title("Historial de vehículos - PARKING SMART")
    ventana.geometry("1100x550")
    ventana.configure(bg=COLOR_FONDO)

    tk.Label(
        ventana,
        text="HISTORIAL DE VEHÍCULOS",
        font=("Arial", 22, "bold"),
        bg=COLOR_FONDO,
        fg=COLOR_PRINCIPAL
    ).pack(pady=20)

    columnas = (
        "ID", "PLACA", "TIPO",
        "ENTRADA", "SALIDA",
        "COSTO", "ESTADO"
    )

    marco = tk.Frame(ventana)
    marco.pack(fill="both", expand=True, padx=20, pady=10)

    historial = ttk.Treeview(
        marco,
        columns=columnas,
        show="headings"
    )

    for columna in columnas:

        historial.heading(
            columna,
            text=columna
        )

        historial.column(
            columna,
            anchor="center",
            width=145
        )

    historial.pack(
        side="left",
        fill="both",
        expand=True
    )

    scroll = ttk.Scrollbar(
        marco,
        orient="vertical",
        command=historial.yview
    )

    historial.configure(
        yscrollcommand=scroll.set
    )

    scroll.pack(side="right", fill="y")

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT id, placa, tipo,
               hora_entrada, hora_salida,
               costo, estado
        FROM vehiculos
        ORDER BY id DESC
    """)

    for registro in cursor.fetchall():

        historial.insert(
            "",
            "end",
            values=(
                registro[0],
                registro[1],
                registro[2],
                registro[3],
                registro[4] or "Pendiente",
                f"${registro[5]:.2f}",
                registro[6]
            )
        )

    conexion.close()

    tk.Button(
        ventana,
        text="CERRAR HISTORIAL",
        font=("Arial", 11, "bold"),
        bg=COLOR_PRINCIPAL,
        fg="white",
        relief="flat",
        command=ventana.destroy
    ).pack(pady=15)


# ==========================================
# MÓDULO DE REPORTES
# ==========================================

def abrir_reportes():

    ventana = tk.Toplevel(VENTANA)

    ventana.title("Reportes - PARKING SMART")
    ventana.geometry("950x650")
    ventana.configure(bg=COLOR_FONDO)

    tk.Label(
        ventana,
        text="REPORTES Y ESTADÍSTICAS",
        font=("Arial", 22, "bold"),
        bg=COLOR_FONDO,
        fg=COLOR_PRINCIPAL
    ).pack(pady=20)

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT COALESCE(SUM(costo), 0)
        FROM vehiculos
        WHERE estado = 'Fuera'
    """)

    ingresos_totales = cursor.fetchone()[0]

    hoy = datetime.now().strftime("%d/%m/%Y")

    cursor.execute("""
        SELECT COALESCE(SUM(costo), 0)
        FROM vehiculos
        WHERE estado = 'Fuera'
        AND substr(hora_salida, 1, 10) = ?
    """, (hoy,))

    ingresos_dia = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM vehiculos
        WHERE estado = 'Fuera'
    """)

    salieron = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM vehiculos
        WHERE estado = 'Dentro'
    """)

    dentro = cursor.fetchone()[0]

    conexion.close()

    tarjetas_reporte = tk.Frame(
        ventana,
        bg=COLOR_FONDO
    )

    tarjetas_reporte.pack(fill="x", padx=15)

    def tarjeta(titulo, valor):

        marco = tk.Frame(
            tarjetas_reporte,
            bg="white",
            height=100,
            highlightbackground="#CBD5E1",
            highlightthickness=1
        )

        marco.pack(
            side="left",
            fill="x",
            expand=True,
            padx=6
        )

        marco.pack_propagate(False)

        tk.Label(
            marco,
            text=titulo,
            bg="white",
            fg="#64748B",
            font=("Arial", 10)
        ).pack(pady=(15, 5))

        tk.Label(
            marco,
            text=valor,
            bg="white",
            fg=COLOR_AZUL,
            font=("Arial", 19, "bold")
        ).pack()

    tarjeta("INGRESOS TOTALES", f"${ingresos_totales:.2f}")

    tarjeta("INGRESOS DEL DÍA", f"${ingresos_dia:.2f}")

    tarjeta("VEHÍCULOS QUE SALIERON", str(salieron))

    tarjeta("VEHÍCULOS DENTRO", str(dentro))

    # GRÁFICA

    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

    figura = Figure(figsize=(8, 4), dpi=100)

    grafica = figura.add_subplot(111)

    grafica.bar(
        ["Ingresos totales", "Ingresos del día"],
        [ingresos_totales, ingresos_dia]
    )

    grafica.set_title("Ingresos del parqueo")
    grafica.set_ylabel("Dinero ($)")

    figura.tight_layout()

    lienzo = FigureCanvasTkAgg(
        figura,
        master=ventana
    )

    lienzo.draw()

    lienzo.get_tk_widget().pack(
        fill="both",
        expand=True,
        padx=20,
        pady=15
    )

    tk.Button(
        ventana,
        text="CERRAR REPORTES",
        font=("Arial", 11, "bold"),
        bg=COLOR_PRINCIPAL,
        fg="white",
        relief="flat",
        command=ventana.destroy
    ).pack(pady=12)


# ==========================================
# BUSCADOR DE VEHÍCULOS
# ==========================================

def buscar_vehiculo():

    placa = entrada_busqueda.get().strip().upper()

    if not placa:

        messagebox.showwarning(
            "Advertencia",
            "Ingrese una placa para buscar."
        )

        return

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT id, placa, tipo,
               hora_entrada, hora_salida,
               costo, estado
        FROM vehiculos
        WHERE placa LIKE ?
        ORDER BY id DESC
    """, (f"%{placa}%",))

    resultados = cursor.fetchall()

    conexion.close()

    for elemento in tabla_busqueda.get_children():
        tabla_busqueda.delete(elemento)

    for registro in resultados:

        tabla_busqueda.insert(
            "",
            "end",
            values=(
                registro[0],
                registro[1],
                registro[2],
                registro[3],
                registro[4] or "Pendiente",
                f"${registro[5]:.2f}",
                registro[6]
            )
        )

    if not resultados:

        messagebox.showinfo(
            "Búsqueda",
            "No se encontraron vehículos."
        )


def abrir_buscador():

    global entrada_busqueda, tabla_busqueda

    ventana = tk.Toplevel(VENTANA)

    ventana.title("Buscar vehículos - PARKING SMART")
    ventana.geometry("1050x500")
    ventana.configure(bg=COLOR_FONDO)

    tk.Label(
        ventana,
        text="BUSCAR VEHÍCULOS",
        font=("Arial", 22, "bold"),
        bg=COLOR_FONDO,
        fg=COLOR_PRINCIPAL
    ).pack(pady=20)

    marco_busqueda = tk.Frame(
        ventana,
        bg=COLOR_FONDO
    )

    marco_busqueda.pack(pady=10)

    tk.Label(
        marco_busqueda,
        text="Número de placa:",
        font=("Arial", 11),
        bg=COLOR_FONDO
    ).pack(side="left", padx=10)

    entrada_busqueda = tk.Entry(
        marco_busqueda,
        font=("Arial", 12),
        width=20
    )

    entrada_busqueda.pack(side="left", padx=10)

    tk.Button(
        marco_busqueda,
        text="BUSCAR",
        bg=COLOR_AZUL,
        fg="white",
        font=("Arial", 10, "bold"),
        relief="flat",
        command=buscar_vehiculo
    ).pack(side="left", padx=10)

    columnas = (
        "ID", "PLACA", "TIPO",
        "ENTRADA", "SALIDA",
        "COSTO", "ESTADO"
    )

    tabla_busqueda = ttk.Treeview(
        ventana,
        columns=columnas,
        show="headings",
        height=10
    )

    for columna in columnas:

        tabla_busqueda.heading(
            columna,
            text=columna
        )

        tabla_busqueda.column(
            columna,
            anchor="center",
            width=140
        )

    tabla_busqueda.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=15
    )


# ==========================================
# BARRA DE MÓDULOS
# ==========================================

barra_modulos = tk.Frame(
    contenido,
    bg=COLOR_FONDO
)

barra_modulos.pack(fill="x", pady=8)


tk.Button(
    barra_modulos,
    text="📋 HISTORIAL",
    font=("Arial", 10, "bold"),
    bg=COLOR_VERDE,
    fg="white",
    relief="flat",
    cursor="hand2",
    command=abrir_historial
).pack(side="left", padx=5, expand=True, fill="x")


tk.Button(
    barra_modulos,
    text="📊 REPORTES",
    font=("Arial", 10, "bold"),
    bg=COLOR_MORADO,
    fg="white",
    relief="flat",
    cursor="hand2",
    command=abrir_reportes
).pack(side="left", padx=5, expand=True, fill="x")


tk.Button(
    barra_modulos,
    text="🔎 BUSCAR VEHÍCULO",
    font=("Arial", 10, "bold"),
    bg="#475569",
    fg="white",
    relief="flat",
    cursor="hand2",
    command=abrir_buscador
).pack(side="left", padx=5, expand=True, fill="x")


# ==========================================
# TABLA DE VEHÍCULOS ACTIVOS
# ==========================================

tk.Label(
    contenido,
    text="Vehículos actualmente en el parqueo",
    font=("Arial", 15, "bold"),
    bg=COLOR_FONDO,
    fg=COLOR_PRINCIPAL
).pack(anchor="w", pady=8)


tabla_frame = tk.Frame(contenido)

tabla_frame.pack(
    fill="both",
    expand=True
)


columnas = (
    "ID",
    "PLACA",
    "TIPO",
    "HORA DE ENTRADA",
    "ESTADO"
)

tabla = ttk.Treeview(
    tabla_frame,
    columns=columnas,
    show="headings",
    height=8
)

for columna in columnas:

    tabla.heading(
        columna,
        text=columna
    )

    tabla.column(
        columna,
        anchor="center",
        width=180
    )

tabla.pack(
    fill="both",
    expand=True
)


# ==========================================
# INICIAR SISTEMA
# ==========================================

actualizar_tabla()

VENTANA.mainloop()