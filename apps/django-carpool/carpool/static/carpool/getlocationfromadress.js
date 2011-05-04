var gdgfields = window.gdgfields || {}
gdgfields.utils = gdgfields.utils || {}

gdgfields.utils.GeoCoder = new google.maps.Geocoder()

gdgfields.utils.LocationSearch = Class.$extend({

	__init__ : function(id, callback) {
        this.callback = callback
		$( '#'+ id ).autocomplete({
	            source: $.proxy(this.autocompleteSource, this),
	            minLength: 2,
	            select: $.proxy(this.selectPosition, this)
        })
        .data( "autocomplete" )._renderItem = function( ul, item ) {
			     return $( "<li></li>" )
				    .data( "item.autocomplete", item )
    				.append( "<a><strong>" + item.label + "</strong><br>" + item.desc + "</a>" )
	       			.appendTo( ul );
        };

	},
	
	autocompleteSource : function( request, response ) {
		gdgfields.utils.GeoCoder.geocode( {'address': request.term}, function(results, status) {

			response($.map(results, function(item) {
				
				// split returned string
				var place_parts = item.formatted_address.split(",");
				var place = place_parts[0];
				var place_details = "";
				
				// parse city, state, and zip
				for(i=1;i<place_parts.length;i++){
					place_details += place_parts[i];
					if(i !== place_parts.length-1) place_details += ",";
				}
				var item_count = 0
				// return top 8 results
				if (item_count < 8) {
					return {
					    label: place,
					    value: item.formatted_address,
					    desc: place_details,
					    location: item.geometry.location
					}
				}
			} // fn end
			) // map end
			) // response end
		} // fn end
		) // geocoder end
	},
	selectPosition: function( event, ui ) {
		this.callback(ui.item)
	},

});

gdgfields.utils.LocationSearchPopup = Class.$extend({
	
	__init__ : function(id, map, buttons) {
		this.smallmapid = id + '_smallmap'
        this.dialog = $('<div id="' + id + '"><input type="text" size="48" id="' + id + '_search"/><div style="visibility: hidden; width: 340px; height: 300px;" id="' + id + '_smallmap"></div></div>')
		.dialog({
			width: 380,
			height: 460,
			buttons: buttons,
			resizable: false,
			autoOpen: true,
			show: "blind",
			hide: "explode"
		})
		
		new gdgfields.utils.LocationSearch(id + '_search', $.proxy(this.searchCallback, this))
        this.position = null
        this.map = map
        
        var latlng = new google.maps.LatLng(0, 0);
        var smallmapOptions = {
            zoom: 13,
            center: latlng,
            mapTypeId: google.maps.MapTypeId.ROADMAP,
            scaleControl : false,
            mapTypeControl : false,
            streetViewControl : false
        }
        this.smallmap = new google.maps.Map(document.getElementById(id + '_smallmap'), smallmapOptions); 
        this.smallmarker = new google.maps.Marker({
            map: this.smallmap,
            draggable: false
        }); 
        
        
	},
	
	searchCallback : function( item ) {
		$('#' + this.smallmapid).css("visibility", "visible")
		this.smallmarker.setPosition(item.location)
        this.smallmap.setCenter(item.location); 
		this.position = item.location
	}
	
});

gdgfields.utils.LocationSearchStartEndPopup = gdgfields.utils.LocationSearchPopup.$extend({
	
	__init__ : function(id, map) {
		var that = this
        this.$super(id, map, [
		    {
		    	disabled: true,
		        text: "Pan here",
		        click: this.centerMapCallback
		    },
		    {
		    	disabled: true,
		        text: "Set start",
		        click: this.setStartCallback
		    },
		    {
		    	disabled: true,
		        text: "Set end",
		        click: this.setEndCallback
		    },
		    {
		        text: "Cancel",
		        click: function() {
		        	that.dialog.dialog("close")
		        }
		    },
		])
	},
	

	centerMapCallback : function( item ) {
		this.position = item.location
	},
	
	setStartCallback : function( item ) {
		this.position = item.location
	},
	
	setEndCallback : function( item ) {
		this.position = item.location
	}
	
});


