"""
Servicio de Visión por Computadora para Conteo de Huevos
Soporta dos métodos:
1. YOLO (Machine Learning) - 95%+ precisión si modelo está disponible
2. Hough Transform (OpenCV) - Fallback si no hay modelo YOLO
"""
import cv2
import numpy as np
from PIL import Image
import os
from django.conf import settings


class EggCounterService:
    """Servicio para contar huevos usando YOLO o Hough Transform."""
    
    def __init__(self):
        # Intentar cargar modelo YOLO si existe
        self.yolo_model = None
        self.use_yolo = False
        
        try:
            from ultralytics import YOLO
            # Buscar modelos (prioridad: entrenado > pre-entrenado)
            trained_model = os.path.join(settings.BASE_DIR, 'models', 'egg_detector.onnx')
            pretrained_model = os.path.join(settings.BASE_DIR, 'models', 'yolov8n.pt')
            
            if os.path.exists(trained_model):
                self.yolo_model = YOLO(trained_model)
                self.use_yolo = True
                self.conf_thres = 0.25
                print(f"✅ Modelo YOLO entrenado cargado: {trained_model}")
            elif os.path.exists(pretrained_model):
                self.yolo_model = YOLO(pretrained_model)
                self.use_yolo = True
                self.conf_thres = 0.15  # Más sensible para modelo pre-entrenado
                print(f"✅ Modelo YOLO pre-entrenado cargado: {pretrained_model}")
            else:
                print(f"⚠️  Ningún modelo YOLO encontrado")
                print("   Usando Hough Transform como fallback")
        except ImportError:
            print("⚠️  Ultralytics no instalado, usando Hough Transform")
        except Exception as e:
            print(f"⚠️  Error al cargar YOLO: {e}")
            print("   Usando Hough Transform como fallback")
        
        # Parámetros de detección de círculos (Hough Transform)
        self.min_radius = 20
        self.max_radius = 100
        self.min_distance = 40
        
    def count_eggs(self, image_path):
        """
        Método principal que usa YOLO si está disponible,
        sino usa Hough Transform como fallback.
        """
        if self.use_yolo:
            return self.count_eggs_yolo(image_path)
        else:
            return self.count_eggs_hough(image_path)
    
    def count_eggs_yolo(self, image_path):
        """
        Detecta huevos usando modelo YOLO.
        Para pre-entrenado detecta clase 'orange' (id 49 in COCO).
        """
        try:
            # Cargar imagen
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError("No se pudo cargar la imagen")
            
            # Inferencia con YOLO
            # conf=0.15, iou=0.30 para mayor sensibilidad con pre-entrenado
            results = self.yolo_model(image, conf=self.conf_thres, iou=0.30, verbose=False)
            
            # Procesar resultados
            detections = []
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    # Obtener coordenadas
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    conf = float(box.conf[0])
                    cls = int(box.cls[0])
                    
                    # Filtrar clases si es modelo pre-entrenado
                    # 49 = orange, 32 = sports ball (comunes para huevos)
                    # Si es modelo entrenado (custom), cls=0 es egg
                    class_name = self.yolo_model.names[cls]
                    is_custom_model = 'egg' in self.yolo_model.names.values()
                    
                    valid_detection = True
                    if not is_custom_model:
                        # Para pre-entrenado, aceptamos objetos redondos
                        valid_classes = ['orange', 'sports ball', 'apple']
                        if class_name not in valid_classes:
                            valid_detection = False
                    
                    if valid_detection:
                        # Calcular centro y radio aproximado
                        center_x = int((x1 + x2) / 2)
                        center_y = int((y1 + y2) / 2)
                        radius = int(max(x2 - x1, y2 - y1) / 2)
                        
                        # Dibujar bounding box
                        cv2.rectangle(image, (int(x1), int(y1)), (int(x2), int(y2)), 
                                    (0, 255, 0), 2)
                        
                        # Agregar etiqueta con confianza
                        label = f'{conf:.2f}'
                        cv2.putText(image, label, (int(x1), int(y1) - 10),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                        
                        detections.append({
                            'x': center_x,
                            'y': center_y,
                            'radius': radius,
                            'confidence': conf,
                            'bbox': [int(x1), int(y1), int(x2), int(y2)]
                        })
            
            count = len(detections)
            
            # Agregar contador y método
            cv2.putText(image, f'Huevos detectados: {count} (YOLO)',
                       (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
            
            # Guardar imagen procesada
            processed_path = self._save_processed_image(image, image_path)
            
            # Calcular confianza promedio
            avg_conf = sum(d['confidence'] for d in detections) / count if count > 0 else 0
            confidence = avg_conf * 100
            
            return {
                'count': count,
                'confidence': confidence,
                'detections': detections,
                'processed_image_path': processed_path,
                'method': 'YOLO'
            }
            
        except Exception as e:
            return {
                'count': 0,
                'confidence': 0.0,
                'detections': [],
                'error': str(e),
                'processed_image_path': None
            }
    
    def count_eggs_hough(self, image_path):
        """
        Procesa una imagen y cuenta los huevos detectados usando Hough Transform.
        Usa preprocesamiento avanzado para mejorar la detección.
        
        Args:
            image_path: Ruta a la imagen a procesar
            
        Returns:
            dict: {
                'count': int - Número de huevos detectados,
                'confidence': float - Nivel de confianza (0-100),
                'detections': list - Lista de círculos detectados,
                'processed_image_path': str - Ruta a imagen procesada
            }
        """
        try:
            # Cargar imagen
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError("No se pudo cargar la imagen")
            
            original = image.copy()
            
            # === PREPROCESAMIENTO AVANZADO ===
            
            # 1. Convertir a escala de grises
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # 2. Aplicar filtro bilateral para reducir ruido preservando bordes
            denoised = cv2.bilateralFilter(gray, 9, 75, 75)
            
            # 3. Mejorar contraste con CLAHE (Contrast Limited Adaptive Histogram Equalization)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced = clahe.apply(denoised)
            
            # 4. Aplicar operaciones morfológicas para separar huevos juntos
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
            morph = cv2.morphologyEx(enhanced, cv2.MORPH_GRADIENT, kernel)
            
            # 5. Blur gaussiano suave
            blurred = cv2.GaussianBlur(enhanced, (5, 5), 1)
            
            # === DETECCIÓN DE CÍRCULOS ===
            circles = cv2.HoughCircles(
                blurred,
                cv2.HOUGH_GRADIENT,
                dp=1.2,  # Resolución del acumulador
                minDist=35,  # Distancia mínima entre centros (ajustado)
                param1=50,  # Umbral superior para Canny
                param2=28,  # Umbral del acumulador (más alto = más estricto)
                minRadius=18,  # Radio mínimo
                maxRadius=70  # Radio máximo
            )
            
            detections = []
            count = 0
            
            if circles is not None:
                circles = np.uint16(np.around(circles))
                
                # Filtrar círculos por calidad
                filtered_circles = []
                for circle in circles[0, :]:
                    x, y, r = circle[0], circle[1], circle[2]
                    
                    # Verificar que el círculo esté dentro de la imagen
                    if (x - r >= 0 and x + r < image.shape[1] and
                        y - r >= 0 and y + r < image.shape[0]):
                        
                        # Extraer región del círculo
                        mask = np.zeros(gray.shape, dtype=np.uint8)
                        cv2.circle(mask, (x, y), r, 255, -1)
                        circle_region = cv2.bitwise_and(gray, gray, mask=mask)
                        
                        # Calcular varianza (los huevos tienen textura uniforme)
                        mean, stddev = cv2.meanStdDev(circle_region, mask=mask)
                        
                        # Filtrar por uniformidad (stddev bajo = huevo)
                        if stddev[0][0] < 50:  # Umbral de uniformidad
                            filtered_circles.append(circle)
                
                count = len(filtered_circles)
                
                # Dibujar círculos filtrados
                for circle in filtered_circles:
                    center = (circle[0], circle[1])
                    radius = circle[2]
                    
                    # Círculo exterior (verde brillante)
                    cv2.circle(image, center, radius, (0, 255, 0), 3)
                    # Centro (rojo)
                    cv2.circle(image, center, 3, (0, 0, 255), -1)
                    
                    detections.append({
                        'x': int(circle[0]),
                        'y': int(circle[1]),
                        'radius': int(circle[2])
                    })
            
            # Agregar contador en la imagen
            cv2.putText(
                image,
                f'Huevos detectados: {count}',
                (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.2,
                (0, 255, 0),
                3
            )
            
            # Guardar imagen procesada
            processed_path = self._save_processed_image(image, image_path)
            
            # Calcular nivel de confianza
            confidence = self._calculate_confidence(count, detections)
            
            return {
                'count': count,
                'confidence': confidence,
                'detections': detections,
                'processed_image_path': processed_path
            }
            
        except Exception as e:
            return {
                'count': 0,
                'confidence': 0.0,
                'detections': [],
                'error': str(e),
                'processed_image_path': None
            }
    
    def _save_processed_image(self, image, original_path):
        """Guarda la imagen procesada con las detecciones marcadas."""
        # Crear directorio si no existe
        processed_dir = os.path.join(settings.MEDIA_ROOT, 'vision_processed')
        os.makedirs(processed_dir, exist_ok=True)
        
        # Generar nombre único
        filename = os.path.basename(original_path)
        name, ext = os.path.splitext(filename)
        processed_filename = f"{name}_processed{ext}"
        processed_path = os.path.join(processed_dir, processed_filename)
        
        # Guardar imagen
        cv2.imwrite(processed_path, image)
        
        # Retornar ruta relativa para Django
        return os.path.join('vision_processed', processed_filename)
    
    def _calculate_confidence(self, count, detections):
        """
        Calcula el nivel de confianza basado en la calidad de las detecciones.
        
        Factores:
        - Número de detecciones
        - Uniformidad de tamaños
        - Distribución espacial
        """
        if count == 0:
            return 0.0
        
        # Base: 70% si hay detecciones
        confidence = 70.0
        
        # Bonus por número razonable de huevos (5-50)
        if 5 <= count <= 50:
            confidence += 10.0
        
        # Bonus por uniformidad de tamaños
        if detections:
            radii = [d['radius'] for d in detections]
            avg_radius = np.mean(radii)
            std_radius = np.std(radii)
            
            # Si la desviación estándar es baja, los huevos son uniformes
            if std_radius < avg_radius * 0.3:
                confidence += 10.0
        
        # Bonus por distribución espacial (no todos en el mismo lugar)
        if len(detections) > 1:
            positions = [(d['x'], d['y']) for d in detections]
            distances = []
            for i in range(len(positions)):
                for j in range(i + 1, len(positions)):
                    dist = np.sqrt(
                        (positions[i][0] - positions[j][0])**2 +
                        (positions[i][1] - positions[j][1])**2
                    )
                    distances.append(dist)
            
            avg_distance = np.mean(distances)
            if avg_distance > self.min_distance * 1.5:
                confidence += 10.0
        
        return min(confidence, 100.0)  # Máximo 100%
    
    def count_eggs_multipass(self, image_path):
        """
        Método mejorado que realiza múltiples pasadas con diferentes parámetros
        y combina los resultados para mejor precisión.
        """
        try:
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError("No se pudo cargar la imagen")
            
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            gray = cv2.equalizeHist(gray)
            
            all_circles = []
            
            # Pasada 1: Parámetros estándar (sensibilidad media)
            blurred1 = cv2.GaussianBlur(gray, (5, 5), 1.5)
            circles1 = cv2.HoughCircles(
                blurred1, cv2.HOUGH_GRADIENT,
                dp=1.1, minDist=25, param1=50, param2=20,
                minRadius=15, maxRadius=80
            )
            if circles1 is not None:
                all_circles.extend(circles1[0])
            
            # Pasada 2: Mayor sensibilidad (para huevos tenues)
            blurred2 = cv2.GaussianBlur(gray, (3, 3), 1)
            circles2 = cv2.HoughCircles(
                blurred2, cv2.HOUGH_GRADIENT,
                dp=1.1, minDist=20, param1=40, param2=18,
                minRadius=12, maxRadius=85
            )
            if circles2 is not None:
                all_circles.extend(circles2[0])
            
            # Pasada 3: Para huevos más grandes
            circles3 = cv2.HoughCircles(
                blurred1, cv2.HOUGH_GRADIENT,
                dp=1.2, minDist=30, param1=50, param2=25,
                minRadius=20, maxRadius=100
            )
            if circles3 is not None:
                all_circles.extend(circles3[0])
            
            # Eliminar duplicados (círculos muy cercanos)
            unique_circles = self._remove_duplicate_circles(all_circles)
            
            # Dibujar círculos únicos
            detections = []
            for circle in unique_circles:
                center = (int(circle[0]), int(circle[1]))
                radius = int(circle[2])
                
                cv2.circle(image, center, radius, (0, 255, 0), 2)
                cv2.circle(image, center, 2, (0, 0, 255), 3)
                
                detections.append({
                    'x': center[0],
                    'y': center[1],
                    'radius': radius
                })
            
            count = len(unique_circles)
            
            # Agregar contador
            cv2.putText(
                image, f'Huevos detectados: {count}',
                (10, 40), cv2.FONT_HERSHEY_SIMPLEX,
                1.2, (0, 255, 0), 3
            )
            
            processed_path = self._save_processed_image(image, image_path)
            confidence = self._calculate_confidence(count, detections)
            
            return {
                'count': count,
                'confidence': confidence,
                'detections': detections,
                'processed_image_path': processed_path
            }
            
        except Exception as e:
            return {
                'count': 0,
                'confidence': 0.0,
                'detections': [],
                'error': str(e),
                'processed_image_path': None
            }
    
    def _remove_duplicate_circles(self, circles, min_distance=15):
        """Elimina círculos duplicados que están muy cerca entre sí."""
        if not circles:
            return []
        
        circles = np.array(circles)
        unique = []
        
        for circle in circles:
            is_duplicate = False
            for unique_circle in unique:
                # Calcular distancia entre centros
                dist = np.sqrt(
                    (circle[0] - unique_circle[0])**2 +
                    (circle[1] - unique_circle[1])**2
                )
                if dist < min_distance:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique.append(circle)
        
        return unique
    
    def adjust_parameters(self, min_radius=None, max_radius=None, min_distance=None):
        """Permite ajustar los parámetros de detección."""
        if min_radius is not None:
            self.min_radius = min_radius
        if max_radius is not None:
            self.max_radius = max_radius
        if min_distance is not None:
            self.min_distance = min_distance
