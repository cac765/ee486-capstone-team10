import cv2
import numpy as np

def getCentroid( min_point: tuple, max_point: tuple ) -> tuple:
    xmin, ymin = min_point
    xmax, ymax = max_point
    x_result = ( xmin + xmax ) // 2
    y_result = ( ymin + ymax ) // 2
    return ( x_result, y_result )

def topViewTransform( img: np.array, pts1: list, pts2: list,
                      output_shape: tuple ) -> np.array:
    shape = img.shape[:-1]
    matrix = cv2.getPerspectiveTransform( pts1, pts2 )
    img_transform = cv2.warpPerspective( img, matrix, shape )
    return img_transform

def displayImage( img: np.array, title: str, resizable = True ):
    if resizable:
        cv2.namedWindow( title, cv2.WINDOW_NORMAL )
    cv2.imshow( title, img )
    cv2.waitKey(0)

img = cv2.imread('t1.jpg')
dimensions = img.shape
print( dimensions )

img = cv2.circle(img, (683,760), 10, (0,0,255), -1)
img = cv2.circle(img, (1150,275), 10, (0,0,255), -1)
img = cv2.circle(img, (250,350), 10, (0,0,255), -1)
img = cv2.circle(img, (650,200), 10, (0,0,255), -1)

img = cv2.circle(img, (10,10), 10, (0,255,255), -1)
img = cv2.circle(img, (1356,10), 10, (0,255,255), -1)
img = cv2.circle(img, (10,758), 10, (0,255,255), -1)
img = cv2.circle(img, (1356,758), 10, (0,255,255), -1)

img = cv2.rectangle(img, (561,310), (884,606), (0,0,255), 1)
centroid_loc = getCentroid((561,310), (884,606))
img = cv2.circle(img, centroid_loc, 10, (255,0,255), -1)

pts1 = np.float32([[250,350],[650,200],[683,760],[1150,275]])
pts2 = np.float32([[10,10],[1356,10],[10,758],[1356,758]])

matrix = cv2.getPerspectiveTransform(pts1,pts2)

img_transform = cv2.warpPerspective(img, matrix, (1366,768))

plot = np.zeros((768,1366,3), np.uint8)
plot += 255
plot = cv2.circle(plot, centroid_loc, 10, (255,0,255), -1)
plot_transform = cv2.warpPerspective(plot, matrix, (1366,768))

cv2.namedWindow('test', cv2.WINDOW_NORMAL)
cv2.imshow('test', img)
cv2.namedWindow('transform', cv2.WINDOW_NORMAL)
cv2.imshow('transform', img_transform)
cv2.namedWindow('plot_transform', cv2.WINDOW_NORMAL)
cv2.imshow('plot_transform', plot_transform)
cv2.waitKey(0)
cv2.destroyAllWindows()

###############################################################################
###############################################################################

img2 = cv2.imread( 't2.jpg' )
img2_dimensions = img2.shape[:-1]
output_shape = img2_dimensions
print( img2_dimensions )

img2 = cv2.circle(img2, (550,420), 10, (0,0,255), -1)
img2 = cv2.circle(img2, (695,490), 10, (0,0,255), -1)
img2 = cv2.circle(img2, (550,545), 10, (0,0,255), -1)
img2 = cv2.circle(img2, (365,510), 10, (0,0,255), -1)

img2 = cv2.circle(img2, (1255,10), 10, (0,255,255), -1)
img2 = cv2.circle(img2, (1255,190), 10, (0,255,255), -1)
img2 = cv2.circle(img2, (1065,190), 10, (0,255,255), -1)
img2 = cv2.circle(img2, (1065,10), 10, (0,255,255), -1)

img2 = cv2.rectangle(img2, (706,49),(895,568),(0,0,255),1)
centroid_loc2 = getCentroid((706,49),(895,568))
img2 = cv2.circle(img2, centroid_loc2, 10, (255,0,255), -1)

pts1 = np.float32([[550,420],[695,490],[550,545],[365,510]])
pts2 = np.float32([[1255,10],[1255,190],[1065,190],[1065,10]])

img2_transform = topViewTransform(img2, pts1, pts2, (1266,613))
displayImage(img2,'img2')
displayImage(img2_transform, 'transform2')


