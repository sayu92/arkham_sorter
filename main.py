import cv2 as cv
import matplotlib.pyplot as plt
from img_card_detector import ocr_card_name
from collection_sorter import trouver_position
import easyocr

#TODO TESTER AVEC UNE IMAGE QU ON RESIZE
#TODO est ce qu'on rescale/resize de toute manière le stream video/camera ?
#TODO Eviter les crash si le flux video est perdu
#TODO Problème pour afficher le nom de la carte quand celle ci possède des accents
#TODO Mettre une forme de latence pour afficher le nom de la carte affin d'éviter le "clignotement"
#TODO Prendre en compte
#TODO Enlever les valeurs hardcoded (les résolutions, le placement du texte)

path_ip = "http://192.168.1.108:8080/video"
rel_pos_centroid_namebox1 = [0.525, 0.05624]
rel_pos_centroid_namebox2 = [0.5, 0.6053]
size_ratio_boxname1 = [0.655, 0.077]
size_ratio_boxname2 = [0.8, 0.077]

def update(source : str, ratio : float = 1.4225, reduc : float = 0.8, processing_resolution  : tuple = (569, 400), resize : bool = True, capture_resolution : tuple = (960,540)):
    capture = cv.VideoCapture(source) # TODO Put those 3 lines a setup method
    ret, original_frame = capture.read()
    frame = cv.resize(original_frame,None, fx=0.5,fy=0.5, interpolation=cv.INTER_AREA)
    
    if resize:
        h, w = frame.shape[:2]
        w_new = round(reduc * w)
        h_new = round(ratio * w_new)
    
        centroid = ( h//2, w//2)
        roi_pt1 = [centroid[1] - w_new//2, centroid[0] - h_new//2]
        roi_pt2 = [centroid[1]+ w_new//2, centroid[0]+h_new//2]
        cv.rectangle(frame, roi_pt1, roi_pt2, thickness=5, color=(255,0,0))
        #roi draw n extract
        roi_capture = frame[roi_pt1[1]:roi_pt2[1],roi_pt1[0]:roi_pt2[0]]
        img_ratio = processing_resolution[1]/roi_capture.shape[1]
        roi_capture = cv.resize(roi_capture, None, fx= img_ratio, fy= img_ratio, interpolation=cv.INTER_AREA)
        roi_capture = cv.cvtColor(roi_capture, cv.COLOR_RGB2GRAY)              
    
    else: #TODO this section will led to bug, only valuable for debug purpose, 
        roi_pt1 = [0, 0]
        roi_pt2 = [frame.shape[1]-1, frame.shape[0]-1]
        roi_capture = frame #TODO Pas très efficace de copier un tableau
        roi_capture = cv.cvtColor(roi_capture, cv.COLOR_RGB2GRAY)
        
    #draw the boxname on the frame
    posx_namebox1 = round(rel_pos_centroid_namebox1[0]*roi_capture.shape[1])
    posy_namebox1 = round(rel_pos_centroid_namebox1[1]*roi_capture.shape[0])
    roi_boxname1_centroid = [posx_namebox1, posy_namebox1]
    roi_boxname1_pt1 = [roi_boxname1_centroid[0] - round(size_ratio_boxname1[0]*roi_capture.shape[1])//2, roi_boxname1_centroid[1] - round(size_ratio_boxname1[1]*roi_capture.shape[0])//2]
    roi_boxname1_pt2 = [roi_boxname1_centroid[0] + round(size_ratio_boxname1[0]*roi_capture.shape[1])//2, roi_boxname1_centroid[1] +round(size_ratio_boxname1[1]*roi_capture.shape[0])//2]
    roi_boxname1 = roi_capture[roi_boxname1_pt1[1]: roi_boxname1_pt2[1], roi_boxname1_pt1[0]:roi_boxname1_pt2[0]]
    #roi_boxname1 = cv.cvtColor(roi_boxname1, cv.COLOR_RGB2GRAY) # TODO Changer pour ne pas effectuer une deuxième fois la conversion(Il faut slicer depuis roi_capture)
    
    cv.rectangle(roi_capture,roi_boxname1_pt1, roi_boxname1_pt2, thickness=2, color=255 )
    
    posx_namebox2 = round(rel_pos_centroid_namebox2[0]*roi_capture.shape[1])
    posy_namebox2 = round(rel_pos_centroid_namebox2[1]*roi_capture.shape[0])
    roi_boxname2_centroid = [posx_namebox2, posy_namebox2]
    roi_boxname2_pt1 = [roi_boxname2_centroid[0] - round(size_ratio_boxname2[0]*roi_capture.shape[1])//2, roi_boxname2_centroid[1] - round(size_ratio_boxname2[1]*roi_capture.shape[0])//2]
    roi_boxname2_pt2 = [roi_boxname2_centroid[0] + round(size_ratio_boxname2[0]*roi_capture.shape[1])//2, roi_boxname2_centroid[1] +round(size_ratio_boxname2[1]*roi_capture.shape[0])//2]
    roi_boxname2 = roi_capture[roi_boxname2_pt1[1]: roi_boxname2_pt2[1], roi_boxname2_pt1[0]:roi_boxname2_pt2[0]]
    #roi_boxname2 = cv.cvtColor(roi_boxname2, cv.COLOR_RGB2GRAY) # TODO Changer pour ne pas effectuer une deuxième fois la conversion(Il faut slicer depuis roi_capture)
    
    cv.rectangle(roi_capture,roi_boxname2_pt1, roi_boxname2_pt2, thickness=2, color=255 )
    return frame, roi_boxname1, roi_boxname2

if __name__ == '__main__':
    
    reader =easyocr.Reader(['fr'], gpu=True)
    
    while True:
        frame, boxname1, boxname2 = update(path_ip, reduc=0.8, resize=True)

        for boxname in [boxname1, boxname2]:
            result = ocr_card_name(boxname)

            if len(result) == 1: # Any other answer is a false positive
                position = trouver_position(result[0][1])

                if position is not None:
                    cv.putText(frame, f"Page: {position[0]}, Position: {position[1]}", (300,300))
                    break
        cv.imshow("camera", frame)
        k = cv.waitKey(10) & 0XFF
        
cv.destroyAllWindows()