import cv2
import numpy as np

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

def getGroundTruthLocations( top_L: tuple, top_R: tuple,
                            bot_L: tuple, bot_R: tuple ) -> np.ndarray:
    """Builds Ground Truth Bounding Box from locations."""
    # Pack tuples of bounding box into numpy array with dtype float-32
    return np.float32([ top_L, top_R, bot_L, bot_R ])

def getTransformMatrix( source_points: np.ndarray,
                        dest_points: np.ndarray ) -> np.ndarray:
    """Calculates transform matrix from ground truth source/dest boxes."""
    return cv2.getPerspectiveTransform( source_points, dest_points )

def getTopViewTransform( img: np.ndarray,
                         trans_matrix: np.ndarray ) -> np.ndarray:
    """Conduct top view transform on an image given the transform matrix."""
    # Get width and height dimensions of original image
    shape = img.shape[:-1]
    return cv2.warpPerspective( img, trans_matrix, shape )

def transformCentroidLocation( src: tuple, mat: np.ndarray ) -> tuple:
    """Perform a top view transform on a single location."""
    xterm, yterm = src
    new_x = ( mat[0][0] * xterm + mat[0][1] * yterm + mat[0][2] ) // \
            ( mat[2][0] * xterm + mat[2][1] * yterm + mat[2][2] )
    new_y = ( mat[1][0] * xterm + mat[1][1] * yterm + mat[1][2] ) // \
            ( mat[2][0] * xterm + mat[2][1] * yterm + mat[2][2] )
    return new_x, new_y

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
        
def main():
    """Main function to execute."""
    # Load and display original images
    edge2 = cv2.imread( "edge2.jpg" )
    edge5 = cv2.imread( "edge5.jpg" )
    displayImage( edge2, title="edge2" )
    displayImage( edge5, title="edge5" )

    # Define source ground truth bounding boxes
    source_edge2 = getGroundTruthLocations( [1050, 1465], [2805, 1485],
                                            [595,  2460], [3270, 2130] )
    source_edge5 = getGroundTruthLocations( [845,  1370], [2785, 1600],
                                            [100,  2420], [3230, 2425] )

    # Define destination ground truth bounding box
    dest_edge2 = getGroundTruthLocations( [900,   150], [2560,  150],
                                          [1300, 1700], [2560, 1385] )
    dest_edge5 = getGroundTruthLocations( [25,    200], [1500,  630],
                                          [25,   1920], [1500, 1820] )

    # Plot and display source/destination ground truth bounding box
    edge2 = plotGroundTruthLocations( edge2, source_edge2, size=25, color='c' )
    edge2 = plotGroundTruthLocations( edge2, dest_edge2, size=25, color='y' )
    edge5 = plotGroundTruthLocations( edge5, source_edge5, size=25, color='c' )
    edge5 = plotGroundTruthLocations( edge5, dest_edge5, size=25, color='y' )
    displayImage( edge2, title="edge2" )
    displayImage( edge5, title="edge5" )

    # Plot and display sample occupant locations
    locA_2 = getLocation( [545, 1325], [881, 2213] )
    locB = getLocation( [2725, 817], [3113, 2017] )
    locX_2 = ( 1545, 1621 )
    locY_2 = ( 157, 2297 )
    locZ_2 = ( 730, 1600 )
    edge2 = plotGroundTruthLocations( edge2, [locA_2,locB,locX_2,locZ_2,locY_2],
                                      size=25, color='r' )
    locC = getLocation( [250, 865], [737, 2265] )
    locA_5 = getLocation( [2441, 925], [2817, 2033] )
    locX_5 = ( 2773, 1565 )
    locY_5 = ( 2090, 2105 )
    locZ_5 = ( 1890, 1525 )
    edge5 = plotGroundTruthLocations( edge5, [locC,locA_5,locX_5,locZ_5,locY_5],
                                      size=25, color='r' )
    displayImage( edge2, title="edge2" )
    displayImage( edge5, title="edge5" )

    # Get perspective transform matrix
    matrix_edge2 = getTransformMatrix( source_edge2, dest_edge2 )
    matrix_edge5 = getTransformMatrix( source_edge5, dest_edge5 )

    # Perform top view transformation
    edge2_topview = getTopViewTransform( edge2, matrix_edge2 )
    edge5_topview = getTopViewTransform( edge5, matrix_edge5 )
    displayImage( edge2_topview, title="edge2 topview" )
    displayImage( edge5_topview, title="edge5 topview" )
    
    # Get transformed location of occupants and plot over images to verify
    new_locB = transformCentroidLocation( locB, matrix_edge2 )
    new_locA_2 = transformCentroidLocation( locA_2, matrix_edge2 )
    new_locX_2 = transformCentroidLocation( locX_2, matrix_edge2 )
    new_locY_2 = transformCentroidLocation( locY_2, matrix_edge2 )
    new_locZ_2 = transformCentroidLocation( locZ_2, matrix_edge2 )
    edge2_topview = plotGroundTruthLocations( edge2_topview,
                                              [new_locA_2, new_locB,
                                               new_locX_2, new_locY_2,
                                               new_locZ_2],
                                              size=25, color='p' )
    new_locC = transformCentroidLocation( locC, matrix_edge5 )
    new_locA_5 = transformCentroidLocation( locA_5, matrix_edge5 )
    new_locX_5 = transformCentroidLocation( locX_5, matrix_edge5 )
    new_locY_5 = transformCentroidLocation( locY_5, matrix_edge5 )
    new_locZ_5 = transformCentroidLocation( locZ_5, matrix_edge5 )
    edge5_topview = plotGroundTruthLocations( edge5_topview,
                                              [new_locC, new_locA_5,
                                               new_locX_5, new_locY_5,
                                               new_locZ_5],
                                              size=25, color='p' )
    displayImage( edge2_topview, title="edge2 topview" )
    displayImage( edge5_topview, title="edge5 topview" )

    print( [new_locA_2, new_locB, new_locX_2, new_locZ_2,
            new_locA_5, new_locC, new_locX_5, new_locZ_5] )

    # Create output plot of centroids
    print( edge5_topview.shape )
    print( edge2_topview.shape )
    plot_shape = edge5_topview.shape
    plot = np.zeros( plot_shape, dtype=np.uint8 )
    plot = plotGroundTruthLocations( plot, [new_locA_2, new_locA_5],
                                     size=25, color='r' )
    plot = plotGroundTruthLocations( plot, [new_locX_2, new_locX_5], size=25,
                                     color='c' )
    plot = plotGroundTruthLocations( plot, [new_locY_2, new_locY_5], size=25,
                                     color='w' )
    plot = plotGroundTruthLocations( plot, [new_locZ_2, new_locZ_5], size=25,
                                     color='g' )
    plot = plotGroundTruthLocations( plot, [new_locB], size=25, color='y' )
    plot = plotGroundTruthLocations( plot, [new_locC], size=25, color='p' )
    displayImage( plot, title="top view plot" )
    
if __name__ == "__main__":
    main()
        
        
