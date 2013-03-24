domready(function(){
  var toggler = document.getElementById('toggler');
  var header = document.getElementById('header');
  var menu = document.getElementById('toggler-menu');
  var togglerItems = document.querySelectorAll('#toggler-menu > li');

  /* Enables the navbar and set height on click. This is because we can't
   * transition from height: 0 to height: auto and using max-height instead
   * will make element animate to max-height rather than just visible area.
   * This cause the detoggle animation to delay by few milliseconds (since
   * it animates back from the non-visible area). */
  toggler.addEventListener('click', function(e){
    e.preventDefault();

    if (header.classList.contains('active')) {

      header.classList.remove('active');
      menu.style.height = 0;

    } else {

      /* Calculate total height; since toggler-menu set its max-height to 0,
       * determining its height via menu.clientHeight will always return 0.
       * Done here instead of on intiailize to prevent height miscalculation
       * due to responsive layout changes. */
      var totalHeight = 0;
      for (var i = togglerItems.length - 1; i >= 0; i--) {
        totalHeight += togglerItems[i].clientHeight;
      }

      header.classList.add('active');
      menu.style.height = totalHeight + 'px';

    }
  });
});
