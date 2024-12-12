<%def name="main()">\
<% greet = "Hello" %>\
${output_tags}
${greet} before
${staticcode('a', default='obsolete a')}
${greet} middle
${staticcode('b')}
${greet} after
</%def>
${main()}
