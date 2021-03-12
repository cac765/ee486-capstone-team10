import picamera
import picamera.array

class CameraStream:
    """Camera object to control the image stream from the PiCamera."""
    def __init__( self, width, height ):
        # Initialize the PiCamera
        self.width = int( width )
        self.height = int( height )
        self.camera = picamera.PiCamera()
        self.camera.resolution = (width, height)
        self.stream = picamera.array.PiRGBArray( self.camera )

    def read( self ):
        # Read a frame from the camera
        self.camera.capture( self.stream, format='bgr' )
        return self.stream.array

    def clear( self ):
        # Truncate the output stream to be ready for another read
        self.stream.truncate(0)

    def stop( self ):
        # Finalize the state of the camera and release the camera resources
        self.camera.close()
