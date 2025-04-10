<%def name="afunc(pos, opt=None)">\
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
manually maintained code goes here
this is just the default
-- GENERATE INPLACE BEGIN afunc("foo3")
-- GENERATE INPLACE END afunc
</%def>
