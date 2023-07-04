<%def name="afunc(pos, opt=None)">\
${makolator.info.inplacewarning}
${output_filepath.name}
pos=${pos}
% if opt:
options: ${opt}
% endif

</%def>
