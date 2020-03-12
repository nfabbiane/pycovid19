##############################################################################80
#                                                                              #
#                       Dipartimento Protezione Civile                         #
#                                                                              #
# (2020) Nicolo Fabbiane                                                       #
#                                                                              #
################################################################################


# data-set______________________________________________________________________

raw_data = {'path'    : 'data/DPC',
            'git_url' : 'https://github.com/pcm-dpc/COVID-19',
            'data_fmt': 'dpc'}


# figures_______________________________________________________________________

# dictionary of figures: the key is the figure name, while the value is the
# list of names of the selected regions. Set it to None for Italy.
figures = {'Lombardia' : ['Lombardia'],
           'Veneto'    : ['Veneto'],
           'Emilia-Romagna': ['Emilia Romagna'],
           'Lazio'     : ['Lazio'],
           'Piemonte'  : ['Piemonte'],
           'Italia'    : None }
