// should be what server expecting
var input_name_app_var_id = 'app-var-id'
var input_name_request_type = 'request-type'
var input_name_request_value = 'request-value'
	
// dict entry info
var input_name_dict_ancestor_keys = 'dict-ancestor-keys'
var input_name_dict_entry_key = 'dict-entry-key'
var input_name_dict_entry_level = 'dict-entry-level'

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
	// add control scripts for all nested dicts (important for ajax response)
	var $dict_element = $element.find('.dict-entries')
	var $dict_controls = $('<div></div>').addClass('dict-controls').prependTo($dict_element)
	
	if (is_admin) {
		$('<button>Add Entry</button>')
			.prop('type', 'button')
			.addClass('add-dict-entry')
			.on('click', function() {
				var $form = toggle_form($(this))
				
				$form.find('[name="'+input_name_request_type+'"]')
							.prop('value', request_type_add_edit_entry)
				
				$form.find('[name="'+input_name_dict_entry_key+'"]')
							.prop('type','text')
			})
			.appendTo($dict_controls)
	
	}
	
	$('<button>Minimize</button>')
		.prop('type', 'button')
		.addClass('minimize-dict-level')
		.on('click', function() {
			$(this).parent().nextAll().slideToggle();
		})
		.appendTo($dict_controls)
}

function add_string_list_controls($element, is_admin=false) {
	if (is_admin) {
		var $elements = $element.find('.list-entries, :not(.list-entry) > .string-entry')
		var $controls = $('<span></span>').addClass('controls').insertAfter($elements)
		
		$('<button>Edit</button>')
			.prop('type', 'button')
			.addClass('edit-entry')
			.on('click', function() {
				var $form = toggle_form($(this))
				
				var existing_value
				var $entry = $(this).closest('.controls').prev()
				
				if ($entry.hasClass('string-entry')) {
					existing_value = '"'+$entry.text()+'"'
				}
				else if ($entry.hasClass('list-entries')) {
					existing_value = '['
					$entry.find('.string-entry').each(function() {
						existing_value += '"'+$(this).text()+'",'
					})
					existing_value = existing_value.substring(0, existing_value.length - 1)
					existing_value += ']'
				}
				
				$form.find('[name="'+input_name_request_value+'"]')
							.prop('value', existing_value)
				
				$form.find('[name="'+input_name_request_type+'"]')
							.prop('value', request_type_add_edit_entry)
			})
			.appendTo($controls)
	}
}

function toggle_form($button) {
	var $form = $button.siblings('form')
	
	if ($form.length) {
		$form.toggle()
	}
	else {
		$form = create_form()
		$form.prependTo($button.parent())
	}
	
	return $form
}

function create_form() {
	var $form = $('<form></form>')
	
	// dict entry information
	$('<input>').prop('name', input_name_dict_entry_key)
				.prop('type','hidden')
				.appendTo($form)
	
	$('<input>').prop('name', input_name_dict_ancestor_keys)
				.prop('type', 'hidden')
				.appendTo($form)
				
	$('<input>').prop('name', input_name_dict_entry_level)
				.prop('type', 'hidden')
				.appendTo($form)
	
	// basic information
	$('<input>').prop('name', input_name_app_var_id)
				.prop('type', 'hidden')
				.appendTo($form)
				
	$('<input>').prop('name', input_name_request_type)
				.prop('type', 'hidden')
				.appendTo($form)
				
	$('<input>').prop('name', input_name_request_value)
				.prop('type', 'text')
				.appendTo($form)
				
	$('<button>Submit</button>').prop('type', 'submit')
								.appendTo($form)
				
	$form.on('submit', function() {
		var $this = $(this)
		$this.find('input').removeClass('error-highlight')
		
		// doing this on submit to ensure correct values
		$this.find('[name="'+input_name_app_var_id+'"]')
				.prop('value', get_app_id($this))
				
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
				$this.toggle()
				
				var $data = $(data)
				
				if ( $this.parent().hasClass('dict-controls') ) {
					$this.closest('.dict-entries').children('.dict-entry:first').before($data)
				}
				else {
					$this.closest('.controls').prev().replaceWith($data)
				}
				
				add_dict_controls($data, true)
				add_string_list_controls($data, true)
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
	
	return $form
}