"""
LoginScreen - Pantalla de login/registro con interfaz gráfica
"""

from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import DirectButton, DirectEntry
from panda3d.core import TextNode, Vec4


class LoginScreen:
    def __init__(self, base, user_manager, on_login_success):
        self.base = base
        self.user_manager = user_manager
        self.on_login_success = on_login_success
        self.mode = "login"  # "login" o "register"
        
        # Fondo
        self.base.setBackgroundColor(Vec4(0.05, 0.05, 0.15, 1))
        
        # Título
        self.title = OnscreenText(
            text="Crystal Breaker - CABJ Edition",
            pos=(0, 0.7), scale=0.12,
            fg=(0.6, 0.9, 1.0, 1),
            shadow=(0, 0, 0, 1),
            align=TextNode.ACenter
        )
        
        # Subtítulo
        self.subtitle = OnscreenText(
            text="INICIAR SESIÓN",
            pos=(0, 0.5), scale=0.08,
            fg=(1, 1, 0.5, 1),
            align=TextNode.ACenter
        )
        
        # Label Usuario
        self.username_label = OnscreenText(
            text="Usuario:",
            pos=(-0.4, 0.25), scale=0.06,
            fg=(1, 1, 1, 1),
            align=TextNode.ALeft
        )
        
        # Campo de texto: Usuario
        self.username_entry = DirectEntry(
            text="",
            scale=0.06,
            pos=(-0.4, 0, 0.15),
            initialText="",
            numLines=1,
            focus=1,
            width=12,
            frameColor=(0.2, 0.2, 0.3, 0.8)
        )
        
        # Label Contraseña
        self.password_label = OnscreenText(
            text="Contraseña:",
            pos=(-0.4, 0.0), scale=0.06,
            fg=(1, 1, 1, 1),
            align=TextNode.ALeft
        )
        
        # Campo de texto: Contraseña
        self.password_entry = DirectEntry(
            text="",
            scale=0.06,
            pos=(-0.4, 0, -0.1),
            initialText="",
            numLines=1,
            width=12,
            obscured=1,  # Ocultar contraseña con asteriscos
            frameColor=(0.2, 0.2, 0.3, 0.8)
        )
        
        # Botón Login
        self.login_button = DirectButton(
            text="INICIAR SESIÓN",
            scale=0.07,
            pos=(0, 0, -0.3),
            command=self.on_login_click,
            frameColor=(0.2, 0.7, 0.2, 0.8),
            text_fg=(1, 1, 1, 1),
            relief=1
        )
        
        # Botón Registrarse
        self.register_button = DirectButton(
            text="REGISTRARSE",
            scale=0.06,
            pos=(0, 0, -0.45),
            command=self.toggle_mode,
            frameColor=(0.3, 0.3, 0.6, 0.8),
            text_fg=(1, 1, 1, 1),
            relief=1
        )
        
        # Mensaje de error/éxito
        self.message_text = OnscreenText(
            text="",
            pos=(0, -0.6), scale=0.05,
            fg=(1, 0.3, 0.3, 1),
            align=TextNode.ACenter
        )
        
        # Instrucciones
        self.instructions = OnscreenText(
            text="Presiona ENTER para continuar",
            pos=(0, -0.8), scale=0.05,
            fg=(0.7, 0.7, 0.7, 1),
            align=TextNode.ACenter
        )
        
        # Controles de teclado
        self.base.accept('enter', self.on_login_click)
        self.base.accept('tab', self.focus_password)
    
    def focus_password(self):
        """Cambia el foco al campo de contraseña"""
        self.password_entry['focus'] = 1
    
    def toggle_mode(self):
        """Alterna entre modo login y registro"""
        if self.mode == "login":
            self.mode = "register"
            self.subtitle.setText("REGISTRARSE")
            self.login_button.setText("CREAR CUENTA")
            self.register_button.setText("Ya tengo cuenta")
            self.message_text.setText("")
        else:
            self.mode = "login"
            self.subtitle.setText("INICIAR SESIÓN")
            self.login_button.setText("INICIAR SESIÓN")
            self.register_button.setText("REGISTRARSE")
            self.message_text.setText("")
    
    def on_login_click(self):
        """Maneja el click en login o registro"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if self.mode == "login":
            # Intentar login
            success, message = self.user_manager.login(username, password)
            
            if success:
                self.message_text.setText(message)
                self.message_text['fg'] = (0.3, 1, 0.3, 1)
                # Pequeño delay antes de continuar
                self.base.taskMgr.doMethodLater(0.5, self.proceed_to_menu, 'proceed')
            else:
                self.message_text.setText(message)
                self.message_text['fg'] = (1, 0.3, 0.3, 1)
        
        else:  # mode == "register"
            # Intentar registro
            success, message = self.user_manager.register_user(username, password)
            
            if success:
                self.message_text.setText(message + "\nAhora puedes iniciar sesión")
                self.message_text['fg'] = (0.3, 1, 0.3, 1)
                # Cambiar automáticamente a modo login
                self.base.taskMgr.doMethodLater(1.5, self.switch_to_login, 'switch')
            else:
                self.message_text.setText(message)
                self.message_text['fg'] = (1, 0.3, 0.3, 1)
    
    def switch_to_login(self, task):
        """Cambia a modo login después de registro exitoso"""
        self.toggle_mode()
        self.password_entry.set("")
        return task.done
    
    def proceed_to_menu(self, task):
        """Procede al menú principal después de login exitoso"""
        self.hide()
        self.on_login_success()
        return task.done
    
    def hide(self):
        """Oculta la pantalla de login"""
        self.title.destroy()
        self.subtitle.destroy()
        self.username_label.destroy()
        self.username_entry.destroy()
        self.password_label.destroy()
        self.password_entry.destroy()
        self.login_button.destroy()
        self.register_button.destroy()
        self.message_text.destroy()
        self.instructions.destroy()
        
        self.base.ignore('enter')
        self.base.ignore('tab')
