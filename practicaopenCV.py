import cv2
from collections import deque
import math
import os


def get_centroid(x, y, w, h):
    return (x + w // 2, y + h // 2)

def distance_between_points(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


script_dir = os.path.dirname(os.path.abspath(__file__))

video_filename = "trafico01.mp4"

video_path = os.path.join(script_dir, video_filename)

print(f"Intentando abrir: {video_path}")
cap = cv2.VideoCapture(video_path)
bg_subtractor = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=25)

object_paths = {}
car_count = 0
next_car_id = 1
line_y = 600  
min_contour_area = 1500  

# Conjunto para mantener coches que han cruzado la línea
crossed_line_cars = set()

# Distancia mínima entre centroides para separarlos
min_centroid_distance = 80  


line_y2 = 600
car_count2 = 0
crossed_line_cars2 = set()

#473  478  517
line_y3 = 478
car_count3 = 0
crossed_line_cars3 = set()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Ha ocurrido un error al leer el vídeo o se ha acabado la transmisión.")
        break

    frame = cv2.resize(frame, (1280, 720))
    roi = frame[230:820, 0:1280]  
    line_y_in_roi = line_y - 230  
    line_y_in_roi2 = line_y2 - 230  
    line_y_in_roi3 = line_y3 - 230


    mask = bg_subtractor.apply(roi)
    _, mask = cv2.threshold(mask, 254, 255, cv2.THRESH_BINARY)
    mask = cv2.medianBlur(mask, 5)

    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    detections = []
    for contour in contours:
        if cv2.contourArea(contour) > min_contour_area:  
            x, y, w, h = cv2.boundingRect(contour)
            detections.append((x, y, w, h))

    # Dibuja la línea de conteo en el ROI
    cv2.line(roi, (0+680, line_y_in_roi), (950, line_y_in_roi), (0, 255, 0), 2)
    cv2.line(roi, (0+200, line_y_in_roi2), (600, line_y_in_roi2), (255, 0, 0), 2)
    cv2.line(roi, (0+860, line_y_in_roi3), (1260, line_y_in_roi3), (0, 255, 255), 2) 

    cv2.line(roi, (0+850, line_y_in_roi), (868, line_y_in_roi), (255, 0, 255), 2)
    cv2.line(roi, (0+929, line_y_in_roi3), (935, line_y_in_roi3), (255, 255, 0), 2)   

    updated_paths = {}
    for (x, y, w, h) in detections:
        centroid = get_centroid(x, y, w, h)
        found = False

        for car_id, path in object_paths.items():
            last_centroid = path[-1]
            dist = distance_between_points(centroid, last_centroid)

            if dist < min_centroid_distance: 
                found = True
                path.append(centroid)
                updated_paths[car_id] = path

                if len(path) >= 2:
                    prev_x, prev_y = path[-2]  # Coordenadas previas
                    curr_x, curr_y = path[-1]  # Coordenadas actuales

                   
                    if (prev_y < line_y_in_roi <= curr_y and
                        680 <= curr_x <= 950 and  
                        car_id not in crossed_line_cars):
                        print(f"Coche cruzó hacia abajo dentro del segmento verde: ID={car_id}")
                        
                        if (prev_y < line_y_in_roi <= curr_y and
                            850 <= curr_x <= 868 and  
                            car_id not in crossed_line_cars):
                        
                            car_count += 2
                            crossed_line_cars.add(car_id)  
                        else:
                            car_count += 1
                            crossed_line_cars.add(car_id) 

                    if (prev_y < line_y_in_roi2 <= curr_y and
                        200 <= curr_x <= 600 and 
                        car_id not in crossed_line_cars2):
                        print(f"Coche cruzó hacia abajo dentro del segmento azúl: ID={car_id}")
                        car_count2 += 1
                        crossed_line_cars2.add(car_id)  

                    if (prev_y > line_y_in_roi3 >= curr_y and
                        860 <= curr_x <= 1260 and  
                        car_id not in crossed_line_cars3):
                        print(f"Coche cruzó hacia abajo dentro del segmento amarillo: ID={car_id}")

                        if (prev_y > line_y_in_roi3 >= curr_y and
                        929 <= curr_x <= 935 and  
                        car_id not in crossed_line_cars3):
                            car_count3 += 2
                            crossed_line_cars3.add(car_id)
                        
                        else:
                            car_count3 += 1
                            crossed_line_cars3.add(car_id)

                break
        
        if not found:
            updated_paths[next_car_id] = deque([centroid], maxlen=10)
            next_car_id += 1

        cv2.rectangle(roi, (x, y), (x + w, y + h), (255, 0, 0), 2)
        cv2.circle(roi, centroid, 4, (0, 0, 255), -1)

    object_paths = updated_paths

    cv2.putText(frame, f"Conteo coches: {car_count}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(frame, f"Conteo coches: {car_count2}", (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
    cv2.putText(frame, f"Conteo coches: {car_count3}", (50, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

    cv2.imshow("Carretera", frame)

    if cv2.waitKey(10) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()