var app = angular.module("myApp2");
app.controller('TrackListController', function($scope, $location, FeedReader, Colors, $uibModal) {
    $scope.initialize = function() {
        $scope.other_track = null;
        $scope.map = new google.maps.Map(
            document.getElementById('map'),
            {
                center: {lat: 53.04, lng: 18.58},
                zoom: 12
            }
        );
    }

    $scope.deleteTrack = function() {
        FeedReader.deleteTrack($scope.selected).then(function()
        {
            FeedReader.getTracks().then(function(f) {
                $scope.tracks = f
                $scope.selected = null
            })
            if($scope.selected){
                $scope.track.reset()
                $scope.track = null;
                $scope.selected = null
            }
        })
    }

    $scope.joinTrack = function() {
        $scope.adding = true;
    }

    $scope.cancelAdd = function() {
        $scope.adding = false;
        $scope.other_track.reset()
        $scope.other_track = null;
        $scope.other = null;
    }

    $scope.joinTracks = function(){
        FeedReader.joinTracks($scope.selected, $scope.other).then(function(d){
            FeedReader.getTracks().then(function(f) {
                $scope.tracks = f
                $scope.cancelAdd()
                $scope.getTrack()
            }, function() {
                $scope.error = true
            })
        })
    }

    $scope.addTrack = function(){
        if($scope.other_track){
            $scope.other_track.reset();
            $scope.other_track = null;
        }

        FeedReader.getTrack($scope.other).then(function(data){
            data.splice(0, 0, $scope.data[$scope.data.length-1])
            $scope.other_track = new Track(data, $scope.map,Colors.next_color())
            $scope.otherTrack = {"center":[data[0].latitude, data[0].longitude]}
            $scope.otherTrack.points = []
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

    $scope.getTrack = function() {
        console.log($scope)
        FeedReader.getTrack($scope.selected).then(function(data) {
            $scope.data = data

            if($scope.track){
                $scope.track.reset()
                $scope.track = null;
            }


            $scope.track = new Track($scope.data, $scope.map, Colors.next_color())


            center = $scope.track.getCenter()
            $scope.map.setCenter({lat: center[0],lng: center[1]});

            distances = $scope.track.countDistance();
            $scope.sum = distances['sum']
            $scope.length = distances['length']

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

    $scope.initialize()
    FeedReader.getTracks().then(function(f) {
        $scope.tracks = f
    }, function() {
        $scope.error = true
    })
});  
