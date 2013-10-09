(function(){
    if(document.location.hash !== undefined){
	    var params = [];
	    var element;
		var elementId;
	    var rules = '';
	    var hasRules = false;
	    var validRules = [
	    	'fill',
	    	'fill-opacity',
	    	'fill-rule',
	    	'display',
	    	'stroke',
	    	'stroke-opacity',
	    	'stroke-width'
	    ];

	    location.href.split( '?' )[1].split( '&' ).forEach(
	        function( i )
	        {
	        	var rule = i.split( '=' );
	        	var key = rule[0];
	        	var val = rule[1];
	        	if(key!=='id'){
		        	if(validRules.indexOf(key)>=0){
		        		hasRules = true;
		            	params.push(rule);
		            }else{
		            	// Not a valid rule
		            }
	        	}else{
	        		// Save the id, if it exists.
	        		elementId = val;
	        	}
	        }
	    );

	    if( hasRules )
	    {

	        if(!elementId){
	        	// Got no element id so we apply the style to the svg doc
	        	element = document.getElementsByTagName('svg')[0];
	        }else{
	        	element = document.getElementById( elementId );
	        }

	        if(element){
				
				params.forEach(
			        function( rule )
			        {
			        	var val;
			        	if(rule.length === 2){
				        	val  = rule[1];
							rules += ( rule[0] + ':' + val + ';');
						}else{
							// Not a key/val pair								
						}
			        }
			    );

				if(rules != ''){
					element.setAttribute( 'style', rules );
				}else{
					// No rules where returned from the foreach loop.
				}

	        }else{
	        	// element id reference returned null
	        }
	    }
	}
})();
