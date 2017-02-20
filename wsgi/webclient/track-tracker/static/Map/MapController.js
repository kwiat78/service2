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

//	        $scope.track = {"center":[$scope.map_[$scope.streets[0]][0][2], $scope.map_[$scope.streets[0]][0][1]]}
	        $scope.track = {"center":[$scope.map_[0][0]['latitude'], $scope.map_[0][0]['longitude']]}
	        $scope.map.setCenter({lat:$scope.track.center[0], lng:$scope.track.center[1]});


//	        for(j in $scope.streets)
//	        {
//                $scope.track.points = []
//                dj = $scope.streets[j]
//                console.log(dj)
//                for(var i=0;i<$scope.map_[dj].length;i++) {
//                    $scope.track.points.push(new google.maps.LatLng($scope.map_[dj][i][2], $scope.map_[dj][i][1]));
//                }
//
////                if($scope.poly){
////                    $scope.poly.setMap(null);
////
////                } else {
////
////                }
//
//                $scope.poly = new google.maps.Polyline({
//                    path: $scope.track.points,
//                    geodesic: true,
//                    strokeColor: Colors.next_color(),
//                    strokeOpacity: 1.0,
//                    strokeWeight: 2,
//                });
//                console.log($scope.map)
//               $scope.poly.setMap($scope.map);
//            }
  for(j in $scope.map_)
	        {
	        console.log("*",$scope.map_[j])
                $scope.track.points = []
//                dj = $scope.streets[j]
//                console.log(dj)
                for(var i=0;i<2;i++) {
                    $scope.track.points.push(new google.maps.LatLng($scope.map_[j][i]['latitude'], $scope.map_[j][i]['longitude']));
                }

//                if($scope.poly){
//                    $scope.poly.setMap(null);
//
//                } else {
//
//                }

                $scope.poly = new google.maps.Polyline({
                    path: $scope.track.points,
                    geodesic: true,
                    strokeColor: Colors.next_color(),
                    strokeOpacity: 1.0,
                    strokeWeight: 2,
                });
                console.log($scope.map)
               $scope.poly.setMap($scope.map);
            }





    }

//    FeedReader.getTracks().then(function(f) {
//        $scope.tracks = f
//    }, function() {
//        $scope.error = true
//    })

    FeedReader.getMap().then(function(f) {
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
