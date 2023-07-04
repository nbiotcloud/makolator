<%!
from pathlib import Path
%>
${output_filepath.name}
${datamodel}
before
<%
makolator.gen(Path("sub.txt.mako"), output_filepath.with_name("sub1.txt"), context={'sub': 'sub-var1'})
makolator.gen(Path("sub.txt.mako"), output_filepath.with_name("sub2.txt"), context={'sub': 'sub-var2'})

with makolator.open_outputfile(output_filepath.with_name("inplace.txt")) as file:
    file.write("""
-- foo0
GENERATE INPLACE BEGIN afunc('abc')
obsolete
GENERATE INPLACE END afunc
-- foo1
GENERATE INPLACE BEGIN afunc('def')
obsolete
GENERATE INPLACE END afunc
-- foo2
""")

makolator.inplace(Path("inplace.txt.mako"), output_filepath.with_name("inplace.txt"))
%>
after
