(function(){
    if(document.location.hash){
	    var params = [];
	    var element;
		var elementId;
	    var isValid = false;
	    var rules = '';
	    var hasRules = false;

	    location.href.split( '?' )[1].split( '&' ).forEach(
	        function( i )
	        {
	        	rule = i.split( '=' );
	        	key = rule[0];
	        	val = rule[1];
	        	if(key!='id'){
	        		hasRules = true;
	            	params.push(rule);
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
			        	if(rule.length == 2){
				        	val  = rule[1];
					    	isValid = /(^#[0-9A-F]{6}$)|(^#[0-9A-F]{3}$)/i.test(val);
					    	// We only allow hex values
					    	if(isValid){
								 rules += ( rule[0] + ':' + val + ';');
							}
						}else{
							// Not a key/val pair								
						}
			        }
			    );

				if(rules !== ''){
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
