
function delTrack(selector){
    console.log("DEL");
    var idx = selector.parent().index()
    console.log(idx)
    console.log(tracks[idx])
    if(tracks[idx]){
	console.log("clearing",tracks[idx])
	tracks[idx].poly.setMap(null);
	for(var j=0;j<tracks[idx].circles.length;j++)
	    tracks[idx].circles[j].setMap(null);
    }
    console.log(tracks[idx])
    tracks.splice(idx,1)
    console.log(tracks)
}


var app = angular.module("myApp2");
app.controller('TrackViewerController', function($scope, $location, FeedReader, Colors) {
    $scope.tracks2=[]
    mapOptions = {
        center: { lat: 53.04, lng: 18.58},
        zoom: 12
    };

    $scope.map = new google.maps.Map(document.getElementById("map"),
            mapOptions);

    FeedReader.getTracks().then(function(f) {
        $scope.tracksX = f
        console.log("f",f)

    })


    $scope.addTrack = function (event_) {
        $scope.tracks2.push({color1:Colors.next_color()})
    }

    $scope.setMap=function (track,label){
        FeedReader.getTrack(track.selected).then(function(data){
            track.center = [data[0].latitude, data[0].longitude]
            $scope.map.setCenter({lat:track.center[0],lng:track.center[1]});

            track.points=[]
	        for(var i=0;i<data.length;i++) {
		        track.points.push(new google.maps.LatLng(data[i].latitude, data[i].longitude));
	        }

            if(track.poly){
                track.poly.setMap(null);
            }

            track.poly = new google.maps.Polyline({
                path: track.points,
                geodesic: true,
                strokeColor: track.color1,
                strokeOpacity: 1.0,
                strokeWeight: 2,
            });

	        track.poly.setMap($scope.map);

	        if(track.circles) {
	            for(var i=0;i<track.circles.length;i++){
	                track.circles[i].setMap(null)
	            }
	        }

            track.circles = []

            for(var i=0;i<track.points.length;i++) {
                var point = new google.maps.Circle({
                    map:map,
                    center:track.points[i],
                    radius:5,
                    strokeColor: "rgb(0,0,0)"
                });
                point.setMap($scope.map)
                track.circles.push(point);
            }
        })
    }

})

