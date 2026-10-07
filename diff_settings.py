def apply(config, args):
    config["arch"] = "mipsel"
    config["baseimg"] = "extracted/SLUS_010.68"
    config["myimg"] = "build/SLUS_010.68"
    config["mapfile"] = "build/SLUS_010.68.map"
    config["source_directories"] = ["src"]
    config["objdump_executable"] = "mipsel-linux-gnu-objdump"
    config["make_command"] = ["make", "build"]
