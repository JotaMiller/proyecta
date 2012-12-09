/*
 * Minichat
 * hola@jotamiller.cl
 */

$(document).ready(function(){
	//originalTitle = document.title;
	//startChatSession();

	$('#chat_admin, #minichat a').click(function (){
		if ($('#lista_admin').hasClass('open')){
			$('#lista_admin').removeClass('open');	
		}else{
			$('#lista_admin').addClass('open');	
		}
	})
	
});