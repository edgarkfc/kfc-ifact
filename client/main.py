import requests
import dearpygui.dearpygui as dpg

# Consultar el servidor (como axios o fetch)
response = requests.get('http://localhost:5000/api/status')
data = response.json()

# Crear interfaz gráfica
dpg.create_context()

with dpg.window(label="Monitor", width=400, height=200):
    dpg.add_text(f"Estado del servidor: {data['status']}")
    dpg.add_text(f"Versión: {data['version']}")

dpg.create_viewport(title='Cliente Escritorio', width=400, height=200)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()