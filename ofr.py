##############################################################################80
#                                                                              #
#                       Dipartimento Protezione Civile                         #
#                                                                              #
# (2020) Nicolo Fabbiane                                                       #
#                                                                              #
################################################################################


# data-set______________________________________________________________________

raw_data = {'path'    : 'data/opencovid19-fr',
            'git_url' : 'https://github.com/opencovid19-fr/data.git',
            'data_fmt': 'ofr'}


# figures_______________________________________________________________________

# dictionary of figures: the key is the figure name, while the value is the
# list of names of the selected regions. Set it to None for Italy.
figures = {#'Ile-de-France': ['Ile-de-France'],
           'France': ['France']}
