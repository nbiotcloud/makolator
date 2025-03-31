A
${run(["echo", "HelloWorld"])}\
${run(["test", "-d", "${TMPDIR}"])}
B
${run('echo HelloWorld', shell=True)}\
${run('test -d ${TMPDIR}', shell=True)}
C
