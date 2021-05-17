import cx_Freeze

executables = [cx_Freeze.Executable("Py_Game.py")]
included_files = ['readme.txt','res/',('genomes/LIV/','genomes/LIV/'),'assets/']

cx_Freeze.setup(
    name="Pygame",
    options={"build_exe": {
                "packages":["pygame"],
                "include_files": included_files}
            },
    executables= executables
    )
