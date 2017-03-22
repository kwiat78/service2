var app = angular.module("myApp2");
app.controller('LogoutController', function($scope, $location, $window) {
    $window.sessionStorage.removeItem('token');
});  
