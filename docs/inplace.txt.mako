<%def name="afunc(pos, opt=None)">\
# This section is updated by '${makolator.info.cli}'

output_filepath.name=${output_filepath.name}
output_tags=${" ".join(output_tags)}
pos=${pos}
% if opt:
options: ${opt}
% endif

</%def>
