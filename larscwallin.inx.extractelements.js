(function(){
	// Check so that running the script is really necessary
    if( document.location.href.indexOf( '?' ) > 0 ){
	    var params = [];
	    var rawParams = [];
	    var hashes = [];
	    var href = '';
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

	    href = location.href;

	    if( document.location.hash !== '' ){
	    	// The hashes as the ids that should be affected by the script
			hashes = document.location.href.split( '#' );

			if( hashes.length > 0 ){
				// For now we only allow one id
				elementId = hashes[1];
				// Now we remove the hashes from the URL
				href = hashes[0];

			}else{
				elementId = false;
			}

	    }else{
	    	// No hash elements in the URL
    	}

    	href = href.split( '?' );

    	if( href.length > 1 ){

		    rawParams = href[1].split( '&' );
		    
		    if( rawParams.length > 0 ){
			    
			    rawParams.forEach(
		
			        function( i )
			        {
			        	var rule = i.split( '=' );
			        	var key = rule[0];
			        	var val = rule[1];
			        	if( validRules.indexOf( key ) >=0 ){
			        		hasRules = true;
			            	params.push( rule );
			            }else{
			            	// Not a valid rule
			            }		        
			         }
		
			    );
			
			}else{
				// No parameters in the URL 	
	        }

		    if( hasRules )
		    {

		        if( !elementId ){
		        	// Got no element id so we apply the style to the svg doc
		        	element = document.getElementsByTagName( 'svg' )[0];
		        }else{
		        	element = document.getElementById( elementId );
		        }

		        if(element){
					
					params.forEach(
				        function( rule )
				        {
				        	var val;
				        	if( rule.length === 2 ){
					        	val = rule[1];
								rules += ( rule[0] + ':' + val + ';' );
							}else{
								// Not a key/val pair								
							}
				        }
				    );

					if( rules != '' ){
						element.setAttribute( 'style', rules );
					}else{
						// No rules where returned from the foreach loop.
					}

		        }else{
		        	// element id reference returned null
		        }
		    }
		}
	}
})();
