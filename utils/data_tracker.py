
class DataTracker:

    def __init__( self ):
        self.data_points = []
        self.mode = None

    def add_point( self, point: int ):
        self.data_points.append( point )

    def clear_data( self ):
        self.__init__()

    def get_mode( self ) -> int:
        self._update_mode()
        return self.mode

    def _update_mode( self ):
        mode: int = 0
        index: int = 0
        occurrence: int = 0
        mode_list: list = []
        occurrence_list: list = []
        occurrence_dict: dict = {}

        self.data_points.sort()

        while ( index < len( self.data_points ) ):
            occurrence = self.data_points.count( self.data_points[ index ] )
            occurrence_list.append( occurrence )
            index += 1

        occurrence_dict = dict( zip( self.data_points, occurrence_list ) )

        for ( mode, occurrence ) in occurrence_dict.items():
            if occurrence == max( occurrence_list ):
                 mode_list.append( mode )

        if len( mode_list ) > 0:
            mode = max( mode_list )
        else:
            mode = 0

        self.mode = mode


