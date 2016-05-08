//var BASE_URL="http://service-kwiat78.rhcloud.com/rest/gps/";
var BASE_URL="http://127.0.0.1:8000/api/";

function restCall(method,url_,data_,positive,negative) {
    console.log(url_)
    console.log(data_)
    $.ajax({ 
	type: method,
	url: BASE_URL+url_,
	data: data_,
	//dataType:"jsonp",
	contentType:"application/json",
	success: positive,
	error: negative
    });
}

function restCall2(method,url_,data_,positive,negative) {
    console.log(url_)
    console.log(data_)
    $.ajax({ 
	type: method,
	url: BASE_URL+url_,
	data: data_,
	headers: {
	    Accept : "application/json; charset=utf-8","Content-Type": "application/json; charset=utf-8"
	},
	contentType:"application/json",
	success: positive,
	error: negative
    });
}


var polys;
var points = [];
var map;
var tracks=[];







function initialize(){
    /*map = new google.maps.Map(document.getElementById("map"),
            mapOptions);
    */
/*
    for(var t=0;t<tracks.length;t++)
    {
	if(!tracks[t].poly){
	    var track = new google.maps.Polyline({
		path: tracks[t].points,
		geodesic: true,
		strokeColor: tracks[t].color1,
		strokeOpacity: 1.0,
		strokeWeight: 2,
	    });
	    tracks[t].poly=track;
	    track.setMap(map);
	}
	
	if(!tracks[t].circles)
	{
	    tracks[t].circles = []
	    
	    for(var i=0;i<tracks[t].points.length;i++){
		
		
		var point= new google.maps.Circle({
		    map:map,
		    center:tracks[t].points[i],
		    radius:5,
		    strokeColor: tracks[t].color2
		});
		point.setMap(map)
		tracks[t].circles.push(point);
	    }
	}
    }*/
}




function setMap(selector){
    
    var idx = selector.parent().index()

    var val = selector.find(":selected").text();
    if(val)
    {
	var newTrack ={}
	var parent = $(this).parent()
	

	newTrack.label = val
	
	restCall("GET","tracks/"+val,{},function(data){
	    
	    newTrack.center =[]
	    newTrack.center[0]=data[0].latitude;
	    newTrack.center[1]=data[0].longitude;
	    map.setCenter({lat:newTrack.center[0],lng:newTrack.center[1]});
	
	    newTrack.points=[]
	    for(var i=0;i<data.length;i++)
	    {
		newTrack.points.push(new google.maps.LatLng(data[i].latitude, data[i].longitude));  
	    }
	    
	    if(tracks[idx]){
		newTrack.color1 = tracks[idx].color1
	    }
	    else{
		newTrack.color1=next_color()
	    }
	    newTrack.color2="rgb(0,0,0)"
	    if(tracks[idx]){		
		tracks[idx].poly.setMap(null);
		for(var j=0;j<tracks[idx].circles.length;j++)
		    tracks[idx].circles[j].setMap(null);
	    }
	    tracks.splice(idx,1,newTrack)
	    console.log("tracks",tracks)
	    
	
	    initialize();
	});
    }
}

function delTrack(selector){
    console.log("DEL");
    var idx = selector.parent().index()
    console.log(idx)
    console.log(tracks[idx])
    if(tracks[idx]){	
	console.log("clearing",tracks[idx])
	tracks[idx].poly.setMap(null);
	for(var j=0;j<tracks[idx].circles.length;j++)
	    tracks[idx].circles[j].setMap(null);
    }
    console.log(tracks[idx])
    tracks.splice(idx,1)
    console.log(tracks)

    //initialize();
}


function addTrack(event_)
{
    var tracks = $('#tracks')
    $('#tracks').append("<div class='track'/>")
    var parent = $('.track').last()
    console.log(parent)
    parent.append("<select class='selectTrack'/>")
    parent.append("<button>del</button>")
    
    var newTrackSelector = parent.find('.selectTrack')
    var newTrackDeletor = parent.find('button')
    console.log(newTrackDeletor)
    restCall("GET","tracks/",{},function(data){
	console.log(data);
	for(var i=0;i<data.length;i++){
	    newTrackSelector.append($('<option>', {
		value: i,
		text: data[i]
	    }));    
	}
	setMap(newTrackSelector);
	newTrackSelector.change(
	    function(){
		setMap($(this))
	    });
	
	newTrackDeletor.click(
	    function(){
		delTrack($(this))
		$(this).parent().remove()
	    });
    });
    event_.preventDefault();
    
}



$(document).ready(function(){
    var newTrackSelector = $('#tracks')
    $("#changeLabel").prop('disabled', true);
    $("#deleteTrack").prop('disabled', true);
    $("#joinTracks").prop('disabled', true);

    
    restCall("GET","tracks/",{},function(data){
	console.log(data);
	for(var i=0;i<data.length;i++){
	    newTrackSelector.append($('<option>', {
		value: i,
		text: data[i]
	    }));    
	}
	
	
	
	newTrackSelector.change(function()
	    {
		
		
		var selected = $(this).find(":selected")
		selected.each(function(s)
		{
		        console.log($(this).text());
		});
		
		if(selected.length==1){
		    $("#changeLabel").prop('disabled', false);
		    $("#deleteTrack").prop('disabled', false);
		    $("#joinTracks").prop('disabled', true);
		    label = selected[0].text
		    
		    $("#changeLabel").off("click")
		    $("#deleteTrack").off("click")
		    $("#joinTracks").off("click")
		    
		    $("#changeLabel").click(label,function(){
			$("#changeLabel").prop('disabled', true)
			$("#tracks").prop('disabled', true);
			console.log(label);
			$('#operations').append("<input type='text' id='newLabel'><button id='ok'>OK</button><button id='cancel'>CANCEL</button>")
			$('#ok').click(function(){
				var nlabel = $('#newLabel').val()
				
				if(nlabel!='')
				
				    restCall2("POST","tracks/"+label,JSON.stringify({new_label:nlabel}),function(){
					$('#operations').empty();
					$("#tracks").prop('disabled', false);
				
					$("#changeLabel").prop('disabled', false);
					selected[0].text = nlabel;
				    })
				    
				
			})
			$('#cancel').click(function(){
				$('#operations').empty();
				$("#tracks").prop('disabled', false);
				
				$("#changeLabel").prop('disabled', false);
			})
			
	    
		    })
		    
		    $("#deleteTrack").click(label,function(){
			
			
			 restCall2("DELETE","tracks/"+label,{},function(){
					
			selected[0].remove()		
				
			    //$("#changeLabel").prop('disabled', false);
			    
			})
				    
				
			

	    
		    })
		}
		else
		{
		    $("#changeLabel").prop('disabled', true)
		    $("#changeLabel").off("click")
		    
		    $("#deleteTrack").prop('disabled', true)
		    $("#deleteTrack").off("click")
		    $("#joinTracks").off("click")
		    
		    $("#joinTracks").prop('disabled', false)
		    if(selected.length>1)
		    {
			$("#joinTracks").click(label,function(){
			console.log(label);
			$("#joinTracks").prop('disabled', true)
			$("#tracks").prop('disabled', true);
			$('#operations').append("<input type='text' id='newLabel'><button id='ok'>OK</button><button id='cancel'>CANCEL</button>")
			$('#ok').click(function(){
				var nlabel = $('#newLabel').val()
				
				if(nlabel!='')
				{
				    var toJoin=[];
				    selected.each(function(s)
				    {
					toJoin.push($(this).text());
				    });
				    console.log(nlabel)
				    console.log(toJoin)
				    
				    restCall2("POST","join/"+nlabel,JSON.stringify(toJoin),function(){
					$('#operations').empty();
					$("#tracks").prop('disabled', false);
				
					$("#joinTracks").prop('disabled', true);
					
					restCall("GET","tracks/",{},function(data){
					    newTrackSelector.empty()
					    for(var i=0;i<data.length;i++){
						newTrackSelector.append($('<option>', {
						value: i,
						text: data[i]	
						}));    
						}
					})
					
				    })
				
				}
				
				    
				
			})
			$('#cancel').click(function(){
				$('#operations').empty();
				$("#tracks").prop('disabled', false);
				
			})
			
	    
		    })
		    
		    }
		    
		}
		
		
	    })
    });
    
    
    
    
});
