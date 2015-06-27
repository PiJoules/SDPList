$("form.basic-info").submit(function(event){
    event.preventDefault(); // don't refresh page

    var inputs = $(this).serializeArray(); // for some reason, returns an array of objects

    // Convert the array of objects to a map
    var formObj = {};
    for (var i = 0; i < inputs.length; i++){
        var val = inputs[i].value;
        if (typeof val == "string")
            val = val.trim();

        if (val == ""){
            alert("Do not leave any fields blank.");
            return;
        }
        formObj[inputs[i].name] = val;
    }
    console.log(formObj);

    $.post("/add_project", formObj, function(response){
        if (response === "success"){
            showSuccess("Successfully updated information");
        }
        else {
            showError(response);
        }
    }).fail(function(jqXHR, textStatus, errorThrown){
        alert([textStatus, errorThrown]);
    });
});