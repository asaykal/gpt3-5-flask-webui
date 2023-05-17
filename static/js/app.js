    
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
            $.ajax({
                type: 'POST',
                url: 'http://127.0.0.1:5000/upload_document',
                data: formData,
                contentType: false,
                processData: false,
                success: function(response) {
                    if (response.status === 'success') {
                        $('#loaded-document').text(response.document);
                        $('#upload_message').text('Upload successful!');
                    } else {
                        $('#upload_message').text('Upload failed.');
                    }
                },
                error: function() {
                    $('#upload_message').text('Upload failed.');
                }
            });
            return false;
        });
    });
        
   


      