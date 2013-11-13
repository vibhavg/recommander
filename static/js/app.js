$(document).ready(function (){
    var $container = $('.movies');

    $('.movie').each(function(i) {
        $(this).data('name', $(this).find('h3').html().toLowerCase());
        $(this).data('rank', i);
    });

    $container.isotope({
        itemSelector: '.well',
        layoutMode: 'masonry',
        getSortData: {
            rank: function($elem) {
                return $elem.data('rank');
            },
            title: function($elem) {
                return $elem.data('name');
            },
            year: function($elem) {
                return Math.random();
            },
            rating: function($elem) {
                return Math.random();
            }
        }
    });

    $('#search-btn').click(function() {
        var text = $('#search-box').val().toLowerCase();
        $('.movie').each(function() {
            if ($(this).data('name').indexOf(text) > -1) {
                $(this).addClass('filter');
            } else {
                $(this).removeClass('filter');
            }
        });

        $container.isotope({filter: '.filter'});
    });

    $('#genre').change(function() {
        var genre = $(this).val();
        $('.movie').each(function() {
            if (!genre || Math.random() > 0.5) {
                $(this).addClass('filter');
            } else {
                $(this).removeClass('filter');
            }
        });

        $container.isotope({filter: '.filter'});
    });

    $('input[name=sort]').change(function() {
        $container.isotope({sortBy: $(this).val()});
    });
});
