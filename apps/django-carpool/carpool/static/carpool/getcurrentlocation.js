
var gdgfields = window.gdgfields || {}
gdgfields.utils = gdgfields.utils || {}

gdgfields.utils.CurrentLocationClass = Class.$extend({
	
	__init__ : function() {
		this.currentLocation = null
		this.triedLocation = false
		this.supportedLocation = false
		this.errorLocation = false
		this.locationCallbacks = []
		this.firstCallback = true
		this.requestedLocation = false
	},
	
	findLocation : function(callback) {
		
		if (!this.requestedLocation) {
	        if (navigator.geolocation) {
	        	this.findUsingGeolocation(callback)
	        } else if (google.gears) {
				this.findUsingGears(callback)
	        } else {
	            this.triedLocation = true
	        }
	    }
	    this.requestedLocation = true
	      	
	    if (!this.triedLocation) {
	        this.locationCallbacks.push(callback)
	    }
	    else {
	        callback(this.currentLocation, this.supportedLocation, this.errorLocation, this.firstCallback)
	        this.firstCallback = false
	    }
	},
	
	findUsingGeolocation : function(callback) {
		var that = this
		navigator.geolocation.getCurrentPosition(function(position) {
		    that.currentLocation = new google.maps.LatLng(position.coords.latitude,position.coords.longitude);
		    that.triedLocation = true
		    that.supportedLocation = true
		    that.callLocationCallbacks()
		}, function() {
		    that.triedLocation = true
		    that.supportedLocation = true
		    that.errorLocation = true
		    that.callLocationCallbacks()
		});  	
	},
	
	findUsingGears : function(callback) {
		var that = this
		var geo = google.gears.factory.create('beta.geolocation');
        geo.getCurrentPosition(function(position) {
            that.currentLocation = new google.maps.LatLng(position.latitude,position.longitude);
		    that.triedLocation = true
		    that.supportedLocation = true
		    that.callLocationCallbacks()
		}, function() {
		    that.triedLocation = true
		    that.supportedLocation = true
		    that.errorLocation = true
		    that.callLocationCallbacks()
		});  	
	},
	
	callLocationCallbacks : function () {
        for (var i=0;i<this.locationCallbacks.length;i++) {
            var callback = this.locationCallbacks[i]
            callback(this.currentLocation, this.supportedLocation, this.errorLocation, this.firstCallback)
            this.firstCallback = false
        }
        this.locationCallbacks = []
    }    

});

gdgfields.utils.CurrentLocation = new gdgfields.utils.CurrentLocationClass()

