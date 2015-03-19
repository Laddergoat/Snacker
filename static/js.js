/**
 * Created by Andy on 19/03/2015.
 */

$( document ).ready(function() {
    $('#imgUpload').click(function(){ $('#imgHide').trigger('click'); });


    $("#imgHide").change(function(){
        alert("This input field has lost its focus.");
    });
});
