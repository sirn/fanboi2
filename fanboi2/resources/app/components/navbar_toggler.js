/* Navbar toggler
 *
 * The toggle button to expand or hide board navigation menu. */

var toggler = document.getElementById('toggler');
var nav = document.getElementById('boards');
var menu = document.getElementById('toggler-menu');
var togglerItems = document.querySelectorAll('#toggler-menu > li');
var classNameRe = /(\s+)?\bactive\b(\s+)?/;

/* Enables the navbar and set height on click. We can't transition from
 * height: 0 to height: auto and animating max-height will make element
 * animate to and from max-height rather than just visible area and
 * creates few second of delay. */
window.addEventListener && toggler.addEventListener('click', function(e){
    e.preventDefault();

    if (classNameRe.test(nav.className)) {

        nav.className = nav.className.replace(classNameRe, "");
        menu.style.height = 0;

    } else {

        /* Calculate total height; since toggler-menu set its max-height
         * to 0, determining its height via menu.clientHeight will always
         * return 0. Done here instead of on intiailize to prevent height
         * miscalculation due to responsive layout changes. */
        var totalHeight = 0;

        for (var i = togglerItems.length - 1; i >= 0; i--) {
            totalHeight += togglerItems[i].clientHeight;
        }

        nav.className = 'active';
        menu.style.height = totalHeight + 'px';
    }
});
