##############################################################################80
#                                                                              #
#                           John Hopkins University                            #
#                                                                              #
# (2020) Nicolo Fabbiane                                                       #
#                                                                              #
################################################################################


# data-set______________________________________________________________________

raw_data = {'path'    : 'data/JHU',
            'git_url' : 'https://github.com/CSSEGISandData/COVID-19.git',
            'data_fmt': 'jhu'}


# figures_______________________________________________________________________

# dictionary of figures: the key is the figure name, while the value is the
# list of names of the selected regions. Set it to None for the World.
figures = {'Italy' : ['Italy'],
           'France': ['France'],
           'Europe': ['Austria', 'Belgium', 'Bulgaria', 'Croatia', 'Cyprus',
                      'Czech Republic', 'Denmark', 'Estonia', 'Finland',
                      'France', 'Germany', 'Greece', 'Hungary', 'Ireland',
                      'Italy', 'Latvia', 'Lithuania', 'Luxembourg', 'Malta',
                      'Netherlands', 'Poland', 'Portugal', 'Romania', 'Slovakia',
                      'Slovenia', 'Spain', 'Sweden',
                      'Switzerland', 'Norway', 'UK'],
           'China' : ['Mainland China'],
           'World' : None }
