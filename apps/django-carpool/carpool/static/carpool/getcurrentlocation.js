
var getCurrentLocation = (function(){
    
    var currentLocation = null
    var triedLocation = false
    var supportedLocation = false
    var errorLocation = false
    var locationCallbacks = []
    var firstCallback = true
    var requestedLocation = false
    
    function callLocationCallbacks() {
        for (var i=0;i<locationCallbacks.length;i++) {
            var callback = locationCallbacks[i]
            callback(currentLocation, supportedLocation, errorLocation, firstCallback)
            firstCallback = false
        }
        locationCallbacks = []
    }
    
    return function(callback) {
        if (!requestedLocation) {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(function(position) {
                    currentLocation = new google.maps.LatLng(position.coords.latitude,position.coords.longitude);
                    triedLocation = true
                    supportedLocation = true
                    callLocationCallbacks()
                }, function() {
                    triedLocation = true
                    supportedLocation = true
                    errorLocation = true
                    callLocationCallbacks()
                });
            } else if (google.gears) {
                alert('gears')
                var geo = google.gears.factory.create('beta.geolocation');
                geo.getCurrentPosition(function(position) {
                    currentLocation = new google.maps.LatLng(position.latitude,position.longitude);
                    triedLocation = true
                    supportedLocation = true
                    callLocationCallbacks()
                }, function() {
                    triedLocation = true
                    supportedLocation = true
                    errorLocation = true
                    callLocationCallbacks()
                });
    
            } else {
                triedLocation = true
            }
        }
        requestedLocation = true
    
        if (!triedLocation) {
            locationCallbacks.push(callback)
        }
        else {
            callback(currentLocation, supportedLocation, errorLocation, firstCallback)
            firstCallback = false
        }
    
    }
})()