var app = angular.module("myApp2");
app.controller('TrackListController', function($scope, $location, FeedReader, Colors, $uibModal) {
    $scope.initialize = function() {
        var mapOptions = {
            center: {lat: 53.04, lng: 18.58},
            zoom: 12
        };
        $scope.map = new google.maps.Map(document.getElementById('map'), mapOptions);

    }

    $scope.initialize()
    $scope.countDistance = function() {
        var track = $scope.track.points;
        var s=0;
        var l = google.maps.geometry.spherical.computeLength(track)
        for(var i=0; i<track.length; i++) {
	        s+=google.maps.geometry.spherical.computeDistanceBetween (track[i],track[(i+1)%track.length]);
        }
        $scope.sum = parseFloat(s/1000).toFixed(2);
        $scope.length = parseFloat(l/1000).toFixed(2);

    }

    $scope.deleteTrack = function() {
            FeedReader.deleteTrack($scope.selected).then(function()
            {
                FeedReader.getTracks().then(function(f) {
                $scope.tracks = f
                $scope.selected=""
            })
            })
    }

    $scope.joinTrack = function() {
        $scope.adding = true;
    }

    $scope.cancelAdd = function() {
        $scope.adding = false;

         if($scope.poly){
                $scope.poly.setMap(null);
                }

          if($scope.otherCircles){

                for(var i = 0; i < $scope.otherCircles.length; i++) {
                    $scope.otherCircles[i].setMap(null);
                }
                $scope.otherCircles = []
            } else {
                $scope.otherCircles = []
            }

             $scope.poly = new google.maps.Polyline({
                path: $scope.track.points,
                geodesic: true,
                strokeColor: $scope.poly.strokeColor,
                strokeOpacity: 1.0,
                strokeWeight: 2,
            });

            $scope.poly.setMap($scope.map);



    }

    $scope.joinTracks = function(){
        FeedReader.joinTracks($scope.selected, $scope.other).then(function(d){
            console.log("x")
             FeedReader.getTracks().then(function(f) {
             console.log("y")
             console.log(f)
                    $scope.tracks = f
                    $scope.cancelAdd()
                    $scope.getTrack()
                }, function() {
                $scope.error = true
                })
            })

    }


    $scope.addTrack = function(){
        console.log($scope)
        FeedReader.getTrack($scope.other).then(function(data){
         $scope.otherTrack = {"center":[data[0].latitude, data[0].longitude]}
         $scope.otherTrack.points = []
        for(var i=0;i<data.length;i++) {
            $scope.otherTrack.points.push(new google.maps.LatLng(data[i].latitude, data[i].longitude));
        }

        if($scope.poly){
                $scope.poly.setMap(null);
                }

          if($scope.otherCircles){

                for(var i = 0; i < $scope.otherCircles.length; i++) {
                    $scope.otherCircles[i].setMap(null);
                }
                $scope.otherCircles = []
            } else {
                $scope.otherCircles = []
            }




         for(var i=0; i < $scope.otherTrack.points.length; i++) {
                var point = new google.maps.Circle({
                    map: $scope.map,
                    center: $scope.otherTrack.points[i],
                    radius: 5,
                    strokeColor: "rgb(1,0,0)",
                });
                $scope.otherCircles.push(point);
            }



            $scope.poly = new google.maps.Polyline({
                path: $scope.track.points.concat($scope.otherTrack.points),
                geodesic: true,
                strokeColor: $scope.poly.strokeColor,
                strokeOpacity: 1.0,
                strokeWeight: 2,
            });

            $scope.poly.setMap($scope.map);
        })



    }


    $scope.changeName = function() {
        var modalInstance = $uibModal.open({
            animation: true,
            templateUrl: '../static/TrackList/ChangeLabelView.html',
            controller: 'ChangeLabelController',
            size: 300,
            resolve: {
                label: function () {
                    return $scope.selected;
                }
            }
        });

        modalInstance.result.then(function (new_label) {
            FeedReader.getTracks().then(function(f) {
                $scope.tracks = f
                $scope.selected=new_label
            })
        }, function () {
            console.log('Modal dismissed at: ' + new Date());
        });
    }
    $scope.update_track = null;
    $scope.getTrack = function() {
        FeedReader.getTrack($scope.selected).then(function(data) {
	        $scope.track = {"center":[data[0].latitude, data[0].longitude]}
	        $scope.map.setCenter({lat:$scope.track.center[0], lng:$scope.track.center[1]});

	        $scope.track.points = []
	        for(var i=0;i<data.length;i++) {
		        $scope.track.points.push(new google.maps.LatLng(data[i].latitude, data[i].longitude));
	        }

	        if($scope.poly){
                $scope.poly.setMap(null);
                for(var i = 0; i < $scope.circles.length; i++) {
                    $scope.circles[i].setMap(null);
                }
                $scope.circles = []
            } else {
                $scope.circles = []
            }

            $scope.poly = new google.maps.Polyline({
                path: $scope.track.points,
                geodesic: true,
                strokeColor: Colors.next_color(),
                strokeOpacity: 1.0,
                strokeWeight: 2,
            });
            console.log($scope.map)
            $scope.poly.setMap($scope.map);

            for(var i=0; i < $scope.track.points.length; i++) {
                var point = new google.maps.Circle({
                    map: $scope.map,
                    center: $scope.track.points[i],
                    radius: 5,
                    strokeColor: "rgb(1,0,0)",
                });
                $scope.circles.push(point);
            }

	        $scope.countDistance();
            FeedReader.getTrackParameters($scope.selected).then(function(f){
                $scope.params = f
            });


            FeedReader.getStreets($scope.selected).then(function(f) {
                $scope.streets = f
            }, function() {
                $scope.error = true
            })


        })
    }

    FeedReader.getTracks().then(function(f) {
        $scope.tracks = f
    }, function() {
        $scope.error = true
    })
});  
