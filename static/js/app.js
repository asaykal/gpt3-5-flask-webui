    
    $(function() {
        $('#export-form').submit(function(event) {
            event.preventDefault();  
            $.get($(this).attr('action'), function(response) {
                var blob = new Blob([response], {type: 'text/csv'});
                var link = document.createElement('a');
                link.href = window.URL.createObjectURL(blob);
                link.download = 'history.csv';
                link.click();
            });
        });
    });
    $(function() {
      $('#upload_document-form').submit(function(event) {
          event.preventDefault();  
          var formData = new FormData(this);
          $.post('{{ url_for("upload_document") }}', formData, function(response) {
              if (response.status == 'success') {
                  $('#upload_message').text('Upload successful!');
              } else {
                  $('#upload_message').text('Upload failed.');
              }
          });
          return false; 
      });
  });

   


      