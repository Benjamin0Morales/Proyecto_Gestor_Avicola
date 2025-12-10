"""
Script para copiar el modelo YOLO pre-entrenado al directorio de modelos de Django
"""
import shutil
import os
from ultralytics import YOLO

def setup_yolo_model():
    print("=" * 60)
    print("INTEGRACIÓN DE YOLO EN DJANGO")
    print("=" * 60)
    
    # 1. Asegurar directorio de modelos
    models_dir = 'models'
    os.makedirs(models_dir, exist_ok=True)
    
    # 2. Descargar modelo si no existe
    print("\n[1/3] Verificando modelo YOLOv8n...")
    model = YOLO('yolov8n.pt')  # Descarga automática
    
    # 3. Copiar a directorio de modelos
    dest_path = os.path.join(models_dir, 'yolov8n.pt')
    shutil.copy('yolov8n.pt', dest_path)
    print(f"✓ Modelo copiado a: {dest_path}")
    
    print("\n[3/3] Configuración completada!")
    print("\n✅ YOLO listo para usar en la aplicación web.")
    print("   El servicio usará yolov8n.pt pre-entrenado.")

if __name__ == "__main__":
    setup_yolo_model()
