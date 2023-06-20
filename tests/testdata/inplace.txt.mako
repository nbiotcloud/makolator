<%def name="afunc(pos, opt=None)">\
${output_filepath.name}
pos=${pos}
% if opt:
options: ${opt}
% endif

</%def>

<%def name="brokenfunc()">\
${4 / 0}
</%def>
