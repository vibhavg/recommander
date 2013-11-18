$(document).ready(function (){
    var $container = $('.movies');

    $('.movie').each(function(i) {
        $(this).data('name', $(this).find('h3').html().toLowerCase());
        $(this).data('rank', i);
        $(this).data('year', $(this).attr('year'));
        $(this).data('rating',$(this).attr('rating'));
        $(this).data('genres', JSON.parse($(this).attr('genres')));
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
                return $elem.data('year');
            },
            rating: function($elem) {
                return 7 - $elem.attr('rating');
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
            if (!genre || $(this).data('genres').indexOf(genre) > -1) {
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

    $('select').select2({width: 150});
    
    $('.navbar-brand').click(function() {
        $('input[value=rating]').click();
        $('select').select2('val', '');
        $container.isotope({sortBy: '', filter: ''});
    });

    $('.movie').popover({trigger: 'hover'})
});
