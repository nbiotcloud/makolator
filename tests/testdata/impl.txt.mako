<%inherit file="base.txt.mako"/>

<%block name="main">\
${impl(1)}
${impl(2, b=3)}
${self.basefunc(4, c=5)}
</%block>

<%def name="impl(*args, **kwargs)">
impl
  args: ${args}
  kwargs: ${kwargs}
</%def>
