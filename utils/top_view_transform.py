import cv2
import numpy as np

def displayImage( img, img_name="", title="image",
                  resize=True, fromFile=False ):
    """Display cv2 image and wait for keypress."""
    # Check to display image from file instead of using img parameter
    if fromFile:
        img = cv2.imread( img_name )
        # Check for incorrect filename of image
        if img is None:
            raise Exception( "[-] Invalid filename for image display." )
        
    # Check if image is to be resizable, create resizable window
    if resize:
        cv2.namedWindow( title, cv2.WINDOW_NORMAL )
    cv2.imshow( title, img )
    # Wait for keypress to continue
    cv2.waitKey(0)

def getGroundTruthLocations( top_L: tuple, top_R: tuple,
                            bot_L: tuple, bot_R: tuple ) -> np.ndarray:
    """Builds Ground Truth Bounding Box from locations."""
    # Pack tuples of bounding box into numpy array with dtype float-32
    return np.float32([ top_L, top_R, bot_L, bot_R ])

def getLocation( min_point: tuple, max_point: tuple ) -> tuple:
    """Gets the bottom center location from the bounding box of an occupant."""
    # Unpack the tuples into min/max values
    xmin, ymin = min_point
    xmax, ymax = max_point
    # Take midpoint of x-coordinate and ymax for bottom middle of box
    x_result = ( xmin + xmax ) // 2
    y_result = ymax
    # Return location
    return ( x_result, y_result )

def getTopViewTransform( img: np.ndarray,
                         trans_matrix: np.ndarray ) -> np.ndarray:
    """Conduct top view transform on an image given the transform matrix."""
    # Get width and height dimensions of original image
    shape = img.shape[:-1]
    return cv2.warpPerspective( img, trans_matrix, shape )

def getTransformMatrix( source_points: np.ndarray,
                        dest_points: np.ndarray ) -> np.ndarray:
    """Calculates transform matrix from ground truth source/dest boxes."""
    return cv2.getPerspectiveTransform( source_points, dest_points )

def plotGroundTruthLocations( img: np.ndarray, points: np.ndarray,
                              size=10, color="red" ):
    """Plots the Ground Truth Locations on an image."""
    # Define color options
    colors = { "black"  : (0,0,0),
               'k'      : (0,0,0),
               "red"    : (0,0,255),
               'r'      : (0,0,255),
               "green"  : (0,255,0),
               'g'      : (0,255,0),
               "yellow" : (0,255,255),
               'y'      : (0,255,255),
               "blue"   : (255,0,0),
               'b'      : (255,0,0),
               "purple" : (255,0,255),
               'p'      : (255,0,255),
               "cyan"   : (255,255,0),
               'c'      : (255,255,0),
               "white"  : (255,255,255),
               'w'      : (255,255,255) }
    # Copy input image
    img_copy = img.copy()
    # Check user input matches color key
    if color not in colors:
        raise Exception( "[-] Invalid argument for color parameter." )
    # Iterate through each point of ground truth locations and plot circle
    for point in points:
        int_point = list( np.array( point, dtype=int ) )
        img_copy = cv2.circle( img_copy, tuple(int_point),
                               size, colors[color], -1 )
    # Return the image copy
    return img_copy

def transformCentroidLocation( src: tuple, mat: np.ndarray ) -> tuple:
    """Perform a top view transform on a single location."""
    xterm, yterm = src
    new_x = ( mat[0][0] * xterm + mat[0][1] * yterm + mat[0][2] ) // \
            ( mat[2][0] * xterm + mat[2][1] * yterm + mat[2][2] )
    new_y = ( mat[1][0] * xterm + mat[1][1] * yterm + mat[1][2] ) // \
            ( mat[2][0] * xterm + mat[2][1] * yterm + mat[2][2] )
    return new_x, new_y

