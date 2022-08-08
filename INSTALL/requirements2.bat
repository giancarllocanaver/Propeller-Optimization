call conda config --append channels conda-forge
call conda activate tcc_giancarllo
call pip install -r pacotes.txt
call pre-commit install
call pre-commit autoupdate
call pause