import os
import uuid
from pathlib import Path
from urllib.parse import urlparse

import httpx

UPLOADS_DIR = Path("uploads")
CROPS_UPLOADS_DIR = UPLOADS_DIR / "crops"
DEFAULT_IMAGE_FILENAME = "default.jpg"
DEFAULT_IMAGE_PATH = CROPS_UPLOADS_DIR / DEFAULT_IMAGE_FILENAME
DEFAULT_IMAGE_URL = f"/uploads/crops/{DEFAULT_IMAGE_FILENAME}"
PEXELS_SEARCH_URL = "https://api.pexels.com/v1/search"
PEXELS_API_KEY = "SCtNi9A0xue4SGQDsccF3xR8vVzS5W1Rd4n8o4G1fiSS9iSW6SVRPD09"
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def ensure_crop_uploads_dir() -> None:
    CROPS_UPLOADS_DIR.mkdir(parents=True, exist_ok=True)


def get_default_crop_image_url() -> str:
    ensure_crop_uploads_dir()
    return DEFAULT_IMAGE_URL


def get_extension_from_content_type(content_type: str | None) -> str:
    mapping = {
        "image/jpeg": ".jpg",
        "image/jpg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
    }
    return mapping.get((content_type or "").lower(), ".jpg")


def get_extension_from_url(image_url: str) -> str:
    parsed = urlparse(image_url)
    suffix = Path(parsed.path).suffix.lower()
    if suffix in ALLOWED_IMAGE_EXTENSIONS:
        return suffix
    return ".jpg"


def build_relative_image_url(filename: str) -> str:
    return f"/uploads/crops/{filename}"


def save_bytes_to_crop_uploads(file_bytes: bytes, extension: str) -> str:
    ensure_crop_uploads_dir()
    filename = f"{uuid.uuid4().hex}{extension}"
    file_path = CROPS_UPLOADS_DIR / filename
    file_path.write_bytes(file_bytes)
    return build_relative_image_url(filename)


def save_uploaded_crop_image(upload_file) -> str:
    content_type = upload_file.content_type or ""
    if not content_type.startswith("image/"):
        raise ValueError("Uploaded file must be an image")

    file_bytes = upload_file.file.read()
    if not file_bytes:
        raise ValueError("Uploaded image is empty")

    extension = get_extension_from_content_type(content_type)
    return save_bytes_to_crop_uploads(file_bytes, extension)


def fetch_pexels_image_url(crop_name: str, crop_type: str | None = None) -> str | None:
    api_key = PEXELS_API_KEY
    if not api_key:
        print("❌ API key de Pexels no configurada")
        return None

    query_parts = [crop_name.strip()]
    if crop_type and crop_type.strip():
        query_parts.append(crop_type.strip())
    query_parts.append("agriculture plant")
    query = " ".join(query_parts)

    headers = {"Authorization": api_key}
    params = {"query": query, "per_page": 1, "orientation": "landscape"}

    try:
        print(f"📡 Consultando Pexels API con query: '{query}'")
        with httpx.Client(timeout=10.0, follow_redirects=True) as client:
            response = client.get(PEXELS_SEARCH_URL, headers=headers, params=params)
            response.raise_for_status()

        payload = response.json()
        photos = payload.get("photos") or []
        if not photos:
            print(f"⚠️ Pexels no retornó fotos para: '{query}'")
            return None

        src = (photos[0] or {}).get("src") or {}
        image_url = src.get("large2x") or src.get("large") or src.get("original")
        print(f"✅ Imagen encontrada: {image_url}")
        return image_url
    except (httpx.HTTPError, ValueError, KeyError) as e:
        print(f"❌ Error consultando Pexels: {e}")
        return None


def download_and_store_crop_image(image_url: str) -> str | None:
    try:
        print(f"⬇️ Descargando imagen: {image_url}")
        with httpx.Client(timeout=15.0, follow_redirects=True) as client:
            response = client.get(image_url)
            response.raise_for_status()

        extension = get_extension_from_content_type(response.headers.get("content-type"))
        if extension == ".jpg":
            extension = get_extension_from_url(image_url)

        print(f"💾 Almacenando con extensión: {extension}")
        result = save_bytes_to_crop_uploads(response.content, extension)
        print(f"✅ Guardado en: {result}")
        return result
    except (httpx.HTTPError, OSError) as e:
        print(f"❌ Error descargando imagen: {e}")
        return None


def fetch_and_store_crop_image(crop_name: str, crop_type: str | None = None) -> str:
    print(f"🔍 Buscando imagen para: {crop_name} ({crop_type})")
    remote_image_url = fetch_pexels_image_url(crop_name, crop_type)
    if remote_image_url:
        print(f"✅ URL encontrada en Pexels: {remote_image_url}")
        stored_image_url = download_and_store_crop_image(remote_image_url)
        if stored_image_url:
            print(f"✅ Imagen guardada en: {stored_image_url}")
            return stored_image_url
        else:
            print("❌ Error al descargar/guardar imagen")
    else:
        print("❌ No se encontró imagen en Pexels")

    print(f"ℹ️ Usando imagen por defecto")
    return get_default_crop_image_url()
