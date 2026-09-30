#!/usr/bin/env python3
"""
rappi_auto_upload.py — Sube 35 productos a Bodega Ofertix en Rappi Mi Tienda
=============================================================================
Prerrequisitos (instalar UNA vez):
    pip install playwright
    playwright install chromium

Uso:
    python rappi_auto_upload.py

Flujo automatizado por producto:
    1. Ir al catálogo → "Crear productos"
    2. Clic en "Desde cero"
    3. Llenar paneles: nombre, precio, descripción, categorías, imágenes
    4. Guardar

El perfil de Chrome queda guardado en _rappi_profile para no pedir login la próxima vez.
"""

import asyncio, sys, time, re
from pathlib import Path
from playwright.async_api import async_playwright, TimeoutError as PWTimeout

# ── Rutas ──────────────────────────────────────────────────────────────────────
IMAGES_BASE   = Path(r"C:\Users\LenovoV14G4-AMN\Pictures\RAP2909202\RAP29092026\RAP29092026")
PROFILE_DIR   = str(IMAGES_BASE / "_rappi_profile")
RAPPI_CATALOG = "https://mitienda.rappi.com.co/cms/catalog/product-list/1"
LOG_FILE      = IMAGES_BASE / "upload_log.txt"

# ── Cookies ────────────────────────────────────────────────────────────────────
COOKIE_STR = "_fbp=fb.2.1788290578722.232069933682777486; _gcl_au=1.1.1176351484.1789687092; rappi.type=0; rappi_refresh_token=ZnQuZ0FBQUFBQnFySFUwSmpSZnhheENEM1diWmMxV1o0Ul9fc2llMDd5dlI2enFUTXlKYTFpWVk4VTNqaTRaX3p1SjRoQWtJeWQ0eXNkT2VPTnRtd1NwVTVmVjZjNkRJVi1WQllKaWswaHYwLUdGaHdOZ2RtbFV3QjdDQjVQR3FMVEs3ZlBBUF9rTlVfelZiWkRlVFVXVzVZb1ZRZk9Ic2w2aG52bGRGWkZ4b3JPdjBPaGxjNWE3b01zMVc5azBwSlMtd1BPX0xaLWt6NkZPdFJWbElGWFpYRFJOeVNza2hRQWg5b0M1dE5sTVMxV3ZvTW9oaWhoUEhiNlVsN0FRSmM5Rk90QldIMFpXN2lTSE1vTzFTbnZXS29LXzUtYmNqWURyV29ncmRMcFBTaUZjdHRxX1FaejRtWlJNM0NmeWVaNUlDNmQwMGdLMXRwbDg5VEhFaHNnRFNnYVVZQjQtajlXYXNjbzBRS2syOG0xTjNrRGN0RXVLaEZRLTczVHNLQk9STzhudG5TZzRHcWNaanBrMllKUDd4OW9XYW1fVkxGczloQT09; QSI_SI_2uf6OdpSYm3mPeC_intercept=true; _gid=GA1.3.1202787915.1790641820; _tt_enable_cookie=1; _ttp=01M3N93NEPD0QP8WYRG4ZAJQ0W_.tt.2.1790641821142; AMP_MKTG_101be7b7fd=JTdCJTdE; AMP_101be7b7fd=JTdCJTIyZGV2aWNlSWQlMjIlM0ElMjI2NjU5NzUwYS00NzgwLTQwY2YtYjI1NC0yYTllOTgwZmUxMzklMjIlMkMlMjJ1c2VySWQlMjIlM0ElMjIlMjIlMkMlMjJzZXNzaW9uSWQlMjIlM0ExNzkwNjQxODIxMzI3JTJDJTIyb3B0T3V0JTIyJTNBZmFsc2UlMkMlMjJsYXN0RXZlbnRUaW1lJTIyJTNBMTc5MDY0MTgyMTMzMiUyQyUyMmxhc3RFdmVudElkJTIyJTNBOCUyQyUyMnBhZ2VDb3VudGVyJTIyJTNBMCUyQyUyMmNvb2tpZURvbWFpbiUyMiUzQSUyMi5yYXBwaS5jb20uY28lMjIlN0Q=; afUserId=8525c5d1-ac56-4639-bf20-8a304acff8ad-p; AF_SYNC=1790641821605; rappi.id=eyJhY2Nlc3NfdG9rZW4iOiJmdC5nQUFBQUFCcXV3YWRULW1UQnVHTlAwWThCa3Fhazlib0ZUVE5jMUdGQVNmWkkyMUo4YWp4Q21YTEp0dHMycDdJV1RWemlmdTlCVzdUQzBPMFpDVzRXUWdzN0NkejNZSUxDT183eTRWVDhNNEVLMkZkaEY1Z0tEclBjS1g5dTJSMW03N3dXRU40U21NZERiRnpkUDFZeHY0ajc3Z0pYNnAtTVpaR0piYmdzMXVOTktuUUZxTFMyR0ZDUUhXeTVwLUdmZHRDc3Uwa1A2SDN1VExUS2pSOE5IaGdPUjJDcDIyNEpqME1hRWlhaWJJUHNoRWd6UGtaN19WWXQ2Z0doem5UbEplM3g0UGgzWVZlZGhMekd0SkFyNUIycGhZNzcwampQS3FDdnB2eWNETWRYc0FidEc3UFk5cm9XOUx6UlB2RDVMb0xndDI1NUZZRVE0THhtNUtFVF9hbmJLejNkZ0xKUF9VaGlDcTlNQ2VmREZ2UklPM0ZxbmhQT1FPWGVsWTZQSkRoTElvV0NvampUdEthMmdRTERULUluWDlPVDlEdWVRPT0iLCJ0b2tlbl90eXBlIjoiQmVhcmVyIn0=; _ga=GA1.1.1696904181.1788290578; _uetsid=f4430c70bb9c11f1b7d41b75e2c08681; _uetvid=0d9721d0b2ee11f1b6148f3ba51675b4; country=CO; name=OFERTIX; mail=nunez0690@gmail.com; csatAck=true; isOnboardingFinished=true; phone_number=+57 3133236471; origin=Mi Tienda; brandId=288661; brandGroupName=null; brandName=OFERTIX; role=Propietario; retailId=14358; partnerId=46194; userId=50658; storeId=900374741; vertical=ecommerce - Hogar"

# ── Catálogo de productos ──────────────────────────────────────────────────────
PRODUCTOS = [
  {"sku":"BS11E","nombre":"LUCES NAVIDAD ESFERA LED 3X0.7M BLANCO CÁLIDO PVC CORTINA DECORATIVA FÁCIL INSTALACIÓN BS11E","precio":60000,"desc":"- Fácil de instalar y conector: cuelga cortinas de luz rápidamente sin herramientas.\n- Material de PVC duradero, bajo voltaje, uso continuo más de 48 horas.\n- LED de color blanco cálido, largo 3m x 0.7m.\n- Materiales: plásticos y componentes electrónicos.\n- Precio especial: $60,000","cat":["Decoración y hogar","Decoración del hogar","Lámparas"]},
  {"sku":"K1430AA","nombre":"TERMO VASO TÉRMICO 700ML ACERO INOXIDABLE DOBLE PARED TAPA ANTIDERRAMES PAJILLA REUTILIZABLE FRÍO CALIENTE AMARILLO CON AZUL K1430AA","precio":65000,"desc":"- Acero inoxidable apto para uso alimentario, excelente durabilidad.\n- Doble pared: mantiene bebidas calientes 6 h y frías 12 h.\n- Tapa resistente a derrames y pajita reutilizable.\n- Capacidad 700 ml, ideal para café, té y batidos.\n- Precio especial: $65,000","cat":["Decoración y hogar","Cocina","Termos y Tomatodos"]},
  {"sku":"VTJ01N","nombre":"RELOJ INTELIGENTE SMARTWATCH PULSERA DIGITAL TÁCTIL COMPACTA VTJ MINI NARANJA VTJ01N","precio":50000,"desc":"- Diseño compacto y elegante, caja rectangular de formato reducido.\n- Pantalla táctil a color de gran definición.\n- Correa de silicona deportiva de alta durabilidad.\n- Compatible con notificaciones y seguimiento de actividad.\n- Precio especial: $50,000","cat":["Tecnología","Celulares y Telefonía","Smartwatch y Smartband"]},
  {"sku":"BS11A","nombre":"LUCES NAVIDAD ÁRBOL ARO LED 3X0.7M BLANCO CÁLIDO PVC CORTINA DECORATIVA FÁCIL INSTALACIÓN BS11A","precio":60000,"desc":"- Fácil de instalar y conector: cuelga cortinas de luz rápidamente sin herramientas.\n- Material de PVC duradero, bajo voltaje, uso continuo más de 48 horas.\n- LED de color blanco cálido, largo 3m x 0.7m.\n- Diseño con motivo árbol de navidad.\n- Precio especial: $60,000","cat":["Decoración y hogar","Decoración del hogar","Lámparas"]},
  {"sku":"TA2020","nombre":"PINZA RIZADORA CABELLO 3 TUBOS BARRILES CERÁMICA 410F IONES ANTI FRIZZ ONDAS PLAYA MARRON TA2020","precio":45000,"desc":"- 3 barriles cerámicos, calentamiento rápido hasta 410°F en 30 segundos.\n- Calentamiento uniforme para rizos hermosos y duraderos de ondas de playa.\n- Temperatura variable con 2 niveles para todo tipo de cabello.\n- Punta fresca para mayor seguridad y comodidad.\n- Precio especial: $45,000","cat":["Cuidado personal","Electro belleza","Otros electro belleza"]},
  {"sku":"TA2020R","nombre":"PINZA RIZADORA CABELLO 3 TUBOS BARRILES CERÁMICA 410F IONES ANTI FRIZZ ONDAS PLAYA ROSADO TA2020R","precio":45000,"desc":"- 3 barriles cerámicos, calentamiento rápido hasta 410°F en 30 segundos.\n- Calentamiento uniforme para rizos hermosos y duraderos de ondas de playa.\n- Temperatura variable con 2 niveles para todo tipo de cabello.\n- Punta fresca para mayor seguridad y comodidad.\n- Precio especial: $45,000","cat":["Cuidado personal","Electro belleza","Otros electro belleza"]},
  {"sku":"F1018","nombre":"ESTANTE ORGANIZADOR DE OLLAS Y SARTENES 8 ESPACIOS F1018","precio":50000,"desc":"- Alambre grueso y marco de alta durabilidad, sin herramientas ni tornillos.\n- 8 separadores ajustables para ollas y sartenes de distintos tamaños.\n- Diseño modular que se adapta a tu cocina fácilmente.\n- Fácil de limpiar y mantener organizado.\n- Precio especial: $50,000","cat":["Decoración y hogar","Organizadores","Organizadores para cocina"]},
  {"sku":"KF047","nombre":"CAFETERA ITALIANA MOKA 9 TAZAS ALUMINIO FUNDIDO ESPRESSO PORTÁTIL VÁLVULA PRESIÓN CAMPING HOGAR KF047","precio":56000,"desc":"- Aluminio fundido de alta calidad con válvula de presión para extracción eficiente.\n- Diseño clásico, café con sabor intenso y aroma tradicional.\n- Compacta: 15 cm x 8 cm, ideal para camping y hogar.\n- Capacidad para 9 tazas de espresso tradicional.\n- Precio especial: $56,000","cat":["Decoración y hogar","Cocina","Utensilios de Cocina"]},
  {"sku":"R008301A","nombre":"COCINA MALETA JUGUETE SET DE CHEF EN MALETA PARA NIÑOS PLEGABLE 008 ROSADO R008301A","precio":60000,"desc":"- Set de rol 3 en 1: valija portátil + cocina armable con estante y mesada.\n- Medidas: 47 cm x 29.5 cm x 18 cm, peso 690 g.\n- Edad recomendada: 3 años en adelante.\n- Estimula el juego de roles y la creatividad infantil.\n- Precio especial: $60,000","cat":["Juguetería","Juegos Musicales y de rol","Roles y Profesiones"]},
  {"sku":"R008305C","nombre":"JUGUETE SET DE DOCTOR EN MALETA DESPLEGABLE PARA NIÑOS CON ACCESORIOS ROSADO R008305C","precio":60000,"desc":"- Maleta médica 3 en 1, se despliega en miniestación médica completa.\n- Montaje sin herramientas, plástico suave y seguro.\n- Accesorios médicos simulados para juego de roles creativo.\n- Para niñas de 3 años o más.\n- Precio especial: $60,000","cat":["Juguetería","Juegos Musicales y de rol","Roles y Profesiones"]},
  {"sku":"MA889","nombre":"COCHE PARA MUÑECAS METÁLICO PLEGABLE ROSA JUGUETE INFANTIL CARRITO MUÑECA RESISTENTE COMPACTO MA889","precio":65000,"desc":"- Estructura robusta en metal de alta calidad, ligero y seguro.\n- Diseño encantador en tonos fucsia y rosa con tela estampada.\n- Plegable y compacto para almacenamiento y transporte fácil.\n- Tamaño: 44 x 32 cm.\n- Precio especial: $65,000","cat":["Juguetería","Muñecas, Muñecos y Peluches","Muñecas y Bebés"]},
  {"sku":"T9855","nombre":"PANEL DE LUZ LED CON CLIP AJUSTABLE VL-60BI T9855","precio":57000,"desc":"- 60 LEDs blancos fríos y cálidos, temperatura de color 2500K-9000K.\n- Iluminación profesional para fotografía y video.\n- Clip ajustable para montaje versátil.\n- Ideal para streaming, reuniones virtuales y contenido digital.\n- Precio especial: $57,000","cat":["Tecnología","Soportes y Tripodes","Aro de luz"]},
  {"sku":"LYS020","nombre":"COLGADOR TENDEDERO RETRÁCTIL ROPA ACERO INOXIDABLE 304 AJUSTABLE 4.2M IMPERMEABLE INTERIOR EXTERIOR LYS020","precio":55000,"desc":"- Cuerda de acero inoxidable 304, carcasa ABS resistente.\n- Se extiende hasta 4.2 m, soporta hasta 20 kg.\n- Retráctil y de fácil instalación para balcón, baño o lavandería.\n- Compatible con decoraciones de interior y exterior.\n- Precio especial: $55,000","cat":["Decoración y hogar","Organizadores","Organizadores de ropa"]},
  {"sku":"XYA13051","nombre":"ESCURRIDOR DE PLATOS DKASA PEQUEÑO 3 PIEZAS HIERRO BANDEJA PLÁSTICA PORTA CUBIERTOS NEGRO XYA13051","precio":60000,"desc":"- Rejilla de hierro con pintura electrostática resistente a la corrosión.\n- Incluye bandeja recolectora de agua y porta cubiertos.\n- Ideal para espacios pequeños en la cocina.\n- 3 piezas en un solo set práctico y funcional.\n- Precio especial: $60,000","cat":["Decoración y hogar","Organizadores","Organizadores para cocina"]},
  {"sku":"SD20AM","nombre":"SET PERCUSION BEBE 5 PIEZAS TAMBOR MARACAS SONAJERO BAQUETAS INSTRUMENTOS MUSICALES INFANTILES AMARILLO SD20AM","precio":45000,"desc":"- Incluye tambor, maracas, sonajero y baquetas para estimulación sensorial.\n- Medidas: 52 cm x 38 cm x 7 cm con bolsa de almacenamiento.\n- Colores llamativos que favorecen la estimulación visual y táctil.\n- Desarrolla coordinación motriz y habilidades musicales.\n- Precio especial: $45,000","cat":["Juguetería","Juegos Musicales y de rol","Juegos musicales"]},
  {"sku":"SMP301","nombre":"SILLA MULTIFUNCIONAL PLEGABLE TABURETE PORTÁTIL PP 200KG CAMPING PESCA PLAYA AZUL OSCURO SMP301","precio":45000,"desc":"- PP de alta calidad, estable, duradero y liviano con asa para transporte.\n- Diseño plegable compacto, fácil de abrir en segundos sin herramientas.\n- Soporta hasta 200 kg / 441 lb, firme y estable.\n- Ideal para camping, pesca, playa y uso interior.\n- Precio especial: $45,000","cat":["Ferretería y jardín","Aire Libre","Muebles de exterior"]},
  {"sku":"SMP301M","nombre":"SILLA MULTIFUNCIONAL PLEGABLE TABURETE PORTÁTIL PP 200KG CAMPING PESCA PLAYA MARRON SMP301M","precio":45000,"desc":"- PP de alta calidad, estable, duradero y liviano con asa para transporte.\n- Diseño plegable compacto, fácil de abrir en segundos sin herramientas.\n- Soporta hasta 200 kg / 441 lb, firme y estable.\n- Ideal para camping, pesca, playa y uso interior.\n- Precio especial: $45,000","cat":["Ferretería y jardín","Aire Libre","Muebles de exterior"]},
  {"sku":"LS206","nombre":"CALENTADOR DE BIBERONES RECARGABLE PORTATIL PARA LECHE CALIENTA BIBERON RAPIDO CONSERVA TEMPERATURA USO NOCTURNO LS206","precio":45000,"desc":"- Calienta biberones en aproximadamente 5 minutos, inalámbrico y recargable.\n- 6 niveles de temperatura entre 38°C y 50°C.\n- Sensores múltiples para control preciso de temperatura.\n- Fabricado en ABS resistente al calor, práctico y duradero.\n- Precio especial: $45,000","cat":["Decoración y hogar","Electromenor","Otros Electromenor"]},
  {"sku":"LP0006","nombre":"LÁMPARA LED MAGNÉTICA 4 EN 1 RECARGABLE USB PARA ESCRITORIO PARED Y CLIP LP0006","precio":48000,"desc":"- Diseño elegante 4 en 1: escritorio, pared, clip y portátil.\n- Tamaño compacto 13.69 cm x 36 cm, ideal para mesitas y escritorios.\n- Recargable por USB, tecnología LED de luz cálida y agradable.\n- Montaje magnético versátil para múltiples superficies.\n- Precio especial: $48,000","cat":["Decoración y hogar","Decoración del hogar","Lámparas"]},
  {"sku":"SM8081","nombre":"PLASTILINA SET MASAS MOLDEABLES INFANTIL ACCESORIOS JUEGO DE ROLES CREATIVO JIRAFA SM8081","precio":60000,"desc":"- Set de masa plástica y moldes con temática de jirafa para creatividad infantil.\n- Máquina de jirafa que funciona como extrusora o prensa para moldear.\n- Plastilina no tóxica en llamativos colores, para niños desde 3 años.\n- Inserta el molde, pon la plastilina y presiona ¡y listo!\n- Precio especial: $60,000","cat":["Arte y Manualidades","Pintura","Otros Pintura"]},
  {"sku":"SM8079","nombre":"PLASTILINA SET MASAS MOLDEABLES INFANTIL ACCESORIOS JUEGO DE ROLES CREATIVO PERRO VETERINARIO SM8079","precio":60000,"desc":"- Experiencia creativa de veterinario para niños desde 3 años.\n- Accesorios de veterinario incluidos para explorar la creatividad.\n- Fomenta la imaginación y el juego de roles.\n- Paquete: 33 cm x 14 cm x 23 cm, fácil de almacenar.\n- Precio especial: $60,000","cat":["Arte y Manualidades","Pintura","Otros Pintura"]},
  {"sku":"SM8115","nombre":"PLASTILINA SET MASAS MOLDEABLES INFANTIL ACCESORIOS JUEGO DE ROLES CREATIVO UNICORNIO SM8115","precio":60000,"desc":"- Kit plastilina unicornio moldeable para estimular la creatividad.\n- Plastilina no tóxica en llamativos colores, segura para niños.\n- Moldes divertidos y accesorios para dejar volar la imaginación.\n- Desarrolla habilidades motoras finas de forma entretenida.\n- Precio especial: $60,000","cat":["Arte y Manualidades","Pintura","Otros Pintura"]},
  {"sku":"PTF1268A","nombre":"TERMO BOTELLA TÉRMICA 1000ML ACERO INOXIDABLE BOCA ANCHA ANTIDERRAME CON AGARRE AZUL PTF1268A","precio":65000,"desc":"- Acero inoxidable, acabado texturizado azul pastel con asa lateral.\n- Tapa hermética con boquilla abatible y tapón de silicona.\n- Boca ancha para fácil llenado y limpieza.\n- Capacidad 1000 ml, ideal para trabajo, viajes y actividades diarias.\n- Precio especial: $65,000","cat":["Decoración y hogar","Cocina","Termos y Tomatodos"]},
  {"sku":"SM8077","nombre":"PLASTILINA SET MASAS MOLDEABLES INFANTIL ACCESORIOS JUEGO DE ROLES CREATIVO OSO SM8077","precio":60000,"desc":"- Kit plastilina oso moldeable para estimular la creatividad infantil.\n- Plastilina no tóxica en llamativos colores, para niños desde 3 años.\n- Moldes divertidos y accesorios para dejar volar la imaginación.\n- Desarrolla habilidades motoras finas de forma entretenida.\n- Precio especial: $60,000","cat":["Arte y Manualidades","Pintura","Otros Pintura"]},
  {"sku":"SM8068","nombre":"PLASTILINA SET MASAS MOLDEABLES INFANTIL ACCESORIOS JUEGO DE ROLES CREATIVO DINOSAURIO SM8068","precio":60000,"desc":"- Set con 6 tarritos de plastilina y 9 moldes de dinosaurios.\n- Completamente lavable, para niños desde 3 años.\n- Plastilina suave que desarrolla habilidades motoras finas.\n- Aventura prehistórica llena de color y diversión.\n- Precio especial: $60,000","cat":["Arte y Manualidades","Pintura","Otros Pintura"]},
  {"sku":"LD3628R","nombre":"MUÑECA DE JUGUETE RUMI CON MICRÓFONO LUCES Y MÚSICA INTERACTIVA LD3628R","precio":65000,"desc":"- Micrófono interactivo con luces de colores y canciones.\n- Muñeca articulada con estilo urbano y moderno.\n- Sistema Try Me desde el empaque para activar efectos.\n- Plástico de alta resistencia, apta para niños desde 3 años.\n- Precio especial: $65,000","cat":["Juguetería","Muñecas, Muñecos y Peluches","Muñecas y Bebés"]},
  {"sku":"C9802S10A","nombre":"CARRO LOCO CON HUMO STUNT CAR RC 360° ACROBÁTICO DOBLE CARA LUCES LED LLANTAS TODOTERRENO AMARILLO C9802S10A","precio":60000,"desc":"- Giros 360°, volteretas y acrobacias extremas con control remoto.\n- Diseño doble cara: si se voltea sigue rodando sin detenerse.\n- Luces LED y llantas todoterreno para cualquier superficie.\n- Batería recargable para más horas de juego.\n- Precio especial: $60,000","cat":["Juguetería","Vehículos","Carros y Motos"]},
  {"sku":"PTF1268","nombre":"TERMO BOTELLA TÉRMICA 1000ML ACERO INOXIDABLE BOCA ANCHA ANTIDERRAME CON AGARRE NEGRO PTF1268","precio":65000,"desc":"- Diseño estable que no se vuelca incluso vacío.\n- Conserva bebidas frías y calientes sin retener olores.\n- Boca ancha de gran diámetro para fácil limpieza a mano.\n- Capacidad 1000 ml, para estudiantes y uso diario.\n- Precio especial: $65,000","cat":["Decoración y hogar","Cocina","Termos y Tomatodos"]},
  {"sku":"HYG01G","nombre":"MANTA COBIJA SABANA LUMINOSA PARA NIÑOS BRILLA OSCURIDAD GRIS HYG01G","precio":50000,"desc":"- Expone 10-15 min a la luz y brillará en la oscuridad.\n- Medidas: 1m x 1.70m, fibra de poliéster de alta calidad.\n- Suave al tacto, buena retención del calor.\n- Perfecta para hacer la hora de dormir más divertida.\n- Precio especial: $50,000","cat":["Decoración y hogar","Textiles de hogar y cortinas","Otros Textiles de hogar y cortinas"]},
  {"sku":"N014MK1","nombre":"CONTROL GAMEPAD X3 PARA CELULAR ANDROID Y TABLETS NEGRO TPL N014MK1","precio":50000,"desc":"- Bluetooth 3.0, ligero y totalmente portátil.\n- Soporte ajustable compatible con la mayoría de smartphones Android.\n- Diseñado para una experiencia de juego cómoda y ergonómica.\n- Compatible con tablets y teléfonos Android.\n- Precio especial: $50,000","cat":["Tecnología","Gaming","Mandos y Volantes Gaming"]},
  {"sku":"LD3628","nombre":"MUÑECA DE JUGUETE ZOEY CON MICRÓFONO LUCES Y MÚSICA INTERACTIVA LD3628","precio":65000,"desc":"- Micrófono de juguete con luces multicolores y canciones.\n- Cuerpo articulado para recrear presentaciones de canto y baile.\n- Función Try Me desde la caja para experiencia interactiva.\n- Materiales duraderos, bordes suaves, apta desde 3 años.\n- Precio especial: $65,000","cat":["Juguetería","Muñecas, Muñecos y Peluches","Muñecas y Bebés"]},
  {"sku":"TA2041","nombre":"VENTILADOR ABANICO PARA CARRO TRIPLE 360° RECARGABLE SILENCIOSO AJUSTABLE TA2041","precio":56000,"desc":"- Tres cabezas giratorias que maximizan el flujo de aire en el vehículo.\n- Conexión al encendedor de cigarrillos de 12V, fácil instalación.\n- Velocidad ajustable y giro 360° en cada cabezal.\n- Operación silenciosa para un ambiente fresco y cómodo.\n- Precio especial: $56,000","cat":["Decoración y hogar","Electromenor","Otros Electromenor"]},
  {"sku":"NB3036","nombre":"ORGANIZADOR COSMETICOS MAQUILLAJE SKINCARE TOCADOR BAÑO ESTANTE CAJONERA MULTINIVEL NB3036","precio":58000,"desc":"- 2 cajones, 1 capa media y 1 espacio superior para gran capacidad.\n- Plástico PET duradero y acero aleado, resistente y estable.\n- Versátil para tocadores, baños, oficinas y múltiples entornos.\n- Diseño moderno que complementa cualquier decoración.\n- Precio especial: $58,000","cat":["Decoración y hogar","Organizadores","Otros Organizadores"]},
  {"sku":"JS7021L","nombre":"RECIPIENTE OLLA CALENTADORA DE CERA PARA DEPILACION LILA PRO WAX 100 JS7021L","precio":38000,"desc":"- Voltaje: 110V, capacidad máxima 400g de cera.\n- Fundidor y pote de metal de alta calidad, filtro de plástico.\n- Compacto y fácil de usar para depilación en el hogar.\n- NO INCLUYE LA CERA.\n- Precio especial: $38,000","cat":["Cuidado personal","Electro belleza","Otros electro belleza"]},
  {"sku":"H2516","nombre":"ORGANIZADOR DE OLLAS Y TAPAS EXPANDIBLE ACERO INOXIDABLE 304 AJUSTABLE 30 A 60CM PARA COCINA H2516","precio":50000,"desc":"- Ajustable de 30 a 60 cm de longitud, 7 marcos de soporte.\n- Acero inoxidable 304, resistente a la corrosión y al óxido.\n- Fácil instalación sin herramientas adicionales.\n- Diseño de ranura para sujeción segura de ollas y tapas.\n- Precio especial: $50,000","cat":["Decoración y hogar","Organizadores","Organizadores para cocina"]},
]

# ── Helpers ────────────────────────────────────────────────────────────────────
def parse_cookies(s):
    cookies = []
    for part in s.split("; "):
        if "=" not in part:
            continue
        name, _, value = part.partition("=")
        name = name.strip()
        domain = ".rappi.com.co" if any(name.startswith(p) for p in
            ["rappi","_ga","_gcl","_fbp","_tt","amplitude","AF_","afUser","AMP"]) \
            else "mitienda.rappi.com.co"
        cookies.append({"name":name,"value":value.strip(),"domain":domain,
                        "path":"/","secure":True,"httpOnly":False,"sameSite":"None"})
    return cookies

def log(msg):
    ts = time.strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except:
        pass

async def click_visible(page, selectors, timeout=4000):
    for sel in selectors:
        try:
            el = page.locator(sel).first
            if await el.is_visible(timeout=timeout):
                await el.click()
                return True
        except:
            pass
    return False

async def react_set(page, selector, value):
    """Establece el valor en un input React disparando los eventos correctos."""
    await page.evaluate("""([sel, val]) => {
        const el = document.querySelector(sel);
        if (!el) return;
        const proto = el.tagName === 'TEXTAREA'
            ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
        const setter = Object.getOwnPropertyDescriptor(proto, 'value');
        if (setter && setter.set) setter.set.call(el, val);
        else el.value = val;
        el.dispatchEvent(new Event('input',  {bubbles: true}));
        el.dispatchEvent(new Event('change', {bubbles: true}));
        el.dispatchEvent(new KeyboardEvent('keyup', {bubbles: true}));
    }""", [selector, value])

async def fill_field(page, selectors, value, label="campo"):
    """Intenta llenar un campo con varios selectores; usa react_set como fallback."""
    for sel in selectors:
        try:
            el = page.locator(sel).first
            if await el.is_visible(timeout=2000):
                await el.triple_click()
                await el.fill(value)
                await page.keyboard.press("Tab")
                return True
        except:
            pass
    # Fallback con react_set en el primer selector que exista en el DOM
    for sel in selectors:
        try:
            cnt = await page.locator(sel).count()
            if cnt > 0:
                await react_set(page, sel, value)
                return True
        except:
            pass
    log(f"  ⚠ No encontré {label}")
    return False

# ── Crear un producto ──────────────────────────────────────────────────────────
RAPPI_STEPS = "https://mitienda.rappi.com.co/cms/catalog/steps"

async def click_chip(page, text, timeout=5000):
    """Clic en un chip/botón de categoría por su texto exacto."""
    for sel in [
        f'button:has-text("{text}")',
        f'span:has-text("{text}")',
        f'div[role="button"]:has-text("{text}")',
        f':text-is("{text}")',
    ]:
        try:
            el = page.locator(sel).first
            if await el.is_visible(timeout=timeout):
                await el.click()
                return True
        except:
            pass
    return False

async def next_step(page):
    """Clic en el botón de avanzar al siguiente paso del wizard."""
    for sel in [
        'button:has-text("Siguiente")',
        'button:has-text("Continuar")',
        'button:has-text("Next")',
        'button[type="submit"]',
    ]:
        try:
            el = page.locator(sel).first
            if await el.is_visible(timeout=3000):
                await el.click()
                await page.wait_for_timeout(1500)
                return True
        except:
            pass
    return False

async def select_dropdown(page, trigger_texts, option_text, label="dropdown"):
    """
    Abre un dropdown (React custom) buscando su trigger por texto visible,
    luego selecciona la opción por texto exacto.
    trigger_texts: lista de textos que puede mostrar el trigger (placeholder o valor actual)
    option_text: texto exacto de la opción a seleccionar
    """
    # Encontrar el elemento trigger usando JS por texto interno
    trigger_found = await page.evaluate("""([triggers]) => {
        const candidates = [...document.querySelectorAll(
            '[class*="select"] [class*="control"], [class*="Select"] [class*="control"], ' +
            '[role="combobox"], [class*="dropdown"] [class*="trigger"], ' +
            '[class*="Select__control"], [class*="select__control"]'
        )];
        for (const t of triggers) {
            const el = candidates.find(c => c.textContent.trim().includes(t));
            if (el) { el.click(); return true; }
        }
        // Fallback: buscar cualquier elemento con el texto
        for (const t of triggers) {
            const el = [...document.querySelectorAll('*')]
                .find(e => e.children.length <= 2 && e.textContent.trim() === t
                      && e.offsetParent !== null);
            if (el) { el.click(); return true; }
        }
        return false;
    }""", trigger_texts)

    if not trigger_found:
        log(f"  ⚠ {label}: no encontré el trigger")
        return False

    await page.wait_for_timeout(700)

    # Seleccionar la opción
    for opt_sel in [
        f':text-is("{option_text}")',
        f'[role="option"]:has-text("{option_text}")',
        f'li:has-text("{option_text}")',
        f'div[class*="option"]:has-text("{option_text}")',
        f'[class*="Option"]:has-text("{option_text}")',
        f'[class*="menu-list"] *:has-text("{option_text}")',
    ]:
        try:
            opt = page.locator(opt_sel).first
            if await opt.is_visible(timeout=1500):
                await opt.click()
                log(f"  ✅ {label}: '{option_text}' seleccionado")
                return True
        except:
            pass

    log(f"  ⚠ {label}: menú abierto pero no encontré '{option_text}'")
    await page.keyboard.press("Escape")
    return False


async def crear_producto(page, prod, idx, total):
    sku    = prod["sku"]
    nombre = prod["nombre"]
    precio = str(prod["precio"])
    desc   = prod["desc"]
    cat    = prod["cat"]   # [L1, L2, L3]

    # Imágenes del producto (carpeta IMAGES_BASE/sku/)
    carpeta = IMAGES_BASE / sku
    imgs = []
    if carpeta.exists():
        wb   = sorted(carpeta.glob(f"{sku}*_wb.jpg"))
        rest = [p for p in sorted(carpeta.glob(f"{sku}*.jpg")) if "_wb" not in p.name]
        rest += sorted(carpeta.glob(f"{sku}*.png"))
        imgs = (wb + rest)[:4]

    log(f"\n[{idx}/{total}] ▶ {sku}  precio=${precio}  imgs={len(imgs)}")

    # ══ PASO 1: Página de categorías ═══════════════════════════════════════
    await page.goto(RAPPI_STEPS, wait_until="networkidle", timeout=30000)
    await page.wait_for_timeout(2000)

    # Verificar que llegamos a la página correcta
    if "login" in page.url or "auth" in page.url:
        log("  ⚠ Sesión expirada — esperando login manual (60s)...")
        try:
            await page.wait_for_url("**/cms/**", timeout=60000)
            await page.goto(RAPPI_STEPS, wait_until="networkidle", timeout=30000)
            await page.wait_for_timeout(2000)
        except:
            log("  ✗ No se pudo restablecer sesión")
            return False

    # L1 — categoría principal
    if not await click_chip(page, cat[0]):
        log(f"  ⚠ No encontré categoría L1: {cat[0]}")
    await page.wait_for_timeout(1200)

    # L2 — subcategoría 1
    if len(cat) > 1:
        if not await click_chip(page, cat[1]):
            log(f"  ⚠ No encontré subcategoría L2: {cat[1]}")
        await page.wait_for_timeout(1200)

    # L3 — subcategoría 2
    if len(cat) > 2:
        if not await click_chip(page, cat[2]):
            log(f"  ⚠ No encontré subcategoría L3: {cat[2]}")
        await page.wait_for_timeout(800)

    # Continuar → Info básica
    await next_step(page)
    await page.wait_for_timeout(2500)

    # ══ PASO 2a: Completa la información del producto ══════════════════════
    # Esperar a que el formulario esté listo
    try:
        await page.wait_for_selector(
            'input, textarea', state="visible", timeout=8000
        )
    except:
        pass
    await page.wait_for_timeout(800)

    # Función JS que llena el N-ésimo input/textarea visible con React events
    async def js_fill_nth(tag, idx, value, label_text):
        ok = await page.evaluate("""([tag, idx, val]) => {
            const all = [...document.querySelectorAll(tag)].filter(el => {
                if (el.type === 'hidden' || el.type === 'file'
                    || el.type === 'checkbox' || el.type === 'radio') return false;
                const r = el.getBoundingClientRect();
                return r.width > 0 && r.height > 0;
            });
            const el = all[idx];
            if (!el) return false;
            el.focus();
            const proto = el.tagName === 'TEXTAREA'
                ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
            const setter = Object.getOwnPropertyDescriptor(proto, 'value');
            if (setter && setter.set) setter.set.call(el, val);
            else el.value = val;
            ['input','change','keyup','blur'].forEach(ev => {
                el.dispatchEvent(new Event(ev, {bubbles: true}));
            });
            return true;
        }""", [tag, idx, value])
        if ok:
            log(f"  ✅ {label_text}: via JS[{tag}][{idx}]")
        else:
            log(f"  ⚠ No encontré campo: {label_text}")
        return ok

    # NOMBRE DEL PRODUCTO — primer input visible (index 0)
    await js_fill_nth("input", 0, nombre, "Nombre del producto")
    await page.wait_for_timeout(400)

    # EAN → dejar vacío (opcional)
    # SKU — segundo input visible (index 1)
    await js_fill_nth("input", 1, sku, "SKU")
    await page.wait_for_timeout(400)

    # Marca del producto → dejar vacío (opcional)

    # DESCRIPCIÓN DEL PRODUCTO — primera textarea visible (index 0)
    await js_fill_nth("textarea", 0, desc, "Descripción del producto")
    await page.wait_for_timeout(400)

    # Continuar → Ficha técnica
    await next_step(page)
    await page.wait_for_timeout(2500)

    # ══ PASO 2b: Ficha técnica ═════════════════════════════════════════════
    # Tres campos OBLIGATORIOS:
    #   1. "Formato de venta" dropdown → "Unidad"
    #   2. "CANTIDAD" input            → "1"
    #   3. "UNIDAD DE VENTA" dropdown  → "Und"

    # 1. Formato de venta → Unidad
    await select_dropdown(page,
        ["Formato de venta", "Seleccionar"],
        "Unidad",
        "Formato de venta"
    )
    await page.wait_for_timeout(600)

    # 2. Cantidad → 1
    await fill_field(page, [
        'input[placeholder="Cantidad"]',
        'input[placeholder*="antidad"]',
        'input[aria-label*="antidad"]',
        'input[name*="antidad"]',
        'input[name*="quantity"]',
    ], "1", "Cantidad")
    await page.wait_for_timeout(400)

    # 3. Unidad de venta → Und
    await select_dropdown(page,
        ["UNIDAD DE VENTA", "Seleccionar", "Unidad de venta"],
        "Und",
        "Unidad de venta"
    )
    await page.wait_for_timeout(600)

    # Continuar → Imágenes
    await next_step(page)
    await page.wait_for_timeout(2500)

    # ══ PASO 2c: Imágenes del producto ════════════════════════════════════
    # UI: 1 slot principal + 3 slots "Imagen adicional (opcional)" con botón "+"
    # Subimos hasta 4 imágenes; los slots adicionales requieren clic en "+"

    if imgs:
        for i, img_path in enumerate(imgs):
            try:
                # Contar inputs de archivo disponibles AHORA
                file_inputs = page.locator('input[type="file"]')
                fi_cnt = await file_inputs.count()

                if i < fi_cnt:
                    # Input ya visible (slot 0 o slots previamente abiertos)
                    await file_inputs.nth(i).set_input_files(str(img_path))
                    await page.wait_for_timeout(3000)
                    log(f"  📷 [{i+1}/{len(imgs)}] {img_path.name}")
                else:
                    # Necesitamos abrir un nuevo slot haciendo clic en "+"
                    # Los "+" son botones dentro de los slots "adicional"
                    plus_btns = page.locator(
                        'button:has-text("+"), [aria-label*="gregar"], [class*="add-image"], [class*="addImage"]'
                    )
                    pb_cnt = await plus_btns.count()
                    if pb_cnt > 0:
                        await plus_btns.first.click()
                        await page.wait_for_timeout(800)
                        # Ahora debe haber un nuevo input de archivo
                        fi_cnt2 = await file_inputs.count()
                        if fi_cnt2 > i:
                            await file_inputs.nth(i).set_input_files(str(img_path))
                            await page.wait_for_timeout(3000)
                            log(f"  📷 [{i+1}/{len(imgs)}] {img_path.name}")
                        else:
                            log(f"  ⚠ Imagen {i+1}: no apareció nuevo input tras clic en +")
                    else:
                        log(f"  ⚠ Imagen {i+1}: no hay más slots disponibles")
            except Exception as e:
                log(f"  ⚠ Error imagen {i+1}: {e}")
    else:
        log(f"  ⚠ Sin imágenes para {sku} (carpeta: {carpeta})")

    # Continuar → Paso 3: Asocia (bodega + precio)
    await next_step(page)
    await page.wait_for_timeout(2500)

    # ══ PASO 3: Asocia — Bodega Ofertix + Precio ══════════════════════════
    # Clic en la tarjeta/botón de "Bodega Ofertix" o "OFERTIX"
    bodega_ok = await click_visible(page, [
        'button:has-text("Ofertix")',
        'button:has-text("OFERTIX")',
        '[class*="store"]:has-text("Ofertix")',
        '[class*="bodega"]:has-text("Ofertix")',
    ], timeout=5000)

    if not bodega_ok:
        bodega_ok = await page.evaluate("""() => {
            const all = [...document.querySelectorAll('*')];
            const el = all.find(e => e.offsetParent !== null
                                  && e.children.length <= 3
                                  && e.textContent.includes('Ofertix'));
            if (!el) return false;
            // Subir hasta encontrar elemento clickeable
            let cur = el;
            for (let i = 0; i < 8; i++) {
                if (!cur || cur === document.body) break;
                if (cur.tagName === 'BUTTON' || cur.getAttribute('role') === 'button'
                    || cur.onclick || cur.style.cursor === 'pointer') {
                    cur.click(); return true;
                }
                cur = cur.parentElement;
            }
            // Si no encontramos button padre, clic directo en el texto
            el.click(); return true;
        }""")

    if bodega_ok:
        log("  🏪 Bodega Ofertix seleccionada")
    else:
        log("  ⚠ No encontré 'Bodega Ofertix' — continuando de todas formas")
    await page.wait_for_timeout(1000)

    # Precio
    precio_ok = await fill_field(page, [
        'input[placeholder*="recio"]',
        'input[placeholder*="Precio"]',
        'input[placeholder*="$ "]',
        'input[type="number"]:visible',
        'input[name*="price"]',
        'input[name*="precio"]',
    ], precio, "Precio")
    await page.wait_for_timeout(400)

    # Botón final: "Asociar" (último paso del wizard)
    asociar_ok = await click_visible(page, [
        'button:has-text("Asociar")',
        'button:has-text("Guardar")',
        'button:has-text("Publicar")',
        'button:has-text("Finalizar")',
        'button:has-text("Crear")',
    ], timeout=5000)

    await page.wait_for_timeout(3000)

    if asociar_ok:
        log(f"  ✅ {sku} creado y asociado")
        return True
    else:
        try:
            await page.screenshot(path=str(IMAGES_BASE / f"err_{sku}.png"))
        except:
            pass
        log(f"  ✗ {sku}: no encontré botón Asociar — ver screenshot")
        return False

# ── Main ───────────────────────────────────────────────────────────────────────
async def main():
    log("=" * 60)
    log(f"RAPPI AUTO UPLOAD — Bodega Ofertix — {len(PRODUCTOS)} productos")
    log("=" * 60)

    if not IMAGES_BASE.exists():
        log(f"ERROR: Carpeta no encontrada: {IMAGES_BASE}")
        sys.exit(1)

    async with async_playwright() as pw:
        ctx = await pw.chromium.launch_persistent_context(
            PROFILE_DIR,
            headless=False,
            slow_mo=200,
            args=["--start-maximized", "--disable-blink-features=AutomationControlled"],
            viewport=None,
        )
        await ctx.add_cookies(parse_cookies(COOKIE_STR))
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()

        log("Verificando sesión en Rappi Mi Tienda...")
        await page.goto(RAPPI_CATALOG, wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(2000)

        if "login" in page.url or "auth" in page.url:
            log("⚠ Sesión expirada. Inicia sesión manualmente. Tienes 120 s...")
            try:
                await page.wait_for_url("**/cms/**", timeout=120000)
                log("✅ Login detectado — comenzando carga...")
            except PWTimeout:
                log("❌ Tiempo agotado. Cerrando.")
                await ctx.close()
                sys.exit(1)
        else:
            log("✅ Sesión activa — URL del formulario: " + RAPPI_STEPS)
            log("   Comenzando carga de productos...")

        await page.wait_for_timeout(1500)

        ok_list, err_list = [], []
        for i, prod in enumerate(PRODUCTOS, 1):
            try:
                result = await crear_producto(page, prod, i, len(PRODUCTOS))
                if result:
                    ok_list.append(prod["sku"])
                else:
                    err_list.append(prod["sku"])
            except Exception as e:
                log(f"  ❌ Error inesperado en {prod['sku']}: {e}")
                try:
                    await page.screenshot(
                        path=str(IMAGES_BASE / f"err_{prod['sku']}_exc.png"))
                except:
                    pass
                err_list.append(prod["sku"])
            await page.wait_for_timeout(800)

        log("=" * 60)
        log(f"✅ Subidos OK: {len(ok_list)}/{len(PRODUCTOS)}  → {ok_list}")
        if err_list:
            log(f"❌ Con errores ({len(err_list)}): {err_list}")
            log(f"   Revisa screenshots err_*.png en {IMAGES_BASE}")
        log(f"Log completo: {LOG_FILE}")
        log("=" * 60)

        input("\nPresiona ENTER para cerrar el navegador...")
        await ctx.close()

if __name__ == "__main__":
    asyncio.run(main())
