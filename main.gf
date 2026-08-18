disp("==================================================");
disp("  Welcome to Graff Programming Language!");
disp("==================================================");

# Functions to_upper, now, platform are automatically pre-bound from project.gf!
let title = to_upper("graff jit engine v1.0");
disp(title);

let current_time = now();
disp("Current Timestamp:");
disp(current_time);

let host_os = platform();
disp("Host Platform:");
disp(host_os);

let result = (100 + 50) * 2;
disp("Native JIT Math Result:");
disp(result);
