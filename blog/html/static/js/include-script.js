 document.write('\
  <!-- Scripts in: ./static/js/-->\
  <!-- jQuery Version 3.1.1 -->\
  <script src="/static/js/jquery-3.1.1.js" type="text/javascript">\
  </script>\
  <!-- Bootstrap Core JavaScript -->\
  <script src="/static/js/bootstrap.js" type="text/javascript">\
  </script>\
  <!-- The rest of the JS -->\
  <script src="/static/js/navigation.js" type="text/javascript">\
  </script>\
  <!-- Docs JS -->\
  <script src="/static/js/docs.js" type="text/javascript">\
  </script>\
  <!-- Popovers -->\
  <script src="/static/js/webui-popover.js" type="text/javascript">\
  </script>\
  <!-- Javascript for page -->\
  <script type="text/javascript">\
   // Change character image on refresh\
      // Add file names and captions to doc-characters.json\
    $.getJSON("/static/js/doc-characters.json", function(data) {\
      var item = data.images[Math.floor(Math.random()*data.images.length)];\
      $('<img src="/static/js/../images/superuser-img/' + item.image + '">').appendTo('#superuser-img');\
      $('<p>' + item.caption + '<strong>Xiao5tech docs</strong></p>').appendTo('#superuser-img');\
    });\
  </script>\
');