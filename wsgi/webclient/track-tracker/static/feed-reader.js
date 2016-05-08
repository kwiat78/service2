var app = angular.module("myApp2");
app.service('FeedReader', function($http) {
    

    function init() {
        options = {}
        options.url="http://service2-kwiat78.rhcloud.com"
        //options.url="http://127.0.0.1:8000"
    }


    this.getTracks = function() {
        init()
        return $http.get(options.url + "/api/tracks", {headers: {}}).then(
            function(obj){
                return obj.data;
            })
    }

    this.postTracks = function(label, new_label) {
        init()
        return $http.post(options.url + "/api/tracks/"+label, {"new_label":new_label}, {headers: {}}).then(
            function(obj){
                return obj.data;
            })
    }

    this.deleteTrack = function(label) {
        init()
        return $http.delete(options.url + "/api/tracks/"+label, {}, {headers: {}}).then(
            function(obj){
                return obj.data;
            })
    }

    this.getTrack = function(val) {
        init()
        //return $http.get(options.url + "/api/tracks/"+val, {headers: {}}).then(
        //return $http.get(options.url + "/api/tracks/"+val+"/intersections", {headers: {}}).then(
        //return $http.get(options.url + "/api/tracks/"+val+"/intersections", {headers: {}}).then(
        return $http.get(options.url + "/api/tracks/"+val+"", {headers: {}}).then(
            function(obj){
                return obj.data;
            })
    }

    this.getStreets = function(val) {
        init()
        //return $http.get(options.url + "/api/tracks/"+val, {headers: {}}).then(
        return $http.get(options.url + "/api/tracks/"+val+"/streets", {headers: {}}).then(
            function(obj){
                return obj.data;
            })
    }
    
    
}); 
