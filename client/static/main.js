var url = "http://"+location.host;
var urlws = "ws://"+location.host;
var token;
var ws;


/**
 * Collect user name and get token.
 * Make websocket connection using token.
 * When message received on websocket, show it as bot message.
 */
$('#name_button').on('click', function (e) {
	if($('#name_input').val() == ''){
		$('#warn_msg').html('Please enter your name');
		$('#loading_div').show();
	}
	else{

		$('#name_button')[0].disabled = true;
		$('#warn_msg').html('Connecting to AI ChatBot. Please wait...');
		$('#loading_div').show();
		// get name and generate token
		$.ajax({
			type: "POST",
			dataType: "json",
			contentType: "application/json",
			url: url+"/token?name="+$('#name_input').val(),
			success: function(data){
				token = data["token"];

				ws = new WebSocket(urlws+"/chat?token="+token);
				ws.onopen = function(e){
					console.log('Websocket Connected');
					$('#name_div').hide();
					$('#loading_div').hide();
					$('#chat_div').show();
					showBotMessage('Hello '+ $('#name_input').val() + '! How can I help you?');
					$('#msg_input').focus();
				}
				ws.onmessage = function(e){
					js = JSON.parse(e.data);
					js = JSON.parse(js);
					resp = js.msg;
					// console.log(typeof js);

					setTimeout(function () {
						showBotMessage(resp);
					}, 300);
					$('#msg_input')[0].placeholder = "Enter your message";

				}
				ws.onclose = function(e){
					console.log('Websocket Closed.');
					$('#name_button')[0].disabled = false;
					$('#name_input').val('');
				}
				ws.onerror = function(e){
					console.log(e)
					$('#name_button')[0].disabled = false;
				}
			},
			error: function(e){
				console.log(e);
				$('#name_button')[0].disabled = false;
			}
		});

	}
});


// Execute above function when the user presses Enter key on the keyboard
$('#name_input').keypress(function(event) {
  // If the user presses the "Enter" key on the keyboard
  if (event.key === "Enter") {
    // Trigger the button element with a click
    $('#name_button').click();
  }
});

/**
 * Returns the current datetime for the message creation.
 */
function getCurrentTimestamp() {
	return new Date();
}

/**
 * Renders a message on the chat screen based on the given arguments.
 * This is called from the `showUserMessage` and `showBotMessage`.
 */
function renderMessageToScreen(args) {
	// local variables
	let displayDate = (args.time || getCurrentTimestamp()).toLocaleString('en-IN', {
		month: 'short',
		day: 'numeric',
		hour: 'numeric',
		minute: 'numeric',
	});
	let messagesContainer = $('.messages');

	// init element
	let message = $(`
	<li class="message ${args.message_side}">
		<div class="avatar"></div>
		<div class="text_wrapper">
			<div class="text">${args.text}</div>
			<div class="timestamp">${displayDate}</div>
		</div>
	</li>
	`);

	// add to parent
	messagesContainer.append(message);

	// animations
	setTimeout(function () {
		message.addClass('appeared');
	}, 0);
	messagesContainer.animate({ scrollTop: messagesContainer.prop('scrollHeight') }, 300);
}

/**
 * Displays the user message on the chat screen. This is the right side message.
 */
function showUserMessage(message, datetime) {
	renderMessageToScreen({
		text: message,
		time: datetime,
		message_side: 'right',
	});
}

/**
 * Displays the chatbot message on the chat screen. This is the left side message.
 */
function showBotMessage(message, datetime) {
	// console.log(message);
	renderMessageToScreen({
		text: message,
		time: datetime,
		message_side: 'left',
	});
}

/**
 * Get input from user and show it on screen on button click.
 */
$('#send_button').on('click', function (e) {
	// get and show message and reset input
	input = $('#msg_input').val();
	showUserMessage(input);
	$('#msg_input').val('');
	$('#msg_input')[0].placeholder = "ChatBot is typing...";

	ws.send(input);


});

/**
* Execute above function when the user presses Enter key on the keyboard
*/
$('#msg_input').keypress(function(event) {
  // If the user presses the "Enter" key on the keyboard
  if (event.key === "Enter") {
    // Trigger the button element with a click
    $('#send_button').click();
  }
});

/**
 * Close websocket connection and show name div for new chat
*/
$('#close_button').on('click', function (e) {
	ws.close();
	$('#loading_div').hide();
	$('#msg_list').empty();
	$('#chat_div').hide();
	$('#name_div').show();
	$('#name_input').focus();

});


/**
 * Show name div, hide others and focus input.
 */
$(window).on('load', function () {
	$('#loading_div').hide();
	$('#chat_div').hide();
	$('#name_input').focus();
});
