import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt
import requests
import json

# Télécharger les images de la base de donnée
#   Les classer dans 6 dossiers différents selon leur clase
# Charger l'image source
#   Crop et redimensionner
# Charger chaque image d'un dossier classe particulier
#   En extraire les template_xp et template_image
#       Templatematch template_image et l'image source redimensionnée TODOLE faire sur une ROI
#           Si la valeur > thres, on fait un templatematch avec templatematch avec template_xp
#               Si ok, on extrait le code de l'image
resolution = [569,400]
xp_region =[[6,3],[54,48]]
class_color_region = [[52,6], [58,11]]
image_roi =[[60, 60], [285, 268]]
image_roi2 = [[115, 25], [275, 38]]
image_roi3 = [[0,100],[400, 400]]
path = r"D:\Louis-Nicolas\projet\arkham_sorter\img\02111.png"

path_src = r"D:\Louis-Nicolas\projet\arkham_sorter\img\global.png"

def dl_collection_img():
    #open collection
    with open('collection.json') as collection_handler :
        collection = json.load(collection_handler)
    
    for xp in range(2) :
        for classe in range(6):
            for card in collection[xp][classe]:
                if card is None :
                    continue
                
                img_url = f"https://fr.arkhamdb.com{card.get('imagesrc')}"
                img_data = requests.get(img_url).content
                with open(f"img/{xp}/{classe}/{card.get('code')}.png", 'wb') as handler:
                    handler.write(img_data)

def image_source():
    roi_camera = [[204,1926],[1491,3667]] 
    img_src = cv.imread(path_src,cv.IMREAD_GRAYSCALE)
    return img_src[roi_camera[0][1] : roi_camera[1][1], roi_camera[0][0] : roi_camera[1][0]]


def roi_template(card, roi):
    return card[ roi[0][1]:roi[1][1], roi[0][0]:roi[1][0]]
    
    
def seach_card(collection, THRE =0.9 ):
    path = r"D:\Louis-Nicolas\projet\arkham_sorter\img"
    #img_src = image_source()
    n=0
    i = 0 
    best = 1000
    best_code =0
    #card_src = card_src[0:300, 0:300]
    for xp in range(2):
        for classe in range(6):
            for card in collection[xp][classe]:
                if card is None :
                    continue
                n = n+1
                card_code = card.get("code")    
                card_img = cv.imread(f"{path}\{xp}\{classe}\{card_code}.png", cv.IMREAD_GRAYSCALE)
                
                card_src = image_source()
                img_ratio = card_img.shape[1]/card_src.shape[1]
                card_src = cv.resize(card_src, None, fx= img_ratio, fy= img_ratio)                
                    
                card_template = roi_template(card_img, image_roi3)
                res = cv.matchTemplate(card_src, card_template, cv.TM_SQDIFF_NORMED)
                min_val, max_val, min_loc, max_loc =cv.minMaxLoc(res)
                if min_val < best:
                    if card_code == '02111':
                        a=0
                    # if max_val > best:
                    #     best = max_val
                    #     best_code = card_code
                    #     plt.imshow(card_img)          
                    if min_val < 0.16:
                        i = i +1
                    best = min_val
                    best_code = card_code
                    print(f"{i} eme match sur {n}")
                    #breakpoint()
    
    remove = 0
            
                         
           
#image source from camera
def test_opencv():    
    img_src = cv.imread(path_src,cv.IMREAD_GRAYSCALE)
    cv.imshow("Ouais", img_src)
    cv.waitKey()
    plt.subplot(2,2,1)
    plt.imshow(img_src,cmap = plt.cm.gray)
    plt.title("Image source")
    roi_camera = [[204,1926],[1491,3667]] 
    img_src_croped = img_src[roi_camera[0][1] : roi_camera[1][1], roi_camera[0][0] : roi_camera[1][0]]
    plt.subplot(2,2,2)
    plt.imshow(img_src_croped, cmap = plt.cm.gray)
    plt.title("Image croped")

    #resize
    img_ratio = resolution[1]/img_src_croped.shape[0]
    img_resize = cv.resize(img_src_croped, None, fx= img_ratio, fy= img_ratio)
    plt.subplot(2,2,3)
    plt.title("Image resized")
    plt.imshow(img_resize, cmap = plt.cm.gray)
    # Reading an image in default mode 
    image = cv.imread(path, cv.IMREAD_GRAYSCALE) 
    
    # Window name in which image is displayed 
    window_name = 'Image'
    
    # Start coordinate, here (5, 5) 
    # represents the top left corner of rectangle 
    start_point = xp_region[0]
    
    # Ending coordinate, here (220, 220) 
    # represents the bottom right corner of rectangle 
    end_point = xp_region[1] 
    
    # Blue color in BGR 
    color = (0, 0, 255) 
    
    # Line thickness of 2 px 
    thickness = 1
    
    # Using cv2.rectangle() method 
    # Draw a rectangle with blue line borders of thickness of 2 px 

    template = image[start_point[1]:end_point[1], start_point[0]:end_point[0]]
    h,w = template.shape

    res = cv.matchTemplate(img_resize,template, cv.TM_CCORR_NORMED)
    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)

    top_left = max_loc
    bottom_right = (top_left[0] + w, top_left[1] + h)
    cv.rectangle(img_resize, top_left, bottom_right, 255, 2)

    plt.subplot(2,2,4)
    plt.imshow(img_resize, cmap= plt.cm.gray)
    plt.show()
    cv.imshow(window_name, template) 
    cv.waitKey()

    image = cv.rectangle(image, start_point, end_point, color, thickness) 
    cv.rectangle(image, image_roi[0], image_roi[1], color, thickness  )
    cv.rectangle(image, class_color_region[0], class_color_region[1], color, thickness  )  
    
    # Displaying the image  
    cv.imshow(window_name, image) 
    cv.waitKey() 

def main() :
    #dl_collection_img()
    with open('collection.json') as collection_handler :
        collection = json.load(collection_handler)
    
    seach_card(collection= collection)
    ouai = 0
    
    
if __name__ == "__main__" :
    main()