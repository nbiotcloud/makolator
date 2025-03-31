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
${lines | indent}
----
${lines | indent(2)}
----
${lines | indent(8)}
----
${lines | indent(8, rstrip=True)}
----
${lines | prefix("PRE")}
----
${lines | comment}
----
${lines | tex}
----
</%def>
${helpme()}
