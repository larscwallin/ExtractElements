(function(){
	    if(document.location.hash){
		    var params = { };
		    var element;
		    var valCheck = false;

		    location.href.split( '?' )[1].split( '&' ).forEach(
		        function( i )
		        {
		            params[ i.split( '=' )[0] ] = i.split( '=' )[1];
		        }
		    );

		    // Force attribute to fill at the moment.
			params.attr = 'fill';

	    	valCheck  = /(^#[0-9A-F]{6}$)|(^#[0-9A-F]{3}$)/i.test(params.value);

	    	// We only allow hex values
	    	if(valCheck){

			    if( params.attr &&  params.value )
			    {

			        if(!params.id){
			        	element = document.getElementsByTagName('svg')[0];
			        }else{
			        	element = document.getElementById( params.id );
			        }

			        if(element){
						element.setAttribute( 'style', ( params.attr + ':' + params.value + ';') );
			        }else{
			        	// element id reference returned null
			        }
			    }
		    }
		}
})();
