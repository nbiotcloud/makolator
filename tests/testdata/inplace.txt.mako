<%def name="afunc(pos, opt=None)">\
${makolator.info.inplacewarning}
${output_filepath.name}
${output_tags}
pos=${pos}
% if opt:
options: ${opt}
% endif

</%def>

<%def name="simple(pos, opt=None)">\
${output_filepath.name}
pos=${pos}
% if opt:
options: ${opt}
% endif

</%def>
