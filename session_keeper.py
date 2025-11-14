#!/usr/bin/env python3
"""
Script para mantener una sesión activa en una página web.
Lee la configuración desde config.json y realiza login automático.
"""

import json
import time
import sys
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('session_keeper.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class SessionKeeper:
    """Clase para mantener una sesión web activa."""
    
    def __init__(self, config_file='config.json'):
        """
        Inicializa el SessionKeeper.
        
        Args:
            config_file (str): Ruta al archivo de configuración JSON.
        """
        self.config = self._load_config(config_file)
        self.driver = None
        self.is_logged_in = False
        
    def _load_config(self, config_file):
        """Carga la configuración desde el archivo JSON."""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            logger.info(f"Configuración cargada desde {config_file}")
            return config
        except FileNotFoundError:
            logger.error(f"Archivo de configuración {config_file} no encontrado")
            sys.exit(1)
        except json.JSONDecodeError as e:
            logger.error(f"Error al parsear JSON: {e}")
            sys.exit(1)
    
    def _setup_driver(self):
        """Configura el driver de Selenium."""
        try:
            # Configuración de opciones para Chrome
            options = webdriver.ChromeOptions()
            
            # Modo headless según configuración
            headless = self.config['session_settings'].get('headless', False)
            if headless:
                options.add_argument('--headless')
                options.add_argument('--disable-gpu')
                logger.info("Modo headless activado (navegador oculto)")
            else:
                logger.info("Modo visible activado (navegador visible)")
            
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--start-maximized')
            
            self.driver = webdriver.Chrome(options=options)
            logger.info("Driver de Selenium configurado correctamente")
        except WebDriverException as e:
            logger.error(f"Error al configurar el driver: {e}")
            logger.info("Asegúrate de tener ChromeDriver instalado")
            sys.exit(1)
    
    def login(self):
        """Realiza el login en la página web."""
        login_url = self.config['login_url']
        credentials = self.config['credentials']
        form_fields = self.config['form_fields']
        timeout = self.config['session_settings']['timeout']
        
        logger.info(f"Intentando hacer login en {login_url}")
        
        try:
            # Navegar a la página de login
            self.driver.get(login_url)
            
            # Esperar a que el formulario esté disponible
            wait = WebDriverWait(self.driver, timeout)
            
            # Localizar y rellenar el campo de usuario
            username_field = wait.until(
                EC.presence_of_element_located((By.NAME, form_fields['username_field']))
            )
            username_field.clear()
            username_field.send_keys(credentials['username'])
            logger.info("Campo de usuario rellenado")
            
            # Localizar y rellenar el campo de contraseña
            password_field = self.driver.find_element(By.NAME, form_fields['password_field'])
            password_field.clear()
            password_field.send_keys(credentials['password'])
            logger.info("Campo de contraseña rellenado")
            
            # Hacer clic en el botón de submit - intentar múltiples métodos
            submit_button = None
            submit_xpath = form_fields.get('submit_button', '')
            
            # Intentar primero con el XPath proporcionado
            try:
                if submit_xpath:
                    submit_button = self.driver.find_element(By.XPATH, submit_xpath)
                    logger.info("Botón encontrado usando XPath proporcionado")
            except Exception:
                logger.warning("No se encontró el botón con el XPath proporcionado, intentando alternativas...")
            
            # Si no funciona, intentar con métodos alternativos
            if not submit_button:
                try:
                    # Intentar por ID común
                    submit_button = self.driver.find_element(By.ID, 'loginbtn')
                    logger.info("Botón encontrado por ID 'loginbtn'")
                except Exception:
                    pass
            
            if not submit_button:
                try:
                    # Intentar por tipo submit
                    submit_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
                    logger.info("Botón encontrado por tipo submit")
                except Exception:
                    pass
            
            if not submit_button:
                try:
                    # Intentar por input submit
                    submit_button = self.driver.find_element(By.XPATH, "//input[@type='submit']")
                    logger.info("Botón encontrado por input submit")
                except Exception:
                    pass
            
            if not submit_button:
                raise Exception("No se pudo localizar el botón de submit con ningún método")
            
            submit_button.click()
            logger.info("Formulario enviado")
            
            # Esperar un momento para que el login se complete
            time.sleep(3)
            
            # Verificar si el login fue exitoso (puedes personalizar esta verificación)
            current_url = self.driver.current_url
            if current_url != login_url:
                self.is_logged_in = True
                logger.info("Login exitoso")
                return True
            else:
                logger.error("Login fallido - seguimos en la página de login")
                return False
                
        except TimeoutException:
            logger.error(f"Timeout al esperar elementos del formulario (timeout: {timeout}s)")
            return False
        except Exception as e:
            logger.error(f"Error durante el login: {e}")
            return False
    
    def navigate_to_session_url(self):
        """Navega a la URL donde se mantendrá la sesión activa."""
        session_url = self.config['session_url']
        try:
            logger.info(f"Navegando a {session_url}")
            self.driver.get(session_url)
            time.sleep(2)
            return True
        except Exception as e:
            logger.error(f"Error al navegar a la URL de sesión: {e}")
            return False
    
    def refresh_page(self):
        """Refresca la página actual."""
        try:
            logger.info("Refrescando página...")
            self.driver.refresh()
            logger.info(f"Página refrescada - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            return True
        except Exception as e:
            logger.error(f"Error al refrescar la página: {e}")
            return False
    
    def keep_session_alive(self):
        """Mantiene la sesión activa refrescando la página periódicamente."""
        refresh_interval = self.config['session_settings']['refresh_interval']
        max_retries = self.config['session_settings']['max_retries']
        
        logger.info(f"Manteniendo sesión activa (intervalo de refresco: {refresh_interval}s)")
        
        retry_count = 0
        
        try:
            while True:
                time.sleep(refresh_interval)
                
                if self.refresh_page():
                    retry_count = 0  # Resetear contador de reintentos
                else:
                    retry_count += 1
                    logger.warning(f"Fallo al refrescar ({retry_count}/{max_retries})")
                    
                    if retry_count >= max_retries:
                        logger.error("Máximo de reintentos alcanzado")
                        return False
                        
        except KeyboardInterrupt:
            logger.info("Sesión interrumpida por el usuario")
            return True
    
    def run(self):
        """Ejecuta el flujo completo: setup, login y mantener sesión."""
        try:
            # Configurar driver
            self._setup_driver()
            
            # Realizar login
            if not self.login():
                logger.error("No se pudo completar el login")
                return False
            
            # Navegar a la URL de sesión
            if not self.navigate_to_session_url():
                logger.error("No se pudo navegar a la URL de sesión")
                return False
            
            # Mantener sesión activa
            self.keep_session_alive()
            
            return True
            
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Limpia recursos y cierra el navegador."""
        if self.driver:
            logger.info("Cerrando navegador...")
            self.driver.quit()
            logger.info("Navegador cerrado")


def main():
    """Función principal."""
    logger.info("=== Session Keeper iniciado ===")
    
    # Crear instancia de SessionKeeper
    keeper = SessionKeeper('config.json')
    
    # Ejecutar
    keeper.run()
    
    logger.info("=== Session Keeper finalizado ===")


if __name__ == "__main__":
    main()
