function showSuccess(successContent) {
	$(".alerts .alert-success").html("<strong>" + (successContent || "Success") + "</strong>");
	$(".alerts .alert-success").append('<button type="button" class="close" onclick="$(\'.alert-success\').hide()"><span aria-hidden="true">&times;</span></button>').show();
}

function showError(errorContent) {
	$(".alerts .alert-danger").html("<strong>" + (errorContent || "Error") + "</strong>");
	$(".alerts .alert-danger").append('<button type="button" class="close" onclick="$(\'.alert-danger\').hide()"><span aria-hidden="true">&times;</span></button>').show();
}