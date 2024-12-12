A
${run(["echo", "Hello World"])}\
${run(["test", "-d", "${TMPDIR}"])}\
B
${run('echo "Hello World"', shell=True)}\
${run('test -d ${TMPDIR}', shell=True)}\
C
