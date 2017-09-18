$(function () {
    $('#side-menu').metisMenu();
});

//Loads the correct sidebar on window load,
//collapses the sidebar on window resize.
// Sets the min-height of #page-wrapper to window size
$(function () {
    $(window).bind("load resize", function () {
        var topOffset = 50;
        var width = (this.window.innerWidth > 0) ? this.window.innerWidth : this.screen.width;
        if (width < 768) {
            $('div.navbar-collapse').addClass('collapse');
            topOffset = 100; // 2-row-menu
        } else {
            $('div.navbar-collapse').removeClass('collapse');
        }

        var height = ((this.window.innerHeight > 0) ? this.window.innerHeight : this.screen.height) - 1;
        height = height - topOffset;
        if (height < 1) height = 1;
        if (height > topOffset) {
            $("#page-wrapper").css("min-height", (height) + "px");
        }
    });
    var navAs = $('ul.nav a');
    var updateNav = function (e) {
        var url = window.location;
        // var element = $('ul.nav a').filter(function() {
        //     return this.href == url;
        // }).addClass('active').parent().parent().addClass('in').parent();
        navAs.each(function (index) {
            var element = $(this);
            element.removeClass('active');
            while (true) {
                if (element.is('li')) {
                    element = element.parent().removeClass('in').parent();
                } else {
                    break;
                }
            }
        });
        var activeElement = $('ul.nav a').filter(function () {
            return this.href == url;
        }).addClass('active').parent();
        while (true) {
            if (activeElement.is('li')) {
                activeElement = activeElement.parent().removeClass('in').parent();
            } else {
                break;
            }
        }
    };
    $(window).on('hashchange', function(e){
        updateNav();
    });
    updateNav();
});