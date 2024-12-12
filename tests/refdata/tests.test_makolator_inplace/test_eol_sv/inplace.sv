Hello World

-- GENERATE INPLACE BEGIN simple("foo")
inplace.sv // GENERATED
pos=foo    // GENERATED
           // GENERATED
-- GENERATE INPLACE END simple
in between
        // GENERATE INPLACE BEGIN simple("foo", "bar")
        inplace.sv   // GENERATED
        pos=foo      // GENERATED
        options: bar // GENERATED
                     // GENERATED
        // GENERATE INPLACE END simple

    in between

    GENERATE INPLACE BEGIN simple("foo", opt="sally")
    inplace.sv     // GENERATED
    pos=foo        // GENERATED
    options: sally // GENERATED
                   // GENERATED
    GENERATE INPLACE END simple

Hello Mars
