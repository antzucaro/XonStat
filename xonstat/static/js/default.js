$(function(){

	init_menus();
	init_checkboxes();
	init_radiobuttons();
	init_datatables();

});

$.fn.hoverClass = function(c) {
    return this.each(function(){
        $(this).hover(
            function() { $(this).addClass(c);  },
            function() { $(this).removeClass(c); }
        );
    });
};

function init_menus() {
	$("#menu li").hover(
        function(){ $("ul", this).fadeIn("fast"); },
        function() { }
    );
    if (document.all) {
        $("#menu li").hoverClass("sfHover");
    }
}
function init_checkboxes() {
	$(".checkbox").change(function(){
		if($(this).is(":checked")){
			$(this).next("label").addClass("checkbox-selected");
		}else{
			$(this).next("label").removeClass("checkbox-selected");
		}
	});
}
function init_radiobuttons() {
	$(".radio").change(function(){
		if($(this).is(":checked")){
			$(".radio-selected:not(:checked)").removeClass("radio-selected");
			$(this).next("label").addClass("radio-selected");
		}
	});
}
function init_datatables() {
	/* lazy test to see if exists,
	 * setup proper routing in document ready */
	if ($("#sidebar table").length) {
		$("#sidebar table").dataTable({
			"bPaginate": false,
			"bLengthChange": false,
			"bFilter": false,
			"bSort": true,
			"bInfo": false,
			"bAutoWidth": false
		});
	}
	if ($("#recent-games").length) {
		$("#recent-games").dataTable({
			"bPaginate": false,
			"bLengthChange": false,
			"bFilter": true,
			"bSort": true,
			"bInfo": false,
			"bAutoWidth": false,
			"oLanguage": {
				"sSearch": "_INPUT_"
			},
			"aaSorting": [[ 0, "desc" ]]
		});
	}
	if ($("table.scoreboard").length) {
		$("table.scoreboard").dataTable({
			"bPaginate": false,
			"bLengthChange": false,
			"bFilter": false,
			"bSort": true,
			"bInfo": false,
			"bAutoWidth": false
		});
	}
	if ($("table.accuracy").length) {
		$("table.accuracy").dataTable({
			"bPaginate": false,
			"bLengthChange": false,
			"bFilter": false,
			"bSort": true,
			"bInfo": false,
			"bAutoWidth": false
		});
	}
	if ($(".recent_game_box").length) {
		$("").colorbox({width:"80%", height:"80%", iframe:true});
	}
	//$("#recent-games_filter input").attr("placeholder","filter names");
}
