<%def name="helpme()">\
<% 
lines = """\
A
&
B
%
C
"""
%>\
----
${lines}
----
${lines | indent}
----
${lines | indent(2)}
----
${lines | indent(8)}
----
${lines | prefix("PRE")}
----
${lines | tex}
----
</%def>
${helpme()}