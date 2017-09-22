$(".hoverclick").unbind('click');
$(".hoverclick").unbind('mouseenter');
$(".hoverclick").click(function(){
	$(this).stop().fadeOut(10).fadeIn(500);
});

$(".hoverclick").mouseenter(function(){
	$(this).fadeOut(100);
    $(this).fadeIn(100);
},null);