<%def name="afunc(pos, opt=None)">\
# This section is updated by '${makolator.info.cli}'

${output_filepath.name}
pos=${pos}
% if opt:
options: ${opt}
% endif

</%def>
