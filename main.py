import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel,QScrollArea,QTextEdit
from PyQt6.QtCore import Qt
import struct
import time
import os
from PyQt6.QtGui import QMovie

class EditorTexto(QWidget):
    def __init__(self, archivo):
        super().__init__()

        self.setWindowTitle("Editor de Texto")
        self.setGeometry(100, 100, 600, 400)

        self.layout = QVBoxLayout()

        self.text_edit = QTextEdit(self)

        self.boton_guardar = QPushButton("Guardar Cambios", self)
        self.boton_guardar.clicked.connect(self.guardar_cambios)

        self.boton_abrir = QPushButton("Abrir Archivo", self)
        self.boton_abrir.clicked.connect(self.abrir_archivo)

        self.label_archivo = QLabel("Archivo no abierto", self)

        self.layout.addWidget(self.label_archivo)
        self.layout.addWidget(self.text_edit)
        self.layout.addWidget(self.boton_abrir)
        self.layout.addWidget(self.boton_guardar)

        self.setLayout(self.layout)

        self.archivo_abierto = archivo

        self.abrir_archivo()

    def abrir_archivo(self):
        try:
            with open("informacion.txt", 'r', encoding='ISO-8859-1') as file:
                contenido = file.read()
                self.text_edit.setText(contenido)
                self.label_archivo.setText(f"Archivo abierto: {self.archivo_abierto}")
        except Exception as e:
            self.label_archivo.setText(f"Error al abrir el archivo: {e}")


    def guardar_cambios(self):
        try:
            with open("informacion.txt", 'w', encoding='ISO-8859-1') as file:
                contenido = self.text_edit.toPlainText()
                file.write(contenido)
                self.label_archivo.setText(f"Archivo guardado: {self.archivo_abierto}")
        except Exception as e:
            self.label_archivo.setText(f"Error al guardar el archivo: {e}")
class MiVentana(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Analizador de archivos gif")
        self.setGeometry(100, 100, 800, 700)
        self.layout = QVBoxLayout()
        self.boton_carpeta = QPushButton("Seleccionar carpeta", self)
        self.boton_carpeta.clicked.connect(self.seleccionar_archivo)
        self.boton_txt = QPushButton("Ver txt", self)
        self.boton_txt.clicked.connect(self.abrir_editor)
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(QWidget())
        self.scroll_area.widget().setLayout(QVBoxLayout())
        self.label_carpeta = QLabel("Ningún archivo seleccionado", self)

        self.layout.addWidget(self.boton_carpeta)
        self.layout.addWidget(self.boton_txt)
        self.layout.addWidget(self.label_carpeta)
        self.layout.addWidget(self.scroll_area)

        self.setLayout(self.layout)

    def seleccionar_archivo(self):
        carpeta = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta", "")

        if carpeta:
            self.label_carpeta.setText(f"Carpeta seleccionada: {carpeta}")
            archivos = listar_archivos_gif(carpeta)
            contador = 1
            layout2 = self.scroll_area.widget().layout()
            for i in archivos:
                try:
                    gif_info = leer_gif(i)
                    print("===============================================================")
                    print("GIF numero: ",contador)
                    imprimir_info_gif(gif_info)
                    contador += 1
                    movie = QMovie(i)
                    label = QLabel(self)
                    label.setMovie(movie)
                    movie.start()
                    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    layout2.addWidget(label)
                    self.scroll_area.widget().setLayout(layout2)
                    contenido = ""
                    try:
                        with open('informacion.txt', 'r') as archivo:
                            contenido += archivo.read()
                    except:
                        pass

                    with open('informacion.txt', 'w') as archivo:
                        archivo.write(contenido)
                        archivo.write("===============================================================\n")
                        n_cont = contador - 1
                        info = "GIF numero: "+str(n_cont)+"\n"
                        archivo.write(info)
                        archivo.write(obtener_info_gif(gif_info))
                except ValueError as e:
                    print(f"Error: {e}")

    def abrir_editor(self):
        archivo ="informacion.txt"
        self.editor = EditorTexto(archivo)
        self.editor.show()

def leer_gif(file_path):
    with open(file_path, 'rb') as f:
        header = f.read(6)
        if header[:3] != b'GIF':
            raise ValueError("No es un archivo GIF válido")
        version = header[3:].decode('ascii')
        logical_screen_descriptor = f.read(7)
        width, height = struct.unpack('<HH', logical_screen_descriptor[:4])
        flags = logical_screen_descriptor[4]
        global_color_table_flag = flags & 0x80
        color_resolution = (flags >> 4) & 0x07
        sort_flag = (flags >> 3) & 0x01
        global_color_table_size = 2 ** ((flags & 0x07) + 1) if global_color_table_flag else 0
        background_color_index = logical_screen_descriptor[5]
        global_palette = None
        if global_color_table_flag:
            global_palette = f.read(global_color_table_size * 3)  # 3 bytes por color (RGB)
        comments = []
        image_count = 0
        while True:
            block = f.read(1)
            if block == b'\x21':
                block_type = f.read(1)
                if block_type == b'\xfe':
                    comment_size = ord(f.read(1))
                    comment = f.read(comment_size)
                    comments.append(comment.decode('ascii', 'ignore'))
                elif block_type == b'\xf9':
                    f.read(1)
                else:
                    break
            if block == b'\x2c':
                image_count += 1
                f.read(9)
                lzw_min_code_size = ord(f.read(1))
                while True:
                    sub_block_size = ord(f.read(1))
                    if sub_block_size == 0:
                        break
                    f.read(sub_block_size)
            else:
                break
        file_info = os.stat(file_path)
        creation_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(file_info.st_ctime))
        modification_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(file_info.st_mtime))
        return {
            'version': version,
            'width': width,
            'height': height,
            'global_color_table_flag': global_color_table_flag,
            'global_color_table_size': global_color_table_size,
            'background_color_index': background_color_index,
            'comments': comments,
            'creation_time': creation_time,
            'modification_time': modification_time,
            'compression_type': 'LZW',
            'color_format': 'RGB o Index',
            'image_count': contar_imagenes_gif(file_path)
        }


def imprimir_info_gif(gif_info):
    print(f"Versión GIF: {gif_info['version']}")
    print(f"Tamaño de imagen: {gif_info['width']}x{gif_info['height']}")
    print(f"Cantidad de colores (Global Color Table): {gif_info['global_color_table_size']}")
    print(f"Color de fondo (índice): {gif_info['background_color_index']}")
    print(f"Tipo de compresión: {gif_info['compression_type']}")
    print(f"Formato numérico (representación de colores): {gif_info['color_format']}")
    print(f"Cantidad de imágenes: {gif_info['image_count']}")
    print(f"Fecha de creación: {gif_info['creation_time']}")
    print(f"Fecha de modificación: {gif_info['modification_time']}")
    print("Comentarios agregados:")
    for comment in gif_info['comments']:
        print(f"  - {comment}")


def obtener_info_gif(gif_info):
    info = ""
    info += f"Versión GIF: {gif_info['version']}\n"
    info += f"Tamaño de imagen: {gif_info['width']}x{gif_info['height']}\n"
    info += f"Cantidad de colores (Global Color Table): {gif_info['global_color_table_size']}\n"
    info += f"Color de fondo (índice): {gif_info['background_color_index']}\n"
    info += f"Tipo de compresión: {gif_info['compression_type']}\n"
    info += f"Formato numérico (representación de colores): {gif_info['color_format']}\n"
    info += f"Cantidad de imágenes: {gif_info['image_count']}\n"
    info += f"Fecha de creación: {gif_info['creation_time']}\n"
    info += f"Fecha de modificación: {gif_info['modification_time']}\n"
    info += "Comentarios agregados:\n"
    for comment in gif_info['comments']:
        info += f"  - {comment}\n"
    return info


def contar_imagenes_gif(archivo_gif):
    with open(archivo_gif, 'rb') as f:
        contenido = f.read()
    contador_fotogramas = 0
    i = 0
    if contenido[0:3] != b'GIF':
        raise ValueError("El archivo no es un GIF válido")
    while i < len(contenido):
        if contenido[i] == 0x2C:
            contador_fotogramas += 1
            i += 9
            if contenido[i] == 0xF9:
                i += 1 + 4
        else:
            i += 1

    return contador_fotogramas


def listar_archivos_gif(carpeta):
    archivos_gif = []

    for carpeta_raiz, directorios, archivos in os.walk(carpeta):
        for archivo in archivos:
            if archivo.lower().endswith(".gif"):
                ruta_completa = os.path.join(carpeta_raiz, archivo)
                archivos_gif.append(ruta_completa)

    return archivos_gif

def conprobar_existencia():
    try:
        with open("informacion.txt", 'r', encoding='ISO-8859-1') as archivo:
            lineas = archivo.readlines()

    except:
        with open("informacion.txt", 'w', encoding='ISO-8859-1') as archivo:
            archivo.write("")
def main():
    conprobar_existencia()

    app = QApplication(sys.argv)
    ventana = MiVentana()
    ventana.show()
    sys.exit(app.exec())


main()