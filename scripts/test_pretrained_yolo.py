"""
Script para probar YOLO pre-entrenado (COCO) con imagen de huevos
Esto nos da una línea base antes de hacer fine-tuning
"""
from ultralytics import YOLO
import cv2
import os

def test_pretrained_yolo(image_path):
    """
    Prueba YOLOv8 pre-entrenado en COCO dataset.
    COCO no tiene clase 'egg', pero puede detectar objetos circulares.
    """
    print("=" * 60)
    print("PRUEBA DE YOLO PRE-ENTRENADO (COCO)")
    print("=" * 60)
    
    if not os.path.exists(image_path):
        print(f"❌ Imagen no encontrada: {image_path}")
        print("\n📸 Coloca una imagen de prueba en:")
        print("   Web/test_images/eggs_test.jpg")
        return
    
    # 1. Cargar modelo pre-entrenado
    print("\n[1/3] Descargando modelo YOLOv8n pre-entrenado...")
    model = YOLO('yolov8n.pt')  # Se descarga automáticamente
    print("✓ Modelo cargado (entrenado en COCO dataset)")
    
    # 2. Ver clases disponibles
    print("\n[2/3] Clases disponibles en COCO:")
    print(f"   Total: {len(model.names)} clases")
    print(f"   Ejemplos: {list(model.names.values())[:10]}...")
    
    # 3. Detectar objetos
    print("\n[3/3] Procesando imagen...")
    image = cv2.imread(image_path)
    
    # Probar con diferentes configuraciones
    configs = [
        {'conf': 0.25, 'iou': 0.45, 'name': 'Estándar'},
        {'conf': 0.15, 'iou': 0.30, 'name': 'Sensible'},
        {'conf': 0.40, 'iou': 0.60, 'name': 'Estricto'},
    ]
    
    best_result = None
    best_count = 0
    
    for config in configs:
        results = model(image, conf=config['conf'], iou=config['iou'], verbose=False)
        
        # Contar detecciones
        count = 0
        for result in results:
            count += len(result.boxes)
        
        print(f"\n   {config['name']} (conf={config['conf']}, iou={config['iou']}): {count} objetos")
        
        # Mostrar clases detectadas
        if count > 0:
            classes_detected = {}
            for result in results:
                for box in result.boxes:
                    cls = int(box.cls[0])
                    class_name = model.names[cls]
                    classes_detected[class_name] = classes_detected.get(class_name, 0) + 1
            
            print(f"   Clases: {classes_detected}")
        
        if count > best_count:
            best_count = count
            best_result = (results, config)
    
    # 4. Guardar mejor resultado
    if best_result:
        results, config = best_result
        print(f"\n✓ Mejor configuración: {config['name']} con {best_count} detecciones")
        
        # Dibujar resultados
        output_image = image.copy()
        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                class_name = model.names[cls]
                
                # Dibujar bounding box
                cv2.rectangle(output_image, (int(x1), int(y1)), (int(x2), int(y2)), 
                            (0, 255, 0), 2)
                
                # Etiqueta
                label = f'{class_name} {conf:.2f}'
                cv2.putText(output_image, label, (int(x1), int(y1) - 10),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Contador
        cv2.putText(output_image, f'Objetos detectados: {best_count}',
                   (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
        
        # Guardar
        output_dir = 'test_results'
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, 'yolo_pretrained_result.jpg')
        cv2.imwrite(output_path, output_image)
        
        print(f"\n📊 Resultado guardado en: {output_path}")
    else:
        print("\n❌ No se detectaron objetos")
    
    print("\n" + "=" * 60)
    print("CONCLUSIÓN")
    print("=" * 60)
    print("\nYOLO pre-entrenado (COCO) NO está optimizado para huevos.")
    print("Puede detectar objetos circulares como 'sports ball', 'orange', etc.")
    print("\n💡 Para 95%+ precisión, necesitas FINE-TUNING con dataset de huevos.")
    print("   Ejecuta: python scripts/train_yolo.py")
    
    return best_count

if __name__ == "__main__":
    # Buscar imagen de prueba
    test_paths = [
        'test_images/eggs_test.jpg',
        'media/temp_vision/egg_count_*.jpg',  # Última imagen subida
    ]
    
    image_path = None
    for path in test_paths:
        if '*' in path:
            # Buscar archivos que coincidan
            import glob
            matches = glob.glob(path)
            if matches:
                image_path = matches[-1]  # Más reciente
                break
        elif os.path.exists(path):
            image_path = path
            break
    
    if image_path:
        print(f"\n📸 Usando imagen: {image_path}\n")
        count = test_pretrained_yolo(image_path)
    else:
        print("\n❌ No se encontró imagen de prueba")
        print("\n📸 Opciones:")
        print("   1. Coloca una imagen en: test_images/eggs_test.jpg")
        print("   2. O sube una imagen desde la web (se guardará en media/temp_vision/)")
        print("\nLuego ejecuta: python scripts/test_pretrained_yolo.py")
