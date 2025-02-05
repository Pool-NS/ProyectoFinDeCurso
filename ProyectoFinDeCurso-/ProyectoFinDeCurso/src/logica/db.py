import sqlite3
import hashlib
import tkinter as tk
from tkinter import simpledialog

class DB:
    @staticmethod
    def inicializar_db():
        """Inicializa todas las tablas necesarias en la base de datos."""
        try:
            conexion = sqlite3.connect("usuarios.db")
            cursor = conexion.cursor()

            # Crear tabla de usuarios
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    alias TEXT NOT NULL UNIQUE,
                    correo TEXT NOT NULL UNIQUE,
                    contrasena TEXT NOT NULL
                )
            """)

            # Crear tabla de preguntas de seguridad
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS preguntas_seguridad (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    idUsuario INTEGER NOT NULL,
                    pregunta TEXT NOT NULL,
                    respuesta TEXT NOT NULL,
                    FOREIGN KEY (idUsuario) REFERENCES usuarios(id)
                )
            """)

            # Crear tabla de categorías de contraseñas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS categorias_contraseñas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    idUsuario INTEGER NOT NULL,
                    categoria TEXT NOT NULL,
                    FOREIGN KEY (idUsuario) REFERENCES usuarios(id)
                )
            """)

            # Crear tabla de contraseñas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS contraseñas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    idCategoria INTEGER NOT NULL,
                    contraseña TEXT NOT NULL,
                    FOREIGN KEY (idCategoria) REFERENCES categorias_contraseñas(id)
                )
            """)

            # Confirmar los cambios y cerrar la conexión
            conexion.commit()
            conexion.close()
            print("Base de datos inicializada correctamente.")
        except sqlite3.Error as e:
            print(f"Error al inicializar la base de datos: {e}")

    @staticmethod
    def insertar_usuario(nombre, alias, correo, contrasena):
        """Inserta un nuevo usuario en la base de datos."""
        try:
            # Encriptar la contraseña antes de almacenarla
            contrasena_hash = hashlib.sha256(contrasena.encode('utf-8')).hexdigest()

            conexion = sqlite3.connect("usuarios.db")
            cursor = conexion.cursor()

            # Insertar el usuario en la base de datos
            cursor.execute("""
                INSERT INTO usuarios (nombre, alias, correo, contrasena)
                VALUES (?, ?, ?, ?)
            """, (nombre, alias, correo, contrasena_hash))

            conexion.commit()
            conexion.close()
            print("Usuario registrado correctamente.")
        except sqlite3.IntegrityError as e:
            print(f"Error de integridad: {e}")
        except sqlite3.Error as e:
            print(f"Error al insertar usuario: {e}")

    @staticmethod
    def agregar_preguntas_seguridad(id_usuario, preguntas_respuestas):
        """Agrega las preguntas de seguridad de un usuario."""
        try:
            conexion = sqlite3.connect("usuarios.db")
            cursor = conexion.cursor()

            # Verificar si el usuario existe
            cursor.execute("SELECT id FROM usuarios WHERE id = ?", (id_usuario,))
            usuario = cursor.fetchone()

            if not usuario:
                print(f"Usuario con ID {id_usuario} no encontrado.")
                return False

            # Insertar las preguntas y respuestas en la base de datos
            for pregunta, respuesta in preguntas_respuestas:
                cursor.execute("""
                    INSERT INTO preguntas_seguridad (idUsuario, pregunta, respuesta)
                    VALUES (?, ?, ?)
                """, (id_usuario, pregunta, respuesta))  # Respuesta no encriptada

            conexion.commit()
            conexion.close()
            print("Preguntas de seguridad agregadas correctamente.")
            return True

        except sqlite3.Error as e:
            print(f"Error al agregar preguntas de seguridad: {e}")
            return False
        finally:
            conexion.close()

    @staticmethod
    def obtener_preguntas(correo):
        """Obtiene las preguntas de seguridad para un correo dado."""
        try:
            conexion = sqlite3.connect("usuarios.db")
            cursor = conexion.cursor()

            # Buscar el ID del usuario por correo
            cursor.execute("""
                SELECT id FROM usuarios WHERE correo = ?
            """, (correo,))
            usuario = cursor.fetchone()

            if usuario:
                id_usuario = usuario[0]
                # Obtener las preguntas de seguridad del usuario
                cursor.execute("""
                    SELECT pregunta FROM preguntas_seguridad WHERE idUsuario = ?
                """, (id_usuario,))
                preguntas = cursor.fetchall()
                conexion.close()
                return [pregunta[0] for pregunta in preguntas]  # Devolver solo las preguntas
            else:
                conexion.close()
                print(f"Usuario con correo {correo} no encontrado.")
                return None  # No se encontró un usuario con ese correo

        except sqlite3.Error as e:
            print(f"Error al obtener las preguntas de seguridad: {e}")
            return None

    @staticmethod
    def verificar_respuestas(correo, respuestas_usuario):
        """Verifica si las respuestas del usuario son correctas."""
        try:
            conexion = sqlite3.connect("usuarios.db")
            cursor = conexion.cursor()

            # Buscar el ID del usuario por correo
            cursor.execute("""
                SELECT id FROM usuarios WHERE correo = ?
            """, (correo,))
            usuario = cursor.fetchone()

            if usuario:
                id_usuario = usuario[0]
                cursor.execute("""
                    SELECT pregunta, respuesta FROM preguntas_seguridad WHERE idUsuario = ?
                """, (id_usuario,))
                preguntas = cursor.fetchall()

                # Verificar que el número de respuestas coincide
                if len(preguntas) != len(respuestas_usuario):
                    print("El número de respuestas no coincide con el número de preguntas.")
                    return False

                # Verificar cada respuesta
                for i, (pregunta, respuesta_almacenada) in enumerate(preguntas):
                    if respuestas_usuario[i] != respuesta_almacenada:
                        print(f"Respuesta incorrecta para la pregunta: {pregunta}")
                        return False  # Si alguna respuesta no coincide

                print("Todas las respuestas son correctas.")
                return True  # Si todas las respuestas son correctas
            else:
                print(f"Usuario con correo {correo} no encontrado.")
                return False  # No se encontró un usuario con ese correo
        except sqlite3.Error as e:
            print(f"Error al verificar respuestas: {e}")
            return False
        finally:
            conexion.close()

    @staticmethod
    def obtener_preguntas_por_usuario(id_usuario):
        """Obtiene las preguntas de seguridad para un usuario dado su idUsuario."""
        try:
            conexion = sqlite3.connect("usuarios.db")
            cursor = conexion.cursor()

            cursor.execute("""
                SELECT pregunta, respuesta FROM preguntas_seguridad WHERE idUsuario = ?
            """, (id_usuario,))
            preguntas = cursor.fetchall()

            conexion.close()
            return preguntas

        except sqlite3.Error as e:
            print(f"Error al obtener preguntas de seguridad por usuario: {e}")
            return None

    @staticmethod
    def insertar_categoria(id_usuario, categoria):
        """Inserta una nueva categoría de contraseñas para un usuario."""
        try:
            conexion = sqlite3.connect("usuarios.db")
            cursor = conexion.cursor()

            # Insertar la categoría en la base de datos
            cursor.execute("""
                INSERT INTO categorias_contraseñas (idUsuario, categoria)
                VALUES (?, ?)
            """, (id_usuario, categoria))

            conexion.commit()
            conexion.close()
            print(f"Categoría '{categoria}' agregada correctamente para el usuario con ID {id_usuario}.")
        except sqlite3.Error as e:
            print(f"Error al insertar categoría: {e}")

    @staticmethod
    def obtener_categorias(id_usuario):
        """Obtiene todas las categorías de contraseñas asociadas a un usuario."""
        try:
            conexion = sqlite3.connect("usuarios.db")
            cursor = conexion.cursor()

            # Obtener las categorías del usuario
            cursor.execute("""
                SELECT categoria FROM categorias_contraseñas WHERE idUsuario = ?
            """, (id_usuario,))
            categorias = cursor.fetchall()

            conexion.close()

            # Retornar las categorías como una lista de strings
            return [categoria[0] for categoria in categorias]
        except sqlite3.Error as e:
            print(f"Error al obtener categorías: {e}")
            return []

    @staticmethod
    def eliminar_categoria(id_usuario, categoria):
        """Elimina una categoría de contraseñas asociada a un usuario."""
        try:
            conexion = sqlite3.connect("usuarios.db")
            cursor = conexion.cursor()

            # Eliminar la categoría de la base de datos
            cursor.execute("""
                DELETE FROM categorias_contraseñas WHERE idUsuario = ? AND categoria = ?
            """, (id_usuario, categoria))

            conexion.commit()
            conexion.close()
            print(f"Categoría '{categoria}' eliminada correctamente para el usuario con ID {id_usuario}.")
        except sqlite3.Error as e:
            print(f"Error al eliminar categoría: {e}")

    @staticmethod
    def insertar_contraseña(id_usuario, categoria, contraseña):
        """Inserta una nueva contraseña asociada a una categoría para un usuario."""
        try:
            conexion = sqlite3.connect("usuarios.db")
            cursor = conexion.cursor()

            # Obtener el id de la categoría para asociar la contraseña
            cursor.execute("""
                SELECT id FROM categorias_contraseñas WHERE idUsuario = ? AND categoria = ?
            """, (id_usuario, categoria))
            categoria_data = cursor.fetchone()

            if categoria_data:
                id_categoria = categoria_data[0]
                # Insertar la contraseña en la base de datos
                cursor.execute("""
                    INSERT INTO contraseñas (idCategoria, contraseña)
                    VALUES (?, ?)
                """, (id_categoria, contraseña))

                conexion.commit()
                conexion.close()
                print(f"Contraseña agregada correctamente en la categoría '{categoria}'.")
            else:
                print(f"No se encontró la categoría '{categoria}' para el usuario con ID {id_usuario}.")
                conexion.close()

        except sqlite3.Error as e:
            print(f"Error al insertar contraseña: {e}")

    @staticmethod
    def obtener_contraseñas(id_usuario, categoria):
        """Obtiene todas las contraseñas asociadas a una categoría de un usuario."""
        try:
            conexion = sqlite3.connect("usuarios.db")
            cursor = conexion.cursor()

            # Obtener el id de la categoría
            cursor.execute("""
                SELECT id FROM categorias_contraseñas WHERE idUsuario = ? AND categoria = ?
            """, (id_usuario, categoria))
            categoria_data = cursor.fetchone()

            if categoria_data:
                id_categoria = categoria_data[0]

                # Obtener las contraseñas asociadas a la categoría
                cursor.execute("""
                    SELECT contraseña FROM contraseñas WHERE idCategoria = ?
                """, (id_categoria,))
                contraseñas = cursor.fetchall()

                conexion.close()

                return [contraseña[0] for contraseña in contraseñas]  # Retornar las contraseñas

            else:
                print(f"No se encontró la categoría '{categoria}' para el usuario con ID {id_usuario}.")
                conexion.close()
                return []

        except sqlite3.Error as e:
            print(f"Error al obtener las contraseñas: {e}")
            return []
