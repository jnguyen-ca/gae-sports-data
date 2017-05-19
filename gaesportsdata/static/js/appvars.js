// should be what server expecting
var input_name_app_var_id = 'app-var-id'
var input_name_request_type = 'request-type'
var input_name_request_value = 'request-value'
	
var request_type_add_edit_entry = 'add-edit-entry'

function get_app_id($element) {
	return $element.closest('.app-var').find('.app-title .app-key').text()
}

function get_ancestor_keys($entry) {
	// recursive to get a nested entry's parents
	if ($entry.hasClass('dict-entry')) {$entry = $entry.parent();}
	
	var $parent_entry = $entry.closest('.dict-entry')
	if ($parent_entry.length < 1){
		return ''
	}
	else {
		return get_ancestor_keys($parent_entry)+'['+$parent_entry.children('.dict-key').text()+']'
	}
}

function add_dict_controls($element, is_admin=false) {
	// should be what server expecting
	var input_name_dict_ancestor_keys = 'dict-ancestor-keys'
	var input_name_dict_entry_key = 'dict-entry-key'
	var input_name_dict_entry_level = 'dict-entry-level'
	
	// add control scripts for all nested dicts (important for ajax response)
	var $dict_element = $element.find('.dict-entries')
	
	var $dict_controls = $('<div></div>').addClass('dict-controls').prependTo($dict_element)
	
	if (is_admin) {
		// only admin can ajax
		function reset_form($form) {
			$form.children(`[name="${input_name_dict_entry_key}"], 
						[name="${input_name_request_value}"],
						[type="submit"]`
				)
				.remove()
		}
		
		$('<button>Add Entry</button>').prop('type', 'button')
									.addClass('add-dict-entry')
									.on('click', function() {
										var $dict_form = $(this).siblings('form')
										
										if ($dict_form.children('[type="submit"]').length) {
											// toggle
											reset_form($dict_form)
											return false;
										}
										
										$dict_form.find('[name="'+input_name_request_type+'"]')
													.prop('value', request_type_add_edit_entry)
										
										$('<input>').prop('name', input_name_dict_entry_key)
													.prop('type','text')
													.appendTo($dict_form)
													
										$('<input>').prop('name', input_name_request_value)
													.prop('type', 'text')
													.appendTo($dict_form)
													
										$('<button>Submit</button>').prop('type', 'submit')
																	.appendTo($dict_form)
									})
									.appendTo($dict_controls)
	
		// base form
		var $dict_form = $('<form></form>')
		
		$('<input>').prop('name', input_name_app_var_id)
					.prop('type', 'hidden')
					.prop('value', get_app_id($dict_element))
					.appendTo($dict_form)
					
		$('<input>').prop('name', input_name_request_type)
					.prop('type', 'hidden')
					.appendTo($dict_form)
					
		$('<input>').prop('name', input_name_dict_ancestor_keys)
					.prop('type', 'hidden')
					.appendTo($dict_form)
					
		$('<input>').prop('name', input_name_dict_entry_level)
					.prop('type', 'hidden')
					.appendTo($dict_form)
		// end base form
					
		$dict_form.on('submit', function() {
			var $this = $(this)
			$this.find('input').removeClass('error-highlight')
			
			// doing this on submit to ensure correct values
			$this.find('[name="'+input_name_dict_ancestor_keys+'"]')
					.prop('value', get_ancestor_keys($this))
					
			$this.find('[name="'+input_name_dict_entry_level+'"]')
					.prop('value', $this.closest('.dict-entries')
										.children('.dict-level')
										.val()
					)
			
			$.ajax({
				url 	: window.location.pathname,
				type	: 'POST',
				data	: $(this).serialize(),
				success	: function(data, text, jqXHR) {
					reset_form($this)
					
					var $data = $(data)
					
					$this.closest('.dict-entries').children('.dict-entry:first').before($data)
					add_dict_controls($data, is_admin)
				},
				error: function(jqXHR, textStatus, errorThrown) {
					if (jqXHR.responseJSON) {
						console.log(jqXHR.responseJSON.message)
					}
					$this.find('input').addClass('error-highlight')
				}
			})
			return false
		});
					
		$dict_form.prependTo($dict_controls)
	}
	
	$('<button>Minimize</button>').prop('type', 'button')
									.addClass('minimize-dict-level')
									.on('click', function() {
										$(this).parent().nextAll().slideToggle();
									})
									.appendTo($dict_controls)
}