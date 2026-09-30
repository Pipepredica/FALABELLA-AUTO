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

async def crear_producto(page, prod, idx, total):
    sku    = prod["sku"]
    nombre = prod["nombre"]
    precio = str(prod["precio"])
    desc   = prod["desc"]
    cat    = prod["cat"]   # [L1, L2, L3]

    # Imágenes del producto
    carpeta = IMAGES_BASE / sku
    imgs = []
    if carpeta.exists():
        wb   = sorted(carpeta.glob(f"{sku}*_wb.jpg"))
        rest = [p for p in sorted(carpeta.glob(f"{sku}*.jpg")) if "_wb" not in p.name]
        rest += sorted(carpeta.glob(f"{sku}*.png"))
        imgs = (wb + rest)[:4]

    log(f"[{idx}/{total}] ▶ {sku}  precio=${precio}  imgs={len(imgs)}")

    # ── Ir directo al formulario "Desde cero" ──────────────────────────────
    await page.goto(RAPPI_STEPS, wait_until="networkidle", timeout=30000)
    await page.wait_for_timeout(2000)

    # ── PASO A: seleccionar categorías por chips ────────────────────────────
    # L1 — categoría principal
    ok_l1 = await click_chip(page, cat[0])
    if not ok_l1:
        log(f"  ⚠ No encontré categoría L1: {cat[0]}")
    await page.wait_for_timeout(1000)

    # L2 — subcategoría 1 (aparece tras seleccionar L1)
    if len(cat) > 1:
        ok_l2 = await click_chip(page, cat[1])
        if not ok_l2:
            log(f"  ⚠ No encontré subcategoría L2: {cat[1]}")
        await page.wait_for_timeout(1000)

    # L3 — subcategoría 2 (aparece tras seleccionar L2)
    if len(cat) > 2:
        ok_l3 = await click_chip(page, cat[2])
        if not ok_l3:
            log(f"  ⚠ No encontré subcategoría L3: {cat[2]}")
        await page.wait_for_timeout(800)

    # Avanzar al siguiente paso (nombre/precio/descripción)
    await next_step(page)
    await page.wait_for_timeout(2000)

    # ── PASO B: Sección 1 — Nombre, SKU, Descripción ───────────────────────
    await fill_field(page, [
        'input[placeholder="Nombre del producto"]',
        'input[placeholder*="ombre del producto"]',
        'input[placeholder*="Nombre"]',
    ], nombre, "nombre")
    await page.wait_for_timeout(300)

    await fill_field(page, [
        'input[placeholder="SKU"]',
        'input[placeholder*="SKU"]',
        'input[name="sku"]',
        'input[id*="sku"]',
    ], sku, "SKU")
    await page.wait_for_timeout(300)

    await fill_field(page, [
        'textarea[placeholder="Descripción del producto"]',
        'textarea[placeholder*="escripción del producto"]',
        'textarea[placeholder*="Ej:"]',
        'textarea:visible',
    ], desc, "descripción")
    await page.wait_for_timeout(300)

    # Continuar → Ficha técnica
    await next_step(page)
    await page.wait_for_timeout(2500)

    # ── PASO C: Ficha técnica — OBLIGATORIO: Cantidad=1, Unidad=UND ──────────
    await page.wait_for_timeout(1500)

    # Cantidad: campo numérico (generalmente un input type=number o text)
    cantidad_ok = await fill_field(page, [
        'input[placeholder*="antidad"]',
        'input[placeholder="Cantidad"]',
        'input[name*="antidad"]',
        'input[name*="quantity"]',
        'input[aria-label*="antidad"]',
    ], "1", "Cantidad")

    if not cantidad_ok:
        # Intentar con el primer input numérico visible de la ficha técnica
        try:
            num_inputs = page.locator('input[type="number"]:visible, input[type="text"]:visible')
            cnt = await num_inputs.count()
            if cnt > 0:
                el = num_inputs.first
                await el.triple_click()
                await el.fill("1")
                await page.keyboard.press("Tab")
                cantidad_ok = True
                log("  Cantidad: llenado con primer input numérico")
        except Exception as e:
            log(f"  ⚠ Cantidad: {e}")

    await page.wait_for_timeout(500)

    # Unidad: dropdown/combobox → seleccionar "UND"
    unidad_ok = False
    # Estrategia 1: combobox con aria-label o placeholder Unidad
    for dd_sel in [
        '[aria-label*="nidad"]',
        '[placeholder*="nidad"]',
        '[role="combobox"]:visible',
        'select:visible',
    ]:
        try:
            el = page.locator(dd_sel).first
            if await el.is_visible(timeout=2000):
                tag = await el.evaluate("el => el.tagName.toLowerCase()")
                if tag == "select":
                    await el.select_option(label="UND")
                else:
                    await el.click()
                    await page.wait_for_timeout(700)
                    # Buscar opción "UND" en el menú desplegado
                    for opt_sel in [
                        ':text-is("UND")',
                        '[role="option"]:has-text("UND")',
                        'li:has-text("UND")',
                        'div[role="option"]:has-text("UND")',
                    ]:
                        try:
                            opt = page.locator(opt_sel).first
                            if await opt.is_visible(timeout=1500):
                                await opt.click()
                                unidad_ok = True
                                break
                        except:
                            pass
                    if not unidad_ok:
                        # Intentar con keyboard: teclear "UND"
                        await page.keyboard.type("UND")
                        await page.wait_for_timeout(500)
                        for opt_sel in [
                            ':text-is("UND")',
                            '[role="option"]:has-text("UND")',
                            'li:has-text("UND")',
                        ]:
                            try:
                                opt = page.locator(opt_sel).first
                                if await opt.is_visible(timeout=1500):
                                    await opt.click()
                                    unidad_ok = True
                                    break
                            except:
                                pass
                if unidad_ok:
                    break
        except:
            pass

    if cantidad_ok:
        log("  ✅ Ficha técnica: Cantidad=1")
    if unidad_ok:
        log("  ✅ Ficha técnica: Unidad=UND")
    if not cantidad_ok or not unidad_ok:
        log(f"  ⚠ Ficha técnica incompleta (cantidad={cantidad_ok}, unidad={unidad_ok})")

    await page.wait_for_timeout(800)
    # Continuar → Imágenes
    await next_step(page)
    await page.wait_for_timeout(2500)

    # ── PASO D: Imágenes — una por una ──────────────────────────────────────
    if imgs:
        for i, img_path in enumerate(imgs):
            # Cada imagen puede tener su propio input o un botón "+"
            try:
                # Buscar el i-ésimo input de archivo disponible
                file_inputs = page.locator('input[type="file"]')
                fi_cnt = await file_inputs.count()
                if i < fi_cnt:
                    await file_inputs.nth(i).set_input_files(str(img_path))
                    await page.wait_for_timeout(3000)
                    log(f"  📷 Imagen {i+1}/{len(imgs)}: {img_path.name}")
                else:
                    # Buscar botón "+" para agregar más imágenes
                    add_btn = await click_visible(page, [
                        'button:has-text("+")',
                        '[aria-label*="agregar"]',
                        '[aria-label*="Agregar"]',
                        '[class*="add"]:visible',
                        'button[class*="upload"]:visible',
                    ], timeout=2000)
                    if add_btn:
                        await page.wait_for_timeout(800)
                        fi_cnt2 = await file_inputs.count()
                        if fi_cnt2 > i:
                            await file_inputs.nth(i).set_input_files(str(img_path))
                            await page.wait_for_timeout(3000)
                            log(f"  📷 Imagen {i+1}/{len(imgs)}: {img_path.name}")
            except Exception as e:
                log(f"  ⚠ Error subiendo imagen {i+1}: {e}")

    # Continuar → Selección de bodega / precio
    await next_step(page)
    await page.wait_for_timeout(2500)

    # ── PASO E: Seleccionar "Bodega Ofertix" ────────────────────────────────
    bodega_ok = await click_visible(page, [
        'button:has-text("Ofertix")',
        'button:has-text("OFERTIX")',
        'div:has-text("Ofertix") >> button',
        '[class*="bodega"]:has-text("Ofertix")',
        ':text("Ofertix")',
        'text=Ofertix',
    ], timeout=5000)
    if not bodega_ok:
        # Intentar con JS como hicimos con "Desde cero"
        bodega_ok = await page.evaluate("""() => {
            const heading = [...document.querySelectorAll('*')]
                .find(el => el.children.length === 0
                         && el.textContent.includes('Ofertix'));
            if (heading) {
                let el = heading.parentElement;
                for (let i = 0; i < 6; i++) {
                    if (!el || el === document.body) break;
                    const btn = el.querySelector('button');
                    if (btn) { btn.click(); return true; }
                    el = el.parentElement;
                }
            }
            return false;
        }""")
    if bodega_ok:
        log("  🏪 Bodega Ofertix seleccionada")
    else:
        log("  ⚠ No encontré 'Bodega Ofertix' — intentando continuar de todas formas")
    await page.wait_for_timeout(1500)

    # ── PASO F: Precio ──────────────────────────────────────────────────────
    await fill_field(page, [
        'input[placeholder*="Precio"]',
        'input[placeholder*="recio"]',
        'input[placeholder*="$ "]',
        'input[type="number"]:visible',
        'input[name="price"]',
        'input[name="precio"]',
    ], precio, "precio")
    await page.wait_for_timeout(400)

    # Continuar → guardar/publicar
    await next_step(page)
    await page.wait_for_timeout(3000)

    # ── PASO G: confirmar guardado ──────────────────────────────────────────
    # El producto ya debería estar creado tras el último "Continuar".
    # Si hay botón de confirmación adicional, clicamos.
    await click_visible(page, [
        'button:has-text("Guardar")',
        'button:has-text("Crear producto")',
        'button:has-text("Publicar")',
        'button:has-text("Finalizar")',
    ], timeout=3000)
    await page.wait_for_timeout(2000)

    # Verificar que salimos del formulario (URL cambia o aparece confirmación)
    cur_url = page.url
    if "steps" not in cur_url or "product-list" in cur_url:
        log(f"  ✅ {sku} creado exitosamente")
        return True
    else:
        await page.screenshot(path=str(IMAGES_BASE / f"err_{sku}_guardar.png"))
        log(f"  ✗ {sku}: formulario sigue abierto tras Continuar — ver screenshot")
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
