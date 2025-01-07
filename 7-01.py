import os
import json
from PIL import Image
from typing import List, Dict, Union
import logging
from datetime import datetime
import hashlib
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
import multiprocessing

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('dataset_creation.log'),
        logging.StreamHandler()
    ]
)

AUTHOR = "Nom de l'auteur"
BASE_DIR = os.path.expanduser("~")
IMAGES_DIR = os.path.join(BASE_DIR, "images")
OUTPUT_DIR = os.path.join(BASE_DIR, "output_coco")
OUTPUT_JSON = os.path.join(OUTPUT_DIR, f"dataset_coco_art_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif'}
DATABASE_JSON = os.path.join(BASE_DIR, "Base_datos.json")

def setup_directories() -> None:
    """Crear los directorios necesarios."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    if not os.path.exists(IMAGES_DIR):
        os.makedirs(IMAGES_DIR)

def load_categories_from_file(json_file: str) -> List[Dict]:
    """Cargar categorías desde un archivo JSON."""
    try:
        with open(json_file, 'r', encoding='utf-8') as file:
            data = json.load(file)
            if "annotations" in data and "categories" in data:
                return data["categories"]
            else:
                raise KeyError("El archivo JSON no contiene las claves necesarias: 'categories'.")
    except Exception as e:
        logging.error(f"Error al cargar las categorías: {str(e)}")
        raise

def validate_image_path(image_path: str) -> bool:
    """Validar si el archivo es una imagen válida."""
    if not os.path.exists(image_path):
        return False
    return os.path.splitext(image_path)[1].lower() in ALLOWED_EXTENSIONS

def determine_category(filename: str, categories: List[Dict]) -> int:
    """Determinar la categoría de una imagen basada en su nombre."""
    filename_lower = filename.lower()
    for category in categories:
        if category["name"].lower() in filename_lower:
            return category["id"]
    return categories[-1]["id"]  # Última categoría como predeterminada.

def create_coco_dataset(images_dir: str, categories: List[Dict]) -> Dict:
    """Crear un dataset en formato COCO."""
    images = []
    annotations = []
    hashes = set()
    image_id = 1
    errors = []
    
    if not os.path.exists(images_dir):
        raise FileNotFoundError(f"El directorio {images_dir} no existe.")
    
    image_files = [f for f in os.listdir(images_dir) 
                   if validate_image_path(os.path.join(images_dir, f))]
    
    for filename in tqdm(image_files, desc="Procesando imágenes"):
        try:
            image_path = os.path.join(images_dir, filename)
            
            with open(image_path, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
                if file_hash in hashes:
                    logging.warning(f"Imagen duplicada ignorada: {filename}")
                    continue
            
            with Image.open(image_path) as img:
                width, height = img.size
                
                images.append({
                    "id": image_id,
                    "file_name": filename,
                    "width": width,
                    "height": height,
                    "date_captured": datetime.now().isoformat(),
                    "author": AUTHOR,
                    "license": 1,
                    "coco_url": "",
                    "flickr_url": ""
                })
                
                category_id = determine_category(filename, categories)
                annotations.append({
                    "id": image_id,
                    "image_id": image_id,
                    "category_id": category_id,
                    "bbox": [0, 0, width, height],
                    "area": width * height,
                    "iscrowd": 0,
                    "segmentation": []
                })
                image_id += 1
            
        except Exception as e:
            errors.append(f"Error procesando {filename}: {str(e)}")
            logging.error(f"Error procesando {filename}: {str(e)}")
    
    return {
        "info": {
            "year": datetime.now().year,
            "version": "1.0",
            "description": "Dataset COCO generado automáticamente",
            "contributor": AUTHOR,
            "date_created": datetime.now().isoformat()
        },
        "images": images,
        "annotations": annotations,
        "categories": categories,
        "licenses": [
            {"id": 1, "name": "Licencia genérica", "url": ""}
        ]
    }

def main():
    try:
        setup_directories()
        
        # Cargar categorías desde el archivo proporcionado.
        categories = load_categories_from_file('/home/cerro/myvenv/Base_datos.json')  # Ruta del JSON cargado.
        
        dataset = create_coco_dataset(IMAGES_DIR, categories)
        
        with open(OUTPUT_JSON, "w", encoding='utf-8') as f:
            json.dump(dataset, f, indent=4, ensure_ascii=False)
        
        logging.info(f"Dataset guardado en {OUTPUT_JSON}")
    except Exception as e:
        logging.error(f"Error durante la ejecución: {str(e)}")

if __name__ == "__main__":
    main()
