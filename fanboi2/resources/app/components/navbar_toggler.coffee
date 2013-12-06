# Navbar toggler
# The toggle button to expand or hide board navigation menu.

$toggler = $('#toggler')
$nav = $('#boards')
$menu = $('#toggler-menu')
$menuItems = $menu.find('> li')

# Enable the navbar and set height on click. Animation is done using specific
# height to prevent slight delay in transition animation when max-height is
# used for transition (e.g. transition from max-height: 0 to max-height: 1000
# will transition to max-height rather than actual height.)
$toggler.on 'click', (e) ->
    e.preventDefault()

    if $nav.hasClass 'active'
        $nav.removeClass 'active'
        $menu.css 'height', 0

    # Since #toggler-menu set its max-height to 0, using $menu.height will
    # always return 0. We need to calculate the height of each element
    # individually. Calculation is done here to prevent height miscalculation
    # due to layout changes.
    else
        totalHeight = 0
        for menuItem in $menuItems
            totalHeight += menuItem.clientHeight
        $nav.addClass 'active'
        $menu.css 'height', "#{totalHeight}px"
