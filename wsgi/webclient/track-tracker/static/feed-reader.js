var app = angular.module("myApp2");
app.service('FeedReader', function($http) {
    

    function init() {
        options = {}
        options.url="http://service2-kwiat78.rhcloud.com"

    }


    this.getTracks = function() {
        init()
        return $http.get(options.url + "/api/tracks", {headers: {}}).then(
            function(obj){
                return obj.data;
            })
    }

    this.getMap = function() {
        init()
        return $http.get("/api/map", {headers: {}}).then(
            function(obj){
                return obj.data;
            })
    }

    this.postTracks = function(label, new_label) {
        init()
        return $http.put(options.url + "/api/tracks/"+label+"/", {"new_label":new_label}, {headers: {}}).then(
            function(obj){
                return obj.data;
            })
    }

    this.joinTracks = function(label, second_label) {
        init()
        return $http.post(options.url + "/api/tracks/"+label+"/join/", {"second_label":second_label}, {headers: {}}).then(
            function(obj){
                return obj.data;
            })
    }

    this.deleteTrack = function(label) {
        init()
        return $http.delete(options.url + "/api/tracks/"+label+"/", {}, {headers: {}}).then(
            function(obj){
                return obj.data;
            })
    }

    this.getTrack = function(val) {
        init()
//        return $http.get(options.url + "/api/tracks/"+val+"/", {headers: {}}).then(
        return $http.get(options.url + "/api/tracks/"+val+"/with_streets", {headers: {}}).then(
        //return $http.get(options.url + "/api/tracks/"+val+"/intersections", {headers: {}}).then(
        //return $http.get(options.url + "/api/tracks/"+val+"/intersections/", {headers: {}}).then(
        //return $http.get(options.url + "/api/tracks2/"+val+"/snap/", {headers: {}}).then(
            function(obj){
                return obj.data;
            })
    }

    this.getTrackParameters = function(val) {
        init()
        return $http.get(options.url + "/api/tracks/"+val+"/params", {headers: {}}).then(
        //return $http.get(options.url + "/api/tracks/"+val+"/intersections", {headers: {}}).then(
        //return $http.get(options.url + "/api/tracks/"+val+"/intersections/", {headers: {}}).then(
        //return $http.get(options.url + "/api/tracks2/"+val+"/snap/", {headers: {}}).then(
            function(obj){
                return obj.data;
            })
    }

    this.getStreets = function(val) {
        init()
        return $http.get(options.url + "/api/tracks/"+val+"/streets/", {headers: {}}).then(
            function(obj){
                return obj.data;
            })
    }
    
    
}); 
