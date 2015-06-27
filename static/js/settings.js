$("form.basic-info").submit(function(event){
	event.preventDefault(); // don't refresh page

	var inputs = $(this).serializeArray(); // for some reason, returns an array of objects

    // Convert the array of objects to a map
	var formObj = {};
	for (var i = 0; i < inputs.length; i++)
		formObj[inputs[i].name] = inputs[i].value;

    if (formObj["firstName"].trim() !== "" && formObj["lastName"].trim() !== ""){
        $.post("/update_user", formObj, function(response){
            console.log(response);
            showSuccess("Successfully updated information");
        }).fail(function(jqXHR, textStatus, errorThrown){
            alert([textStatus, errorThrown]);
        });
    }
});