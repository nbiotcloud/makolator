<% greet = "Hello" %>\
${greet} before
${staticcode('a', default='obsolete a')}
${greet} middle
  ${staticcode('b', comment_sep='#')}
${greet} after
