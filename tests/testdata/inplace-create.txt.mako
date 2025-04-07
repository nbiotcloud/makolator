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


<%def name="create_inplace()">\
-- GENERATE INPLACE BEGIN afunc("foo2")
created
-- GENERATE INPLACE END afunc

-- GENERATE INPLACE BEGIN afunc("foo3")
-- GENERATE INPLACE END afunc
</%def>
