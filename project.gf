struct Package {
    name : str,
    version : str,
    author : str, 
    main_file : str,
    jit : bool,
    modules : str
}

pub fix config = Package {
    name : "graff-app",
    version : "0.0.1",
    author : "Ben Promkaew",
    main_file : "main.gf",
    jit : true,
    modules : ["std::string", "std::file", "std::time", "std::sys"]
};