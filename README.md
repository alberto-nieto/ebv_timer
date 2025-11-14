# Session Keeper - Mantenedor de Sesión Web

Script en Python que mantiene activa una sesión web mediante login automático y refrescos periódicos de página.

## 📋 Características

- Login automático en páginas web
- Mantiene la sesión activa refrescando la página periódicamente
- Configuración flexible mediante archivo JSON
- Logging detallado de todas las operaciones
- Manejo de errores y reintentos
- Compatible con Chrome/Chromium

## 🔧 Requisitos

- Python 3.7 o superior
- Google Chrome o Chromium
- ChromeDriver (compatible con tu versión de Chrome)

## 📦 Instalación

1. **Instalar dependencias de Python:**

```bash
pip install -r requirements.txt
```

2. **Instalar ChromeDriver:**

   **Opción A - Descarga manual:**
   - Ve a [ChromeDriver Downloads](https://chromedriver.chromium.org/downloads)
   - Descarga la versión compatible con tu Chrome
   - Añade el ejecutable a tu PATH

   **Opción B - Con webdriver-manager (recomendado):**
   ```bash
   pip install webdriver-manager
   ```
   Luego modifica la línea en `session_keeper.py`:
   ```python
   from webdriver_manager.chrome import ChromeDriverManager
   self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
   ```

## ⚙️ Configuración

Edita el archivo `config.json` con tus datos:

```json
{
  "login_url": "https://ejemplo.com/login",
  "session_url": "https://ejemplo.com/dashboard",
  "credentials": {
    "username": "tu_usuario",
    "password": "tu_contraseña"
  },
  "form_fields": {
    "username_field": "username",
    "password_field": "password",
    "submit_button": "//button[@type='submit']"
  },
  "session_settings": {
    "refresh_interval": 300,
    "max_retries": 3,
    "timeout": 10
  }
}
```

### Parámetros de configuración:

- **login_url**: URL de la página de login
- **session_url**: URL donde mantener la sesión activa
- **credentials**: Usuario y contraseña para el login
- **form_fields**: 
  - `username_field`: Atributo `name` del campo de usuario
  - `password_field`: Atributo `name` del campo de contraseña
  - `submit_button`: XPath del botón de envío
- **session_settings**:
  - `refresh_interval`: Intervalo de refresco en segundos (300 = 5 minutos)
  - `max_retries`: Número máximo de reintentos en caso de error
  - `timeout`: Tiempo de espera para elementos web (segundos)

### 🔍 Cómo encontrar los nombres de los campos

Para configurar correctamente los campos del formulario:

1. **Abre la página de login en Chrome**
2. **Clic derecho sobre el campo de usuario → Inspeccionar**
3. Busca el atributo `name` en el HTML:
   ```html
   <input type="text" name="username" ...>
   ```
4. **Repite para el campo de contraseña**
5. **Para el botón de submit**, copia el XPath:
   - Clic derecho en el elemento en DevTools
   - Copy → Copy XPath

## 🚀 Uso

Ejecuta el script:

```bash
python session_keeper.py
```

El script:
1. Abrirá un navegador Chrome
2. Navegará a la página de login
3. Introducirá las credenciales automáticamente
4. Navegará a la URL de sesión
5. Refrescará la página cada X segundos (según configuración)

Para detener el script, presiona `Ctrl+C`.

## 📝 Logs

El script genera logs en:
- **Archivo**: `session_keeper.log` (registro completo)
- **Consola**: Mensajes importantes en tiempo real

## 🎛️ Modo Headless

Para ejecutar el navegador sin interfaz gráfica (en segundo plano), edita `session_keeper.py` y descomenta:

```python
# En la función _setup_driver()
options.add_argument('--headless')
```

## ⚠️ Consideraciones de Seguridad

- **No compartas el archivo `config.json`** con tus credenciales
- Añade `config.json` a `.gitignore` si usas Git:
  ```
  echo config.json >> .gitignore
  ```
- Considera usar variables de entorno para credenciales sensibles

## 🐛 Solución de Problemas

### Error: "ChromeDriver not found"
Instala ChromeDriver o usa webdriver-manager (ver sección Instalación)

### Error: "Element not found"
Los selectores de campos pueden ser incorrectos. Verifica:
- Los atributos `name` de los campos
- El XPath del botón de submit
- Que la página haya cargado completamente

### El login no funciona
- Verifica las credenciales en `config.json`
- Aumenta el `timeout` en la configuración
- Revisa los logs en `session_keeper.log`

### La página tiene CAPTCHA
Este script no maneja CAPTCHAs. Considera:
- Autenticación por API si está disponible
- Soluciones de CAPTCHA automático (de pago)

## 📄 Licencia

Este proyecto es de código libre. Úsalo bajo tu propia responsabilidad.

## 🤝 Contribuciones

Si encuentras bugs o tienes sugerencias, siéntete libre de modificar el código según tus necesidades.
