$(function() {
    $("#autosearch").autocomplete({
          source: function( request, response ) {
              var terms = request.term.split(" ");
              var q = "*";
              for (index = 0; index < terms.length; ++index) {
                  q = q + terms[index] + "* AND label:*";
              }
              q = q.slice(0, -12)
              $.ajax({
              url: "/solr/roman_consuls/select",
              data: {
                  q: "label:"+q+" AND year:[-30 TO *]",
                  fl: "label,godot_uri",
                  wt: 'json',
                  rows: 20
               },
               dataType: "jsonp",
               jsonp: 'json.wrf',
               success: function( data ) {
                  response($.map(data.response.docs, function( item ) {
                      return {
                          label: item.label,
                          value: item.label + " | " + item.godot_uri,
                      };
                  }));
              }
            });
           },
           minLength: 2
      });
});