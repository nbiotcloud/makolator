Hello World

-- GENERATE INPLACE BEGIN simple("foo")
inplace.cpp // GENERATED
pos=foo     // GENERATED
            // GENERATED
-- GENERATE INPLACE END simple
in between
        // GENERATE INPLACE BEGIN simple("foo", "bar")
        inplace.cpp  // GENERATED
        pos=foo      // GENERATED
        options: bar // GENERATED
                     // GENERATED
        // GENERATE INPLACE END simple

    in between

    GENERATE INPLACE BEGIN simple("foo", opt="sally")
    inplace.cpp    // GENERATED
    pos=foo        // GENERATED
    options: sally // GENERATED
                   // GENERATED
    GENERATE INPLACE END simple

Hello Mars
