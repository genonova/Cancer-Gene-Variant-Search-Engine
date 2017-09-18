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
    var updateNav = function () {
        var url = window.location;
        // var element = $('ul.nav a').filter(function() {
        //     return this.href == url;
        // }).addClass('active').parent().parent().addClass('in').parent();
        for (var i = 0; i < navAs.length; i++) {
            var element = navAs[i];
            element.removeClass('active');
            while (true) {
                if (element.is('li')) {
                    element = element.parent().removeClass('in').parent();
                } else {
                    break;
                }
            }
        }
        alert('asd');
        var activeElement = $('ul.nav a').filter(function () {
            return this.href === url;
        }).addClass('active').parent();
        while (true) {
            if (activeElement.is('li')) {
                activeElement = activeElement.parent().removeClass('in').parent();
            } else {
                break;
            }
        }
    };
    navAs.addEventListener('click', function (e) {
        updateNav();
    });
    updateNav();
});
