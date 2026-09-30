"""
Script: descargar_imagenes_30092026.py
Descarga imágenes del lote 30092026 y aplica fondo blanco a portadas.
Uso: python descargar_imagenes_30092026.py
"""
import requests, io, json
from pathlib import Path
from PIL import Image

try:
    from rembg import remove
    REMBG = True
except ImportError:
    REMBG = False
    print("⚠ rembg no instalado — se omite fondo blanco")

BASE = Path(r"C:\Users\LenovoV14G4-AMN\Pictures\RAP30092026")
HEADERS = {"User-Agent": "Mozilla/5.0"}

def dl(url, dest):
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        r.raise_for_status()
        dest.write_bytes(r.content)
        return True
    except Exception as e:
        print(f"  ⚠ {e}")
        return False

def fondo_blanco(src, dst):
    if not REMBG: return
    try:
        out = remove(src.read_bytes())
        img = Image.open(io.BytesIO(out)).convert('RGBA')
        bg = Image.new('RGBA', img.size, (255,255,255,255))
        bg.paste(img, mask=img.split()[3])
        bg.convert('RGB').save(dst, 'JPEG', quality=95)
        print(f"    ✅ fondo blanco → {dst.name}")
    except Exception as e:
        print(f"    ⚠ fondo blanco: {e}")

PRODUCTOS = [
    ("K2207", ["https://back.ofertix.co/recursos/imagenes/933_K2207.jpg", "https://back.ofertix.co/recursos/imagenes/3-10742-5618_IMG.jpg", "https://back.ofertix.co/recursos/imagenes/3-10742-4013_IMG.jpg", "https://back.ofertix.co/recursos/imagenes/3-10742-3084_IMG.jpg", "https://back.ofertix.co/recursos/imagenes/3-10742-8874_IMG.jpg"]),
    ("K2259", ["https://back.ofertix.co/recursos/imagenes/4184_K2259.jpg", "https://back.ofertix.co/recursos/imagenes/3-10743-7454_IMG.jpg", "https://back.ofertix.co/recursos/imagenes/3-10743-4699_IMG.jpg", "https://back.ofertix.co/recursos/imagenes/3-10743-1925_IMG.jpg", "https://back.ofertix.co/recursos/imagenes/3-10743-8511_IMG.jpg"]),
    ("JH412", ["https://back.ofertix.co/recursos/imagenes/4288_JH412.webp", "https://back.ofertix.co/recursos/imagenes/3-9777-7119_IMG.png", "https://back.ofertix.co/recursos/imagenes/3-9777-4732_IMG.png", "https://back.ofertix.co/recursos/imagenes/3-9777-3295_IMG.png", "https://back.ofertix.co/recursos/imagenes/3-9777-6887_IMG.png"]),
    ("YH6604C", ["https://back.ofertix.co/recursos/imagenes/3718_YH6604C.png", "https://back.ofertix.co/recursos/imagenes/3-10769-8469_IMG.png", "https://back.ofertix.co/recursos/imagenes/3-10769-5514_IMG.png", "https://back.ofertix.co/recursos/imagenes/3-10769-8860_IMG.png", "https://back.ofertix.co/recursos/imagenes/3-10769-2753_IMG.png"]),
    ("MAT005", ["https://back.ofertix.co/recursos/imagenes/601_MAT005.webp", "https://back.ofertix.co/recursos/imagenes/3-9983-9379_IMG.png", "https://back.ofertix.co/recursos/imagenes/3-9983-9179_IMG.jpg", "https://back.ofertix.co/recursos/imagenes/3-9983-3013_IMG.png", "https://back.ofertix.co/recursos/imagenes/3-9983-1224_IMG.png"]),
    ("FS2387A", ["https://back.ofertix.co/recursos/imagenes/9794_J32501.webp"]),
    ("G98046", ["https://back.ofertix.co/recursos/imagenes/165_98046.webp", "https://back.ofertix.co/recursos/imagenes/1870_IMG.jpg", "https://back.ofertix.co/recursos/imagenes/3528_IMG.jpg", "https://back.ofertix.co/recursos/imagenes/3-4237-33_IMG.png"]),
    ("Z002MK1", ["https://back.ofertix.co/recursos/imagenes/9767_Z002MK.webp"]),
    ("T79090R", ["https://back.ofertix.co/recursos/imagenes/5049_T79090R.png", "https://back.ofertix.co/recursos/imagenes/3-10942-9847_IMG.png", "https://back.ofertix.co/recursos/imagenes/3-10942-4995_IMG.png", "https://back.ofertix.co/recursos/imagenes/3-10942-6564_IMG.png", "https://back.ofertix.co/recursos/imagenes/3-10942-7676_IMG.png"]),
    ("RA123", ["https://back.ofertix.co/recursos/imagenes/7537_RA123.webp", "https://back.ofertix.co/recursos/imagenes/3-9730-7197_IMG.jpeg", "https://back.ofertix.co/recursos/imagenes/3-9730-7513_IMG.jpeg", "https://back.ofertix.co/recursos/imagenes/3-9730-4103_IMG.jpeg", "https://back.ofertix.co/recursos/imagenes/3-9730-8431_IMG.jpeg"]),
    ("SM102", ["https://back.ofertix.co/recursos/imagenes/8317_SM102.webp", "https://back.ofertix.co/recursos/imagenes/3-10187-7330_IMG.jpg", "https://back.ofertix.co/recursos/imagenes/3-10187-9223_IMG.jpg", "https://back.ofertix.co/recursos/imagenes/3-10187-4428_IMG.jpg"]),
    ("FS23810A", ["https://back.ofertix.co/recursos/imagenes/4594_J1555.webp", "https://back.ofertix.co/recursos/imagenes/5976_IMG.jpeg"]),
    ("T79090D", ["https://back.ofertix.co/recursos/imagenes/4291_T79090D.png", "https://back.ofertix.co/recursos/imagenes/3-10945-1586_IMG.png", "https://back.ofertix.co/recursos/imagenes/3-10945-974_IMG.png", "https://back.ofertix.co/recursos/imagenes/3-10945-5727_IMG.png", "https://back.ofertix.co/recursos/imagenes/3-10945-1361_IMG.png"]),
    ("H110VA", ["https://back.ofertix.co/recursos/imagenes/2216_H110VA.webp", "https://back.ofertix.co/recursos/imagenes/3-9425-1255_IMG.jpg", "https://back.ofertix.co/recursos/imagenes/3-9425-2125_IMG.png", "https://back.ofertix.co/recursos/imagenes/3-9425-4334_IMG.jpg", "https://back.ofertix.co/recursos/imagenes/3-9425-2417_IMG.jpg"]),
    ("CY0117B", ["https://back.ofertix.co/recursos/imagenes/7987_CY0117B.webp", "https://back.ofertix.co/recursos/imagenes/3-9921-1341_IMG.jpeg", "https://back.ofertix.co/recursos/imagenes/3-9921-9255_IMG.jpeg", "https://back.ofertix.co/recursos/imagenes/3-9921-3967_IMG.jpeg", "https://back.ofertix.co/recursos/imagenes/3-9921-2254_IMG.jpeg"]),
    ("SK09023", ["https://back.ofertix.co/recursos/imagenes/6014_SK09023.webp", "https://back.ofertix.co/recursos/imagenes/3-10318-1175_IMG.jpg", "https://back.ofertix.co/recursos/imagenes/3-10318-1968_IMG.png", "https://back.ofertix.co/recursos/imagenes/3-10318-5828_IMG.png", "https://back.ofertix.co/recursos/imagenes/3-10318-1343_IMG.png"]),
    ("SD9952A", ["https://back.ofertix.co/recursos/imagenes/3423_SD9952A.png", "https://back.ofertix.co/recursos/imagenes/3-10877-248_IMG.png", "https://back.ofertix.co/recursos/imagenes/3-10877-8611_IMG.png", "https://back.ofertix.co/recursos/imagenes/3-10877-1248_IMG.png", "https://back.ofertix.co/recursos/imagenes/3-10877-9379_IMG.png"]),
    ("LBI4602", ["https://back.ofertix.co/recursos/imagenes/7087_LBI4602.png", "https://back.ofertix.co/recursos/imagenes/3-10250-6959_IMG.jpg", "https://back.ofertix.co/recursos/imagenes/3-10250-3742_IMG.jpg", "https://back.ofertix.co/recursos/imagenes/3-10250-0_IMG.jpg", "https://back.ofertix.co/recursos/imagenes/3-10250-4762_IMG.png"]),
    ("LBI4602R", ["https://back.ofertix.co/recursos/imagenes/9193_LBI4602R.webp", "https://back.ofertix.co/recursos/imagenes/3-10361-1651_IMG.png", "https://back.ofertix.co/recursos/imagenes/3-10361-7532_IMG.png", "https://back.ofertix.co/recursos/imagenes/3-10361-8909_IMG.png", "https://back.ofertix.co/recursos/imagenes/3-10361-957_IMG.png"]),
    ("F25120N", ["https://back.ofertix.co/recursos/imagenes/674_F25120N.webp", "https://back.ofertix.co/recursos/imagenes/3972_IMG.jpg", "https://back.ofertix.co/recursos/imagenes/1031_IMG.jpg", "https://back.ofertix.co/recursos/imagenes/355_IMG.jpg"]),
    ("MZ5807", ["https://back.ofertix.co/recursos/imagenes/1745_MZ5807.webp", "https://back.ofertix.co/recursos/imagenes/6349_IMG.png"]),
    ("CFZ205", ["https://back.ofertix.co/recursos/imagenes/7346_CFZ205.webp", "https://back.ofertix.co/recursos/imagenes/3-8761-2215_IMG.png", "https://back.ofertix.co/recursos/imagenes/3-8761-9039_IMG.png", "https://back.ofertix.co/recursos/imagenes/3-8761-4382_IMG.png", "https://back.ofertix.co/recursos/imagenes/3-8761-2650_IMG.png"]),
]

for sku, urls in PRODUCTOS:
    folder = BASE / sku
    folder.mkdir(parents=True, exist_ok=True)
    for idx, url in enumerate(urls, 1):
        ext = url.split('.')[-1].split('?')[0].lower()
        if ext not in ['jpg','jpeg','png','webp']: ext = 'jpg'
        dest = folder / f"{sku}{idx}.{ext}"
        print(f"  [{idx}/{len(urls)}] {url.split('/')[-1]}")
        if dl(url, dest) and idx == 1:
            wb = folder / f"{sku}1_wb.jpg"
            fondo_blanco(dest, wb)
    print(f"✅ {sku} — {len(urls)} imgs")

print("\n🏁 Descarga completa.")
