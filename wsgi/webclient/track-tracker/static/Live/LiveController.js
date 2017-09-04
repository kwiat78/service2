var app = angular.module("myApp2");
app.controller('LiveController', function($scope, $location, $interval, FeedReader, Colors, $uibModal) {

    $scope.map = new google.maps.Map(
        document.getElementById('map'),
        {
            center: {lat: 53.04, lng: 18.58},
            zoom: 12
        }
    );

    $scope.update_track = null;

    $scope.getTrack = function(){
        FeedReader.getLive().then(function(data2){
            $scope.selected = data2.label
            FeedReader.getTrack($scope.selected).then(function(data) {
                $scope.data = data
                $interval.cancel($scope.update_track)
                $scope.track = new Track($scope.data, $scope.map, Colors.next_color())
                center = $scope.track.getCenter()
                $scope.map.setCenter({lat: center[0],lng: center[1]});
                distances = $scope.track.countDistance();
                $scope.sum = distances['sum']
                $scope.length = distances['length']
                FeedReader.getTrackParameters($scope.selected).then(function(f){
                    $scope.params = f
                    if(!$scope.params.ended)
                    {
                        $scope.update_track = $interval(function(){
                            last_date = data[data.length-1].date
                            FeedReader.getTrack($scope.selected,last_date).then(function(data2) {
                                if(data2.length>0) {
                                    for(var i=0;i<data2.length;i++) {
                                        $scope.track.add_location(data2[i])
                                        $scope.data.push(data2[i])
                                    }

                                    FeedReader.getTrackParameters($scope.selected).then(function(f){
                                        $scope.params = f
                                    })
                                }
                            })
                        }, 10000)
                    }
                });

                FeedReader.getStreets($scope.selected).then(function(f) {
                    $scope.streets = f
                }, function() {
                    $scope.error = true
                })
            })
        })
    }
    $scope.getTrack()
});  
