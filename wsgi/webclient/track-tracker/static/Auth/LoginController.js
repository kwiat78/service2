var app = angular.module("myApp2");
app.controller('LoginController', function($scope, $location, $window, FeedReader, Colors, $uibModal) {
    $scope.submit = function(){
         FeedReader.login($scope.user.username, $scope.user.password).then(function(data) {
                        $window.sessionStorage.setItem('token', data.token);
                        window.location.hash=$window.sessionStorage.next


                        console.log($window)
                        console.log(data)

    }, function() {
        $scope.error = true
    })
    }
});  
