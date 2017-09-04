class Track {
    constructor(data, map, color) {
        this.data = data
        this.map = map
        this.length = data.length
        this.center = this.getCenter()
        this.color = color
        this.dots = []
        this.locations = []
        self = this
        console.log(self);

         this.line = new google.maps.Polyline({
            path: this.locations,
            geodesic: true,
            strokeColor: this.color,
            strokeOpacity: 1.0,
            strokeWeight: 2,
        });
        this.line.setMap(map)

        for(var i=0;i<this.length;i++) {
            self.add_location(self.data[i])
        }
    }

    getCenter(){
        var ltd = 0
        var lng = 0
        for(var i=0;i<this.length;i++){
            ltd += this.data[i].latitude
            lng += this.data[i].longitude
        }
        return [ltd/this.length, lng/this.length]
    }



    prepare_dots(){
        for(var i=0;i<this.length;i++) {
            this.add_dot(this.locations[i])
        }
    }

    show_dots(){
        for(var i=0;i<this.length;i++) {
            this.dots[i].setMap(this.map)
        }
    }

    toggle_dots(){
        var map_x = this.map;
        if(this.dots[0].getMap()){
            map_x = null
        }
        for(var i=0;i<this.length;i++) {
            this.dots[i].setMap(map_x)
        }
    }

    toggle_line(){
        var map_x = this.map;
        if(this.line.getMap()){
            map_x = null
        }
        this.line.setMap(map_x)

    }

    hide_dots(){
        for(var i=0;i<this.length;i++) {
            this.dots[i].setMap(null)
        }
    }

    prepare_line(){
        this.line = new google.maps.Polyline({
            path: this.locations,
            geodesic: true,
            strokeColor: this.color,
            strokeOpacity: 1.0,
            strokeWeight: 2,
        });
    }

    show_line(){
        this.line.setMap(this.map)
    }

    hide_line(){
        this.line.setMap(null)
    }


    add_dot(x){
            var point = new google.maps.Circle({
                map:null,
                center:x,
                radius:5,
                strokeColor: "rgb(0,0,0)"
            });
            this.dots.push(point);
    }
    countDistance() {

        var s=0;
        var l = google.maps.geometry.spherical.computeLength(this.locations)
        for(var i=0; i<this.length; i++) {
	        s+=google.maps.geometry.spherical.computeDistanceBetween (this.locations[i],this.locations[(i+1)%this.length]);
        }
        var sum_ = parseFloat(s/1000).toFixed(2);

        var length_ = parseFloat(l/1000).toFixed(2);
        return {
            sum: sum_,
            length: length_
        }
    }

    add_location(location){
        console.log(location)
        location = new google.maps.LatLng(location.latitude, location.longitude)

        this.locations.push(location);

        var point = new google.maps.Circle({
                map:null,
                center:location,
                radius:5,
                strokeColor: "rgb(0,0,0)"
        });
        this.dots.push(point);
        point.setMap(this.map)
        this.line.setPath(this.locations)
    }

    reset(){
        this.hide_line()
        this.hide_dots()
        this.locations = []
        this.dots = []
        this.line = null

    }
}
