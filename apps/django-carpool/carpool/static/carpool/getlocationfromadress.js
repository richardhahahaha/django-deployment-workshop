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
	},

});

gdgfields.utils.LocationSearchPopup = Class.$extend({
	
	__init__ : function(id, buttons) {
        this.dialog = $('<div id="' + id + '"><input type="text" id="' + id + '_search"/></div>')
		.appendTo(document.body)
		.dialog({
			autoOpen: true,
			show: "blind",
			hide: "explode"
		})
		new gdgfields.utils.LocationSearch(id + '_search', this.searchCallback)
        this.position = null
	},
	
	searchCallback: function( item ) {
		this.position = item.location
	},
	
});


