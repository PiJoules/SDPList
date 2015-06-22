$("form.basic-info").submit(function(event){
    event.preventDefault(); // don't refresh page

    var inputs = $(this).serializeArray(); // for some reason, returns an array of objects

    // Convert the array of objects to a map
    var formObj = {};
    for (var i = 0; i < inputs.length; i++)
        var val = inputs[i].value;
        if (typeof val == "string")
            val = val.trim();

        if (val == "")
            alert("Do not leave any fields blank.");
            return;
        formObj[inputs[i].name] = val;

    if (formObj["firstName"].trim() !== "" && formObj["lastName"].trim() !== ""){
        $.post("/update_user", formObj, function(response){
            console.log(response);
            if (response !== "success"){
                showSuccess("Successfully updated information");
            }
            else {
                showError("An error occured on the server while updating information");
            }
        }).fail(function(jqXHR, textStatus, errorThrown){
            alert([textStatus, errorThrown]);
        });
    }
});