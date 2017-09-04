var app = angular.module("myApp2");
app.controller('TrackViewerController', function($scope, $location, FeedReader, Colors) {
    $scope.map_tracks = []

    $scope.map = new google.maps.Map(
        document.getElementById("map"),
        {
            center: {lat: 53.04, lng: 18.58},
            zoom: 12
        }
    );

    FeedReader.getTracks().then(function(data) {
        $scope.tracks = data
        console.log("data",data)
    })

    $scope.delete_track=function ($event, row){
        row.track.reset()
        delete row.track
        $($event.target).closest('div').remove()
    }

    $scope.show_dots = function (row){
        row.track.toggle_dots()
    }

    $scope.show_line=function (row){
        row.track.toggle_line()
    }

    $scope.addTrack = function (event_) {
        $scope.map_tracks.push({color1:Colors.next_color()})
    }

    $scope.setMap=function (row){
        FeedReader.getTrack(row.selected).then(function(data){
            $scope.data = data
            if(row.track){
                row.track.reset()
            }
            row.track = new Track($scope.data, $scope.map, Colors.next_color())
            center = row.track.getCenter()
            $scope.map.setCenter({lat: center[0],lng: center[1]});
        })
    }
})
