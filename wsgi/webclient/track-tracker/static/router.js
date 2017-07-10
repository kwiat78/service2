var app = angular.module('myApp2', ["ngRoute", "ngCookies", "ui.bootstrap.contextMenu", "ui.bootstrap"])
.config(['$routeProvider',"$httpProvider", "$compileProvider",
  function($routeProvider, $httpProvider, $compileProvider) {
    $httpProvider.interceptors.push('authInterceptor');
    $routeProvider.
      when('/track_list', {
        templateUrl: '../static/TrackList/TrackListView.html',
        controller: 'TrackListController'
      }).
      when('/track_viewer', {
        templateUrl: '../static/TrackViewer/TrackViewerView.html',
        controller: 'TrackViewerController'
      }).
      when('/map', {
        templateUrl: '../static/Map/MapView.html',
        controller: 'MapController'
      }).
      when('/live', {
        templateUrl: '../static/Live/LiveView.html',
        controller: 'LiveController'
      }).
      when('/login', {
        templateUrl: '../static/Auth/LoginView.html',
        controller: 'LoginController'
      }).
      when('/logout', {
        templateUrl: '../static/Auth/LogoutView.html',
        controller: 'LogoutController'
      }).
      otherwise({
        redirectTo: '/index.html'
      });
    
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
    //$httpProvider.defaults.headers.common.user = 'szymon';

    
    /*$compileProvider.aHrefSanitizationWhitelist(/^\s*(https?|ftp|mailto|file|chrome-extension):/);*/

  }]);

  app.factory('authInterceptor', function ($rootScope, $q, $window) {

  return {

    request: function (config) {
      config.headers = config.headers || {};
      if ($window.sessionStorage.token) {
        config.headers.Authorization = 'JWT ' + $window.sessionStorage.token;
        $rootScope.token = $window.sessionStorage.token
      }
      return config;
    },
    response: function (response) {

        if(window.location.hash!='#/login'){
            if(!$window.sessionStorage.token)
            {
                  $window.sessionStorage.setItem('next', window.location.hash);
                  window.location.href = '/#/login';

            }
        }

      if (response.status === 401) {
        // handle the case where the user is not authenticated

      }
      return response || $q.when(response);
    },

  };
});



 
