##############################################################################80
# Environment
#
PY = python
PY_FLAGS =




################################################################################
# Definitions
#
name = visualize
data = 'dpc'

# library location______________________________________________________________
LIB = libpy


# Run___________________________________________________________________________
MAIN  = $(name).py
DATA  = data
FIGS  = figs




################################################################################
# Rules
#
default: $(name) clean-py
clean: clean-py clean-data
clean-all: clean clean-figs
all: default


# Python________________________________________________________________________
clean-py:
	@echo cleaning Python
	@rm -rf *~ *.pyc __pycache__ $(LIB)/*~  $(LIB)/*.pyc $(LIB)/__pycache__


# Run___________________________________________________________________________
$(name): $(MAIN)
	@echo running $(MAIN) with $(PY) with dataset $(data)
	@$(PY) $(PY_FLAGS) $(MAIN) $(data) #> /dev/null

# cleaning
clean-data:
	@echo cleaning data
	@rm -rf $(DATA)
clean-figs:
	@echo cleaning figures
	@rm -rf $(FIGS)
