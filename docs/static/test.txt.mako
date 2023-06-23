<%def name="afunc(pos, opt=None)">\
${output_filepath.name}
pos=${pos}
% if opt:
options: ${opt}
% endif

</%def>
Text
${afunc('abc')}
${afunc('def', opt=5)}
