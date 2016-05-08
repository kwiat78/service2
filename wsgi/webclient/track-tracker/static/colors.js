var app = angular.module("myApp2");
app.service('Colors', function() {
    var start_h = Math.random();
    var h=start_h;
    var grc = 0.618033988749895;

    function hsv_to_rgb(h,s,v){
        h1=h*360
        c=v*s
        x=c*(1-Math.abs((h1/60) % 2-1))
        m = v-c
        if(h1<60){i=c; j=x; k=0}
        else if(h1<120){i=x; j=c; k=0}
        else if(h1<180){i=0; j=c; k=x}
        else if(h1<240){i=0; j=x; k=c}
        else if(h1<300){i=x; j=0; k=c}
        else if(h1<360){i=c; j=0; k=x}

        r=Math.round((i+m)*255)
        g=Math.round((j+m)*255)
        b=Math.round((k+m)*255)
        return "rgb("+r+","+g+","+b+")";
    }

    this.next_color = function() {
        h+=grc
        h%=1
        return hsv_to_rgb(h,0.99,0.95)
    }
 })
