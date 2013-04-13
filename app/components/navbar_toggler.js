/* Navbar toggler
 *
 * The toggle button to expand or hide top left navigation menu button on
 * responsive mobile layout. See also layout.styl for CSS animation. */

var toggler = document.getElementById('toggler');
var header = document.getElementById('header');
var menu = document.getElementById('toggler-menu');
var togglerItems = document.querySelectorAll('#toggler-menu > li');
var classNameRe = /(\s+)?\bactive\b(\s+)?/;

/* Enables the navbar and set height on click. We can't transition from
 * height: 0 to height: auto and animating max-height will make element
 * animate to and from max-height rather than just visible area and
 * creates few second of delay. */
window.addEventListener && toggler.addEventListener('click', function(e){
    e.preventDefault();

    if (classNameRe.test(header.className)) {

        header.className = header.className.replace(classNameRe, "");
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

        header.className = 'active';
        menu.style.height = totalHeight + 'px';
    }
});
