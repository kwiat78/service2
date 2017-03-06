var app = angular.module("myApp2");
app.controller('MapController', function($scope, $location, FeedReader, Colors, $uibModal) {
    $scope.initialize = function() {
        var mapOptions = {
            center: {lat: 53.04, lng: 18.58},
            zoom: 12
        };
        $scope.map = new google.maps.Map(document.getElementById('map'), mapOptions);

    }

    $scope.initialize()

    $scope.getTrack = function() {
	        $scope.track = {"center":[$scope.map_[0][0]['latitude'], $scope.map_[0][0]['longitude']]}
	        $scope.map.setCenter({lat:$scope.track.center[0], lng:$scope.track.center[1]});
            for (j in $scope.map_) {
                $scope.track.points = []
                for (var i=0;i<$scope.map_[j].length;i++) {
                    $scope.track.points.push(
                        new google.maps.LatLng(
                            $scope.map_[j][i]['latitude'],
                            $scope.map_[j][i]['longitude']
                        )
                    );
                }

                $scope.poly = new google.maps.Polyline({
                    path: $scope.track.points,
                    geodesic: true,
                    strokeColor: Colors.next_color(),
                    strokeOpacity: 1.0,
                    strokeWeight: 2,
                });
               $scope.poly.setMap($scope.map);
            }
    }

    FeedReader.getMap().then(function(f) {
        console.log($scope.map_)
        $scope.map_ = f
        $scope.streets =[]
        for(var x in  $scope.map_){$scope.streets.push(x)}
        console.log(f)
        console.log($scope.streets)
        $scope.getTrack()
    }, function() {
        $scope.error = true
    })

});  
