"""
Script para entrenar YOLOv8 con el dataset de huevos de Roboflow
Usa transfer learning desde modelo pre-entrenado en COCO
"""
from ultralytics import YOLO
import os

def train_egg_detector():
    """
    Entrena modelo YOLO para detectar huevos usando transfer learning.
    """
    print("=" * 60)
    print("ENTRENAMIENTO DE MODELO YOLO PARA DETECCIÓN DE HUEVOS")
    print("=" * 60)
    
    # 1. Cargar modelo pre-entrenado
    print("\n[1/4] Cargando modelo YOLOv8 pre-entrenado...")
    model = YOLO('yolov8n.pt')  # nano (rápido) - cambiar a yolov8s.pt para más precisión
    print("✓ Modelo cargado: YOLOv8n (pre-entrenado en COCO)")
    
    # 2. Configurar entrenamiento
    print("\n[2/4] Configurando entrenamiento...")
    data_yaml = 'datasets/eggs/data.yaml'
    
    if not os.path.exists(data_yaml):
        print("❌ ERROR: Dataset no encontrado")
        print(f"   Esperado en: {data_yaml}")
        print("\n📥 DESCARGA EL DATASET PRIMERO:")
        print("   1. Ve a: https://universe.roboflow.com/roboflow-universe/eggs")
        print("   2. Click 'Download Dataset'")
        print("   3. Selecciona formato 'YOLOv8'")
        print("   4. Descarga y extrae en: datasets/eggs/")
        return None
    
    # 3. Entrenar con transfer learning
    print("\n[3/4] Iniciando entrenamiento...")
    print("⏱️  Tiempo estimado: 30-60 minutos (depende de tu hardware)")
    print("-" * 60)
    
    results = model.train(
        data=data_yaml,
        epochs=50,              # Número de épocas (ajustar según resultados)
        imgsz=640,              # Tamaño de imagen
        batch=8,                # Batch size (reducir si hay error de memoria)
        device='cpu',           # Cambiar a 'cuda' si tienes GPU
        patience=10,            # Early stopping
        save=True,              # Guardar checkpoints
        project='runs/train',   # Directorio de salida
        name='egg_detector',    # Nombre del experimento
        exist_ok=True,          # Sobrescribir si existe
        pretrained=True,        # Usar pesos pre-entrenados
        optimizer='Adam',       # Optimizador
        verbose=True,           # Mostrar progreso
        seed=42,                # Semilla para reproducibilidad
        deterministic=True,
        single_cls=True,        # Una sola clase (huevos)
        
        # Augmentations (mejoran generalización)
        hsv_h=0.015,           # Variación de matiz
        hsv_s=0.7,             # Variación de saturación
        hsv_v=0.4,             # Variación de valor
        degrees=10,            # Rotación
        translate=0.1,         # Traslación
        scale=0.5,             # Escala
        shear=0.0,             # Shear
        perspective=0.0,       # Perspectiva
        flipud=0.0,            # Flip vertical
        fliplr=0.5,            # Flip horizontal
        mosaic=1.0,            # Mosaic augmentation
        mixup=0.0,             # Mixup augmentation
    )
    
    print("\n✓ Entrenamiento completado!")
    
    # 4. Validar modelo
    print("\n[4/4] Validando modelo...")
    metrics = model.val()
    
    print("\n" + "=" * 60)
    print("RESULTADOS DEL ENTRENAMIENTO")
    print("=" * 60)
    print(f"mAP50:     {metrics.box.map50:.3f} (Precisión al 50% IoU)")
    print(f"mAP50-95:  {metrics.box.map:.3f} (Precisión promedio)")
    print(f"Precisión: {metrics.box.mp:.3f}")
    print(f"Recall:    {metrics.box.mr:.3f}")
    
    # 5. Guardar modelo optimizado
    print("\n[5/5] Exportando modelo...")
    model_path = model.export(format='onnx')  # ONNX es más rápido para inferencia
    print(f"✓ Modelo exportado a: {model_path}")
    
    # Copiar a directorio de modelos de Django
    import shutil
    django_model_dir = '../models'
    os.makedirs(django_model_dir, exist_ok=True)
    
    final_path = os.path.join(django_model_dir, 'egg_detector.onnx')
    shutil.copy(model_path, final_path)
    print(f"✓ Modelo copiado a: {final_path}")
    
    print("\n" + "=" * 60)
    print("🎉 ¡ENTRENAMIENTO EXITOSO!")
    print("=" * 60)
    print("\n📊 Revisa los resultados en: runs/train/egg_detector/")
    print("📈 Gráficas de entrenamiento: runs/train/egg_detector/results.png")
    print("🔍 Ejemplos de validación: runs/train/egg_detector/val_batch*.jpg")
    
    return model

if __name__ == "__main__":
    model = train_egg_detector()
    
    if model:
        print("\n✅ Modelo listo para usar en Django!")
        print("   Reinicia el servidor para que cargue el nuevo modelo.")
