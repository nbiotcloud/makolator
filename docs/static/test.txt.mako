<%def name="afunc(pos, opt=None)">\
output_filepath.name=${output_filepath.name}
output_tags=${" ".join(output_tags)}
pos=${pos}
% if opt:
options: ${opt}
% endif

</%def>
# ${makolator.info.genwarning}
# This file is updated by '${makolator.info.cli}'

Text
${afunc('abc')}
${afunc('def', opt=5)}
