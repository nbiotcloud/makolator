<%def name="example(greet='Hello')">\
output_tags=${" ".join(output_tags)}
${greet} before

${staticcode('a', default='obsolete a')}

${greet} middle

${staticcode('b')}

${greet} after

</%def>
${example()}
