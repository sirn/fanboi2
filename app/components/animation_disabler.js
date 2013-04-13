/* Animation Disabler
 *
 * Remove the animation disabler CSS class on initial page load, a workaround
 * to prevent "flash animation" due to responsive media query. See also
 * layout.styl for CSS disabler. */

setTimeout(function(){
    var body = document.getElementsByTagName('body')[0];
    body.className = '';
}, 1000);
