var app = angular.module('myApp2', ["ngRoute", "ngCookies", "ui.bootstrap.contextMenu", "ui.bootstrap"])
.config(['$routeProvider',"$httpProvider", "$compileProvider",
  function($routeProvider, $httpProvider, $compileProvider) {
    $routeProvider.
      when('/a', {
        templateUrl: '../static/TrackList/TrackListView.html',
        controller: 'TrackListController'
      }).
      when('/b', {
        templateUrl: '../static/TrackViewer/TrackViewerView.html',
        controller: 'TrackViewerController'
      }).
      otherwise({
        redirectTo: '/index.html'
      });
    
     $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
    //$httpProvider.defaults.headers.common.user = 'szymon';
    
    /*$compileProvider.aHrefSanitizationWhitelist(/^\s*(https?|ftp|mailto|file|chrome-extension):/);*/

  }]);



 
