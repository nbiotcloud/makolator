<%def name="example(greet='Hello')">\
${greet} before

${staticcode('a', default='obsolete a')}

${greet} middle

${staticcode('b')}

${greet} after

</%def>
${example()}
