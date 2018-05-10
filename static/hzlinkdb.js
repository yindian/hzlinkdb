function add_del_btn() {
  var tbody = $(this).parentsUntil('table').get(-1);
  if (tbody.tagName != 'TBODY') {
    alert('Unexpected body tag ' + tbody.tagName);
    return;
  }
  var tr = $(this).parent().get(0);
  if (tr.tagName != 'TR') {
    alert('Unexpected row tag ' + tr.tagName);
    return;
  }
  if ($(tr).parent().get(0) != tbody) {
    alert('Unexpected parent ' + $(tr).parent().get(0).tagName);
    return;
  }
  var row = $(tbody).children().index(tr);
  if (row <= 0) {
    alert('Unexpected row index ' + row);
    return;
  }
  if ($(tr).children().index(this) != 0) {
    alert('Unexpected column index ' + $(tr).children().index(this));
    return;
  }
  var db = $(tbody).parent().children('caption').text();
  var keys;
  if (db == 'HZGraph') {
    keys = 1;
  } else if (db == 'HZMorph') {
    keys = 3;
  } else {
    alert('Unexpected caption ' + db);
    return;
  }
  var div = $(this).parentsUntil('.result').get(-1);
  var error = $(div).siblings('.error').children('pre').get(0);
  if (!error) {
    alert('Error div not found');
    return;
  }
  var head = $(tbody).children().first().children();
  var obj = {db: db};
  for (var i = 0; i < keys; i++) {
    obj[head[1 + i].innerHTML] = $(tr).children()[1 + i].innerHTML;
  }
  var btn = $('<button>-</button>');
  btn.click(function() {
    $.post('/del', obj, function(data) {
      if (data.error) {
        $(error).text(data.error);
      } else {
        $(error).empty();
        $(tr).remove();
      }
    }, 'json').fail(function(data) {
      $(error).text('Ajax failure: ' + data.status + ' ' + data.statusText);
    });
  });
  $(this).append(btn);
  $(tr).children().each(function(i) {
    if (i < 2) {
      return;
    }
    var field = head[i].innerHTML;
    var val = this.innerHTML;
    var me = this;
    $(this).click(function() {
      var input = window.prompt(field, val);
      if (input != null) {
        var d = $.extend({field: field, val: input}, obj);
        $.post('/upd8', d, function(data) {
          if (data.error) {
            $(error).text(data.error);
          } else {
            $(error).empty();
            $(me).empty();
            val = data.val;
            if (val != '') {
              $(me).text(val);
            }
            if (i <= keys) {
              obj[field] = val;
            }
          }
        }, 'json').fail(function(data) {
          $(error).text('Ajax failure: ' + data.status + ' ' + data.statusText);
        });
      } else {
        $(error).empty();
      }
    });
  });
}
$(window).on('load', function() {
  $('td.hz_del').each(add_del_btn);
  $('td.hz_add').each(function() {
    var tbody = $(this).parentsUntil('table').get(-1);
    if (tbody.tagName != 'TBODY') {
      alert('Unexpected body tag ' + tbody.tagName);
      return;
    }
    var tr = $(this).parent().get(0);
    if (tr.tagName != 'TR') {
      alert('Unexpected row tag ' + tr.tagName);
      return;
    }
    if ($(tr).parent().get(0) != tbody) {
      alert('Unexpected parent ' + $(tr).parent().get(0).tagName);
      return;
    }
    var row = $(tbody).children().index(tr);
    if ($(tr).children().index(this) != 0) {
      alert('Unexpected column index ' + $(tr).children().index(this));
      return;
    }
    var db = $(tbody).parent().children('caption').text();
    var keys;
    if (db == 'HZGraph') {
      keys = 1;
    } else if (db == 'HZMorph') {
      keys = 3;
    } else {
      alert('Unexpected caption ' + db);
      return;
    }
    var div = $(this).parentsUntil('.result').get(-1);
    var error = $(div).siblings('.error').children('pre').get(0);
    if (!error) {
      alert('Error div not found');
      return;
    }
    var code = $(div).siblings('.float_left').children('.code').get(0);
    if (!code) {
      alert('Code div not found');
      return;
    }
    var obj = {db: db, code: $(code).text()};
    var btn = $('<button>+</button>');
    btn.click(function() {
      $.post('/add', obj, function(data) {
        if (data.error) {
          $(error).text(data.error);
        } else {
          $(error).empty();
          if (row == 0) {
            var head = $('<tr><th></th></tr>');
            $.each(data.keys, function(i, v) {
              head.append($('<th>' + v + '</th>'));
            })
            $(tr).before(head);
          }
          row = $('<tr></tr>');
          var td = $('<td></td>').addClass('hz_del');
          row.append(td);
          $.each(data.values, function(i, v) {
            row.append($('<td>' + v + '</td>'));
          })
          $(tr).before(row);
          $(td).each(add_del_btn);
        }
      }, 'json').fail(function(data) {
        $(error).text('Ajax failure: ' + data.status + ' ' + data.statusText);
      });
    });
    $(this).append(btn);
  });
});
/* vim: set ts=2 sw=2 et tw=80 cc=80 : */
