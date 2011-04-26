var gdgfields = window.gdgfields || {}
gdgfields.utils = gdgfields.utils || {}

gdgfields.utils.LocationSearchClass = Class.$extend({
	
	__init__ : function() {
		this.geoCoder = new google.maps.Geocoder()
		this.dialog = null
	},
	
	getDialog : function() {
		if (!this.dialog) {
			this.dialog = $('<div id="autocomplete_address_dialog"></div>')
				.appendTo(document.body)
				.dialog({
					autoOpen: false,
					show: "blind",
					hide: "explode"
				}	
			)
			$( '<input type="text" id="autocomplete_address_input"/>' )
				.appendTo(this.dialog.dialog("widget"))
				.autocomplete({
		            source: $.proxy(this.autocompleteSource, this),
		            minLength: 2,
		            select: $.proxy(this.selectPosition, this)
	        })
	    }
	    return this.dialog
	},
	
	autocompleteSource : function( request, response ) {
		this.geoCoder.geocode( {'address': request.term}, function(results, status) {

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
					item_count++;
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
		this.getDialog().dialog("close")
	},
	
	popUp : function( callback ) {
		this.callback = callback
		this.getDialog().dialog("open")
	}
	
});

gdgfields.utils.LocationSearch = new gdgfields.utils.LocationSearchClass()

